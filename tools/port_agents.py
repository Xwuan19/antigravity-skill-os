#!/usr/bin/env python3
"""Port subagent từ hệ Claude Code sang định dạng Antigravity.

Claude Code:  tools: Read, Write, Edit, Bash, Glob, Grep   model: sonnet
Antigravity:  tools: [view_file, run_command, ...]          model: pro

Antigravity docs cảnh báo: *"Specifying an unmapped or misspelled tool name in
the `tools` list may cause the subagent process to hang during execution."*
Nên mặc định script **không ghi `tools`** — subagent thừa hưởng toolset của
parent. Chỉ ghi khi bạn dùng `--tools strict` và tự chịu rủi ro.

    python3 tools/port_agents.py --list
    python3 tools/port_agents.py --all
    python3 tools/port_agents.py --group code --tools strict
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_JSON = ROOT / "registry" / "agents.json"
OUT = ROOT / "agents"

# Claude Code tool  ->  Antigravity tool
# Chỉ những cặp chắc chắn tương đương. Không map được thì loại khỏi danh sách.
TOOL_MAP = {
    "Read": "view_file",
    "Write": "write_to_file",
    "Edit": "replace_file_content",
    "MultiEdit": "multi_replace_file_content",
    "Bash": "run_command",
    "Glob": "find_by_name",
    "Grep": "grep_search",
    "LS": "list_dir",
    "WebSearch": "search_web",
    "WebFetch": "read_url_content",
    "Task": "invoke_subagent",
    "NotebookEdit": None,   # không có tương đương
    "TodoWrite": None,      # không có tương đương
    "SlashCommand": None,
}

# Claude tier -> Antigravity tier (inherit | flash | pro)
MODEL_MAP = {"haiku": "flash", "sonnet": "pro", "opus": "pro"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    fm: dict = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        fm[k.strip()] = v
    return fm, body


def yaml_str(s: str) -> str:
    s = " ".join(str(s).split())
    return json.dumps(s, ensure_ascii=False) if any(c in s for c in ':#"\'') else s


def convert(fm: dict, body: str, *, model_mode: str, tools_mode: str,
            group: str) -> str:
    name = fm.get("name", "unknown").strip()
    desc = " ".join(fm.get("description", "").split())

    claude_tools = [t.strip() for t in str(fm.get("tools", "")).split(",") if t.strip()]
    mapped, unmapped = [], []
    for t in claude_tools:
        if t in TOOL_MAP and TOOL_MAP[t]:
            mapped.append(TOOL_MAP[t])
        elif t not in TOOL_MAP:
            unmapped.append(t)

    raw_model = str(fm.get("model", "inherit")).lower()
    model = "inherit" if model_mode == "inherit" else MODEL_MAP.get(raw_model, "pro")

    fm_out = [
        "---",
        f"name: {name}",
        f"description: {yaml_str(desc)}",
    ]
    if tools_mode == "strict" and mapped:
        fm_out.append("tools:")
        fm_out += [f"  - {t}" for t in dict.fromkeys(mapped)]
    fm_out += [
        "subagent: true",
        "mainAgent: false",
        f"model: {model}",
        "commandExecutionPolicy: sandbox",
        f"# ported-from: claude-code/{group}",
    ]
    if unmapped:
        fm_out.append(f"# tools không có tương đương, đã bỏ: {', '.join(unmapped)}")
    fm_out.append("---")

    note = []
    if tools_mode != "strict":
        note.append(
            "> Ported agent. `tools` để trống có chủ ý — Antigravity treo subagent "
            "nếu gặp tên tool không hợp lệ, nên agent thừa hưởng toolset của parent.")
    if unmapped:
        note.append(f"> Đã bỏ tool không tương đương: {', '.join(unmapped)}.")
    header = "\n".join(note)

    return "\n".join(fm_out) + "\n\n" + (header + "\n\n" if header else "") + body


def fetch(repo: str, ref: str | None, paths: list[str], tmp: Path) -> Path | None:
    d = tmp / repo.replace("/", "__")
    r = subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout",
                        "--quiet", f"https://github.com/{repo}.git", str(d)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ✗ clone {repo}: {r.stderr.strip()[:120]}")
        return None
    subprocess.run(["git", "-C", str(d), "sparse-checkout", "init", "--no-cone"])
    (d / ".git" / "info" / "sparse-checkout").write_text(
        "\n".join(paths + ["LICENSE", "LICENSE.md"]) + "\n", encoding="utf-8")
    if ref:
        subprocess.run(["git", "-C", str(d), "fetch", "--depth", "1", "--quiet",
                        "origin", ref], capture_output=True)
        subprocess.run(["git", "-C", str(d), "checkout", "--quiet", ref],
                       capture_output=True)
    else:
        subprocess.run(["git", "-C", str(d), "checkout", "--quiet"],
                       capture_output=True)
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--group")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tools", choices=["omit", "strict"], default="omit")
    ap.add_argument("--model", choices=["map", "inherit"], default="map")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    cfg = json.loads(AGENTS_JSON.read_text(encoding="utf-8"))
    entries = cfg["agents"]

    if a.list:
        groups: dict[str, list[str]] = {}
        for e in entries:
            groups.setdefault(e["group"], []).append(e["id"])
        for g, ids in groups.items():
            print(f"\n  {g} ({len(ids)})")
            print("    " + ", ".join(ids))
        print(f"\n  tổng {len(entries)}\n")
        return

    if not (a.all or a.group):
        ap.print_help()
        return

    sel = [e for e in entries if a.all or e["group"] == a.group]
    if not sel:
        sys.exit(f"  Không có agent nào trong group '{a.group}'")

    out_root = Path(a.out)
    by_repo: dict[tuple[str, str], list[dict]] = {}
    for e in sel:
        by_repo.setdefault((e["repo"], e.get("ref") or ""), []).append(e)

    n_ok = 0
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for (repo, ref), group in by_repo.items():
            print(f"\n  {repo} @ {ref[:10] or 'HEAD'}  ({len(group)} agent)")
            src = fetch(repo, ref, sorted({e["path"] for e in group}), tmp)
            if src is None:
                continue
            for e in group:
                f = src / e["path"]
                if not f.is_file():
                    print(f"    ✗ {e['id']}: không thấy {e['path']}")
                    continue
                fm, body = parse_frontmatter(f.read_text(encoding="utf-8"))
                out = convert(fm, body, model_mode=a.model, tools_mode=a.tools,
                               group=e["group"])
                dest_dir = out_root / e["group"]
                dest_dir.mkdir(parents=True, exist_ok=True)
                (dest_dir / f"{e['id']}.md").write_text(out, encoding="utf-8")
                print(f"    ✓ {e['id']:<32} {e['group']}")
                n_ok += 1

    print(f"\n  {n_ok} agent → {out_root}")
    print(f"  cài bằng: python3 tools/install.py --agents --profile <id> -w <ws>\n")


if __name__ == "__main__":
    main()
