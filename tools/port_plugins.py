#!/usr/bin/env python3
"""Chuyển plugin Claude Code sang plugin Antigravity.

Khác biệt phải xử lý:

| Claude Code                     | Antigravity                          |
|---------------------------------|--------------------------------------|
| `.claude-plugin/plugin.json`    | `plugin.json` ở gốc plugin            |
| `commands/<x>.md` (slash cmd)   | skill `<x>/SKILL.md` — Antigravity tự sinh `/x` từ tên skill |
| `` !`git status` ``             | không có inline exec → đổi thành chỉ dẫn chạy lệnh |
| `allowed-tools: Bash(git add:*)`| không có pattern scope → bỏ, ghi chú  |
| `hooks/hooks.json` + `hooks` key| `hooks.json` dạng `{tên: {enabled, Event: [...]}}` |
| `${CLAUDE_PLUGIN_ROOT}`         | `${PLUGIN_ROOT}`                      |
| `UserPromptSubmit`              | `PreInvocation` (gần nhất)            |
| `Notification`, `SubagentStop`  | không có → bỏ                         |

    python3 tools/port_plugins.py --list
    python3 tools/port_plugins.py --all
    python3 tools/port_plugins.py --only commit-commands
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
REGISTRY = ROOT / "registry" / "plugins.json"
VENDOR = ROOT / "vendor" / "claude"
OUT = ROOT / "plugins"

# Claude tool -> Antigravity tool (None = không có tương đương)
TOOL_MAP = {
    "Read": "view_file", "Write": "write_to_file", "Edit": "replace_file_content",
    "MultiEdit": "multi_replace_file_content", "Bash": "run_command",
    "BashOutput": None, "KillShell": None, "Glob": "find_by_name",
    "Grep": "grep_search", "LS": "list_dir", "WebSearch": "search_web",
    "WebFetch": "read_url_content", "Task": "invoke_subagent",
    "NotebookRead": None, "NotebookEdit": None, "TodoWrite": None,
    "SlashCommand": None, "ExitPlanMode": None,
}
MODEL_MAP = {"haiku": "flash", "sonnet": "pro", "opus": "pro"}

# event Claude -> Antigravity
EVENT_MAP = {
    "SessionStart": "SessionStart",
    "PreToolUse": "PreToolUse",
    "PostToolUse": "PostToolUse",
    "UserPromptSubmit": "PreInvocation",
    "Stop": "Stop",
}
EVENT_DROP = {"Notification", "SubagentStop", "PreCompact", "SessionEnd"}

INLINE_EXEC = re.compile(r"!`([^`]+)`")


def parse_fm(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4:].lstrip("\n")
    fm: dict = {}
    key = None
    for line in raw.splitlines():
        if re.match(r"^[\w-]+:", line):
            k, v = line.split(":", 1)
            key, fm[k.strip()] = k.strip(), v.strip()
        elif key and line.startswith("  "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm, body


def yaml_str(s: str) -> str:
    s = " ".join(str(s).split())
    return json.dumps(s, ensure_ascii=False) if any(c in s for c in ':#"\'') else s


# ---------------------------------------------------------------- commands

def command_to_skill(name: str, text: str) -> tuple[str, list[str]]:
    fm, body = parse_fm(text)
    desc = " ".join(str(fm.get("description", f"/{name}")).split())
    notes: list[str] = []

    if fm.get("allowed-tools"):
        notes.append(
            "> Bản gốc giới hạn tool (`allowed-tools`). Antigravity không có pattern "
            "scope theo lệnh nên giới hạn đó bị bỏ — chỉ dẫn bên dưới thay thế.")
    if fm.get("argument-hint"):
        notes.append(f"> Tham số: `{fm['argument-hint']}`")

    # !`cmd` -> hướng dẫn chạy lệnh rồi đọc output
    cmds = INLINE_EXEC.findall(body)
    if cmds:
        gathered = "\n".join(f"- `{c}`" for c in cmds)
        # thay bằng đúng lệnh, để phần Context vẫn đọc hiểu được
        body = INLINE_EXEC.sub(lambda m: f"(output của `{m.group(1)}`)", body)
        notes.append(
            "## Dữ liệu cần thu thập\n\n"
            "Trước khi làm, chạy các lệnh sau và đọc output thật của chúng:\n\n"
            f"{gathered}")

    hdr = [f"---", f"name: {name}", f"description: {yaml_str(desc)}", "---", ""]
    out = "\n".join(hdr) + "\n"
    if notes:
        out += "\n\n".join(notes) + "\n\n"
    out += body
    return out, notes


# ------------------------------------------------------------------ agents

def agent_to_antigravity(name: str, text: str, *, strict_tools: bool) -> str:
    fm, body = parse_fm(text)
    desc = " ".join(str(fm.get("description", "")).split())
    claude_tools = [t.strip() for t in str(fm.get("tools", "")).split(",") if t.strip()]
    mapped = [TOOL_MAP[t] for t in claude_tools if TOOL_MAP.get(t)]
    unknown = [t for t in claude_tools if t not in TOOL_MAP]
    model = MODEL_MAP.get(str(fm.get("model", "")).lower(), "inherit")

    out = ["---", f"name: {name}", f"description: {yaml_str(desc)}"]
    if strict_tools and mapped:
        out += ["tools:"] + [f"  - {t}" for t in dict.fromkeys(mapped)]
    out += ["subagent: true", "mainAgent: false", f"model: {model}",
            "commandExecutionPolicy: sandbox", "---", ""]
    note = ["Ported từ plugin Claude Code. `tools` để trống có chủ ý — tên tool không"]
    note.append("hợp lệ làm Antigravity treo subagent, nên agent thừa hưởng toolset parent.")
    if unknown:
        note.append(f"Đã bỏ tool không tương đương: {', '.join(unknown)}.")
    return "\n".join(out) + "\n> " + " ".join(note) + "\n\n" + body


# ------------------------------------------------------------------- hooks

def convert_hooks(src: Path) -> tuple[dict | None, list[str]]:
    if not src.is_file():
        return None, []
    try:
        raw = json.loads(src.read_text(encoding="utf-8"))
    except Exception as e:
        return None, [f"hooks.json không đọc được: {e}"]
    hooks = raw.get("hooks") if isinstance(raw.get("hooks"), dict) else raw
    if not isinstance(hooks, dict):
        return None, ["hooks.json không đúng dạng"]

    out: dict = {}
    dropped: list[str] = []
    for event, entries in hooks.items():
        if event in EVENT_DROP:
            dropped.append(event)
            continue
        target = EVENT_MAP.get(event)
        if not target:
            dropped.append(event)
            continue
        fixed = []
        for entry in entries if isinstance(entries, list) else []:
            e = json.loads(json.dumps(entry))
            for h in e.get("hooks", []):
                if "command" in h:
                    h["command"] = (h["command"]
                                    .replace("${CLAUDE_PLUGIN_ROOT}", "${PLUGIN_ROOT}")
                                    .replace("$CLAUDE_PLUGIN_ROOT", "${PLUGIN_ROOT}"))
            fixed.append(e)
        if fixed:
            out.setdefault(target, []).extend(fixed)

    if not out:
        return None, dropped
    return {"converted": {"enabled": False, "note": "Bật bằng enabled:true sau khi kiểm script",
                          **out}}, dropped


# ------------------------------------------------------------------ convert

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
        "\n".join(paths) + "\n", encoding="utf-8")
    if ref:
        subprocess.run(["git", "-C", str(d), "fetch", "--depth", "1", "--quiet",
                        "origin", ref], capture_output=True)
        subprocess.run(["git", "-C", str(d), "checkout", "--quiet", ref],
                       capture_output=True)
    else:
        subprocess.run(["git", "-C", str(d), "checkout", "--quiet"], capture_output=True)
    return d


def convert_plugin(entry: dict, src: Path, *, strict_tools: bool) -> dict:
    name = entry["id"]
    dest = OUT / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    report = {"id": name, "skills": [], "agents": [], "hooks": None, "warnings": []}

    # plugin.json
    desc = entry.get("description") or f"Ported from {entry['repo']}"
    (dest / "plugin.json").write_text(json.dumps({
        "$schema": "https://antigravity.google/schemas/v1/plugin.json",
        "name": name,
        "description": " ".join(desc.split())[:120],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # skills có sẵn
    if (src / "skills").is_dir():
        for d in (src / "skills").iterdir():
            if d.is_dir() and (d / "SKILL.md").is_file():
                shutil.copytree(d, dest / "skills" / d.name)
                report["skills"].append(d.name)

    # commands -> skills
    if (src / "commands").is_dir():
        for f in sorted((src / "commands").glob("*.md")):
            body, notes = command_to_skill(f.stem, f.read_text(encoding="utf-8"))
            tgt = dest / "skills" / f.stem
            tgt.mkdir(parents=True, exist_ok=True)
            (tgt / "SKILL.md").write_text(body, encoding="utf-8")
            report["skills"].append(f.stem)
            if any("allowed-tools" in n for n in notes):
                report["warnings"].append(f"{f.stem}: bỏ allowed-tools")

    # agents
    if (src / "agents").is_dir():
        for f in sorted((src / "agents").glob("*.md")):
            text = agent_to_antigravity(f.stem, f.read_text(encoding="utf-8"),
                                        strict_tools=strict_tools)
            (dest / "agents").mkdir(exist_ok=True)
            (dest / "agents" / f"{f.stem}.md").write_text(text, encoding="utf-8")
            report["agents"].append(f.stem)

    # hooks
    hk, dropped = convert_hooks(src / "hooks" / "hooks.json")
    if hk:
        (dest / "hooks.json").write_text(
            json.dumps(hk, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["hooks"] = "converted"
        (dest / "hooks").mkdir(exist_ok=True)
        for f in (src / "hooks").glob("*"):
            if f.is_file() and f.name != "hooks.json":
                shutil.copy2(f, dest / "hooks" / f.name)
    if dropped:
        report["warnings"].append("hook event không có tương đương, đã bỏ: "
                                  + ", ".join(sorted(set(dropped))))

    # license + nguồn
    for lic in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        if (src / lic).is_file():
            shutil.copy2(src / lic, dest / lic)
            break
    (dest / "SOURCE.md").write_text(
        f"# {name}\n\nNguồn: `{entry['repo']}`"
        f"{(' @ `' + entry['ref'] + '`') if entry.get('ref') else ''}"
        f"\nLicense: {entry.get('license')}\nĐường dẫn gốc: `{entry['path']}`\n\n"
        f"Chuyển đổi tự động bởi `tools/port_plugins.py`. Xem đầu file đó để biết "
        f"bảng ánh xạ command→skill, tool, hook event.\n", encoding="utf-8")

    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tools", choices=["omit", "strict"], default="omit")
    a = ap.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))["plugins"]

    if a.list:
        for p in reg:
            print(f"  {p['id']:<24} {p['license']:<12} {p['origin']:<28} {p['path']}")
        print(f"\n  {len(reg)} plugin\n")
        return

    sel = [p for p in reg if a.all or p["id"] == a.only]
    if not sel:
        ap.print_help()
        return

    by_repo: dict[tuple[str, str], list[dict]] = {}
    for p in sel:
        by_repo.setdefault((p["repo"], p.get("ref") or ""), []).append(p)

    reports = []
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for (repo, ref), group in by_repo.items():
            print(f"\n  {repo} @ {ref[:10] or 'HEAD'}")
            src = fetch(repo, ref, sorted({p["path"] for p in group}), tmp)
            if src is None:
                continue
            for p in group:
                pdir = src / p["path"]
                if not pdir.is_dir():
                    print(f"    ✗ {p['id']}: không thấy {p['path']}")
                    continue
                if p.get("vendor", True):
                    vdest = VENDOR / p["id"]
                    if vdest.exists():
                        shutil.rmtree(vdest)
                    shutil.copytree(pdir, vdest)
                rep = convert_plugin(p, pdir, strict_tools=a.tools == "strict")
                reports.append(rep)
                print(f"    ✓ {rep['id']:<22} skill {len(rep['skills'])} "
                      f"agent {len(rep['agents'])} hook {rep['hooks'] or '—'}")

    OUT.mkdir(exist_ok=True)
    (OUT / "PORTED.json").write_text(
        json.dumps({"generated": "auto", "plugins": reports}, indent=2,
                   ensure_ascii=False) + "\n", encoding="utf-8")
    warn = sum(len(r["warnings"]) for r in reports)
    print(f"\n  {len(reports)} plugin → {OUT}  ({warn} cảnh báo)\n")


if __name__ == "__main__":
    sys.exit(main())
