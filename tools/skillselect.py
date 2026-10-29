#!/usr/bin/env python3
"""Một chỗ duy nhất quyết định skill nào vào workspace nào.

Trước đây `install.py` và `route.py` mỗi bên có một bản `select()` riêng và chúng đã
lệch nhau (max_skills được một bên tôn trọng, bên kia bỏ qua). Gom về đây.

Bốn trục lọc: domain → artifact → families → stack.

`stack` là trục theo ngôn ngữ, để skill Python không lọt vào project TypeScript:

    skill:  stack = ["python"]        → chỉ project có Python
    skill:  stack = ["typescript"]    → chỉ project có TS/JS
    skill:  stack = ["general"]       → mọi project
    skill:  không khai stack          → mọi project (tương thích cũ)
"""
from __future__ import annotations

import os
from pathlib import Path

# đuôi file → tên stack. Khớp với tên dùng trong registry.
EXT_STACK = {
    ".py": "python", ".pyi": "python",
    ".ts": "typescript", ".tsx": "typescript", ".js": "typescript",
    ".jsx": "typescript", ".mjs": "typescript", ".cjs": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin", ".kts": "kotlin",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".lua": "lua",
    ".c": "cpp", ".cc": "cpp", ".cpp": "cpp", ".h": "cpp", ".hpp": "cpp",
    ".sql": "sql",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".ps1": "shell",
}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    "target", ".next", ".nuxt", ".svelte-kit", "vendor", "Pods", ".gradle", ".idea",
    ".vscode", "coverage", ".pytest_cache", ".ruff_cache", ".mypy_cache", "out", "obj",
    ".terraform", ".cache", "bower_components", ".dart_tool",
}
MAX_FILES = 3000


def detect_stacks(ws: Path) -> list[str]:
    """Đoán stack của workspace bằng cách đếm đuôi file. Trả [] nếu không thấy gì."""
    ws = Path(ws)
    if not ws.is_dir():
        return []
    seen: dict[str, int] = {}
    n = 0
    for dirpath, dirnames, filenames in os.walk(ws):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            n += 1
            st = EXT_STACK.get(Path(f).suffix.lower())
            if st:
                seen[st] = seen.get(st, 0) + 1
        if n > MAX_FILES:
            break
    # từ 2 file trở lên mới tính, để một file lẻ không kéo cả bộ skill vào
    return [k for k, v in sorted(seen.items(), key=lambda kv: -kv[1]) if v >= 2]


def select(skills: list[dict], prof: dict, include_manual: bool = False,
           stacks: list[str] | None = None) -> list[dict]:
    """Skill được cài vào workspace này. `stacks=None` → không lọc theo stack."""
    want_dom = set(prof["select"].get("domain", []))
    want_art = set(prof["select"].get("artifact", []))
    forbid = set(prof.get("forbid_domains", []))
    want_fam = set(prof.get("families", []))
    want_stk = set(stacks) if stacks is not None else None

    out = []
    for s in skills:
        if s["mode"] == "system":
            continue
        if s["mode"] == "manual" and not include_manual:
            continue

        dom = set(s["domain"])
        art = set(s["artifact"]) or {"*"}
        fam = set(s.get("families", []))
        stk = set(s.get("stack", []))

        # họ: skill khai families thì phải khớp họ của profile
        if fam and want_fam and not (fam & want_fam):
            continue
        if dom & forbid:
            continue
        if not ("*" in dom or dom & want_dom):
            continue
        if not ("*" in art or art & want_art):
            continue

        # stack: "general" luôn qua; skill không khai stack cũng qua
        if stk and want_stk and "general" not in stk and not (stk & want_stk):
            continue

        out.append(s)

    return sorted(out, key=lambda s: (s["pack"], s["id"]))


def explain(s: dict, prof: dict, stacks: list[str] | None) -> str:
    """Vì sao skill bị loại — dùng cho `route.py` khi cần giải thích."""
    want_dom = set(prof["select"].get("domain", []))
    want_art = set(prof["select"].get("artifact", []))
    forbid = set(prof.get("forbid_domains", []))
    want_fam = set(prof.get("families", []))
    want_stk = set(stacks) if stacks is not None else None

    if s["mode"] == "system":
        return "rule hệ thống"
    if s["mode"] == "manual":
        return "mode=manual (cần --include-manual)"
    if set(s["domain"]) & forbid:
        return "domain bị cấm: " + ", ".join(sorted(set(s["domain"]) & forbid))
    if not (set(s["domain"]) & want_dom):
        return "domain: " + "/".join(s["domain"])
    art = set(s["artifact"]) or {"*"}
    if not ("*" in art or art & want_art):
        return "artifact: " + "/".join(sorted(art))
    fam = set(s.get("families", []))
    if fam and want_fam and not (fam & want_fam):
        return "families: " + "/".join(sorted(fam))
    stk = set(s.get("stack", []))
    if stk and want_stk and "general" not in stk and not (stk & want_stk):
        return "stack: " + "/".join(sorted(stk))
    return "khác"
