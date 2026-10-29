#!/usr/bin/env python3
"""Tầng code intelligence cho Antigravity: nối LSP vào MCP.

Antigravity nói MCP. Language server nói LSP. tools/lsp_bridge.py làm cầu.
Module này quét workspace, thấy ngôn ngữ nào thì đăng ký server đó.

    python3 tools/lsp.py --check              # máy đã cài language server nào
    python3 tools/lsp.py -w . --scan          # xem sẽ đăng ký gì
    python3 tools/lsp.py -w .                 # ghi .agents/mcp_config.json
    python3 tools/lsp.py -w . --langs go,rust # ép đăng ký, bỏ qua quét
    python3 tools/lsp.py -w . --global        # ghi ~/.gemini/config/mcp_config.json

Chỉ dùng stdlib. Không chép bridge vào workspace khi gọi từ install.py
(install.py tự chép).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LSP_JSON = ROOT / "registry" / "lsp.json"
BRIDGE = ROOT / "tools" / "lsp_bridge.py"
GLOBAL_CFG = Path.home() / ".gemini" / "config" / "mcp_config.json"

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    "target", ".next", ".nuxt", ".svelte-kit", "vendor", "Pods", ".gradle",
    ".idea", ".vscode", "coverage", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    "out", "obj", ".terraform", ".cache", "bower_components", ".dart_tool",
}
MAX_FILES = 4000
MIN_FILES = 2


def servers() -> dict:
    return json.loads(LSP_JSON.read_text(encoding="utf-8"))["servers"]


def scan(ws: Path) -> Counter:
    """Đếm file theo ngôn ngữ. Bỏ thư mục phụ thuộc/build."""
    ext_to_lang = {e: lang for lang, s in servers().items() for e in s["ext"]}
    counts: Counter = Counter()
    seen = 0
    for dirpath, dirnames, filenames in os.walk(ws):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            seen += 1
            lang = ext_to_lang.get(Path(f).suffix.lower())
            if lang:
                counts[lang] += 1
        if seen > MAX_FILES:
            break
    return counts


def build_config(bridge: str, langs: list[str], ws) -> dict:
    srv = servers()
    out = {}
    for lang in langs:
        s = srv[lang]
        args = [bridge, "--command", s["command"], "--root", str(ws)]
        if s["args"]:
            # sau "--": argparse của bridge không nuốt --stdio nữa
            args += ["--", *s["args"]]
        out[s["mcp_name"]] = {"command": "python3", "args": args}
    return {"mcpServers": out}


def available(langs: list[str]) -> tuple[list[str], list[str]]:
    srv = servers()
    ok = [l for l in langs if shutil.which(srv[l]["command"])]
    return ok, [l for l in langs if l not in ok]


def install(ws: Path, langs: list[str] | None = None, *, bridge: str | None = None,
            global_: bool = False, dry: bool = False, force: bool = False,
            copy_bridge: bool = False, quiet: bool = False) -> dict:
    """Ghi mcp_config.json. Trả {'written', 'servers', 'skipped', 'missing'}."""
    def say(*a):
        if not quiet:
            print(*a)

    ws = ws.resolve()
    srv = servers()

    if langs is None:
        counts = scan(ws)
        langs = [l for l, c in counts.most_common() if c >= MIN_FILES]
        if not quiet and counts:
            say(f"\n  Quét {ws}")
            for l, c in counts.most_common():
                mark = "✓" if shutil.which(srv[l]["command"]) else "✗ chưa cài"
                flag = "" if c >= MIN_FILES else "  (dưới ngưỡng)"
                say(f"    {l:<14} {c:>5} file  {mark}{flag}")

    langs = [l for l in langs if l in srv]
    ok, missing = available(langs)

    result = {"written": None, "servers": [], "detected": list(langs),
              "missing": missing}
    for l in missing:
        say(f"    ! {l}: chưa cài — {srv[l]['install']}")

    if not ok:
        if langs or missing:
            say("    Không language server nào dùng được. Chưa ghi gì.")
        return result

    # Global: bridge nằm trong ~/.gemini. Workspace: nằm trong <ws>/.agents
    # để workspace tự chứa, repo xoá vẫn chạy.
    if bridge is None:
        bridge_path = (GLOBAL_CFG.parent / "lsp" / "lsp_bridge.py" if global_
                       else ws / ".agents" / "lsp" / "lsp_bridge.py")
        if copy_bridge and not dry:
            bridge_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(BRIDGE, bridge_path)
            bridge_path.chmod(0o755)
        bridge = str(bridge_path)

    # global: root để "." — bridge giải theo cwd lúc Antigravity khởi động,
    # nên một config dùng được cho mọi workspace
    cfg = build_config(bridge, ok, "." if global_ else ws)
    target = GLOBAL_CFG if global_ else ws / ".agents" / "mcp_config.json"

    # giữ server của người dùng, chỉ thêm/cập nhật cái của mình
    if target.is_file():
        try:
            old = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            old = {}
        if old.get("mcpServers") and not force:
            old.setdefault("mcpServers", {}).update(cfg["mcpServers"])
            cfg = old
        elif not force:
            cfg = old | {"mcpServers": {**old.get("mcpServers", {}),
                                        **cfg["mcpServers"]}}

    result["servers"] = list(cfg["mcpServers"])
    if dry:
        say(f"    · sẽ ghi {target}  ({len(ok)} server: {', '.join(ok)})")
        return result

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    result["written"] = str(target)
    say(f"    ✓ {target}  →  {', '.join(cfg['mcpServers'])}")
    return result


def remove(ws: Path, *, global_: bool = False, dry: bool = False) -> int:
    """Gỡ các server lsp-* và thư mục .agents/lsp/. Giữ server của người dùng."""
    target = GLOBAL_CFG if global_ else ws.resolve() / ".agents" / "mcp_config.json"
    n = 0
    if target.is_file():
        try:
            cfg = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
        keep = {k: v for k, v in (cfg.get("mcpServers") or {}).items()
                if not k.startswith("lsp-")}
        n = len(cfg.get("mcpServers") or {}) - len(keep)
        if n:
            cfg["mcpServers"] = keep
            if not dry:
                target.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
            print(f"    - {n} server lsp-* khỏi {target}")
    bridge_dir = ws.resolve() / ".agents" / "lsp"
    if bridge_dir.is_dir():
        print(f"    - {bridge_dir}")
        if not dry:
            shutil.rmtree(bridge_dir)
        n += 1
    return n


def do_check() -> None:
    srv = servers()
    print(f"\n  {'ngôn ngữ':<14}{'lệnh':<26}trạng thái")
    print(f"  {'-'*14}{'-'*26}{'-'*22}")
    have = 0
    for lang, s in srv.items():
        ok = shutil.which(s["command"])
        have += bool(ok)
        print(f"  {lang:<14}{s['command']:<26}"
              f"{'✓ có' if ok else '✗ thiếu — ' + s['install']}")
    print(f"\n  {have}/{len(srv)} language server đã cài.\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Nối LSP vào Antigravity qua MCP")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--check", action="store_true", help="kiểm language server đã cài")
    ap.add_argument("--scan", action="store_true", help="chỉ in, không ghi file")
    ap.add_argument("--langs", help="ép đăng ký, ví dụ: go,python,rust (hoặc 'all')")
    ap.add_argument("--global", dest="global_", action="store_true",
                    help="ghi ~/.gemini/config/mcp_config.json thay vì trong workspace")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="ghi đè mcp_config.json")
    ap.add_argument("--remove", action="store_true", help="gỡ các server lsp-*")
    a = ap.parse_args()

    if a.check:
        do_check()
        return

    if a.remove:
        ws0 = Path(a.workspace).expanduser()
        print(f"\n  Gỡ LSP khỏi {ws0}")
        n = remove(ws0, global_=a.global_, dry=a.dry_run)
        print(f"\n  {'Sẽ gỡ' if a.dry_run else 'Đã gỡ'} {n} mục.\n")
        return

    ws = Path(a.workspace).expanduser()
    if not ws.is_dir():
        sys.exit(f"  Không phải thư mục: {ws}")

    langs = None
    if a.langs:
        langs = list(servers()) if a.langs.strip() == "all" else \
            [x.strip() for x in a.langs.split(",") if x.strip()]
        bad = [x for x in langs if x not in servers()]
        if bad:
            sys.exit(f"  Không hỗ trợ: {', '.join(bad)}. Có: {', '.join(servers())}")

    print()
    r = install(ws, langs, dry=a.scan or a.dry_run, force=a.force,
                copy_bridge=True, global_=a.global_)
    if r["written"]:
        print("\n  Khởi động lại Antigravity để nạp MCP server.")
        print("  Thử: \"dùng lsp_definition tìm chỗ khai báo hàm X\"\n")
    elif not r["detected"]:
        print("  Không thấy ngôn ngữ nào khớp 12 server đã hỗ trợ.")
        print("  Xem `python3 tools/lsp.py --check` hoặc ép bằng --langs.\n")
    elif a.scan or a.dry_run:
        print("  (chưa ghi — bỏ --scan/--dry-run để ghi thật)\n")
    else:
        print()


if __name__ == "__main__":
    main()
