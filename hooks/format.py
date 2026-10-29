#!/usr/bin/env python3
"""PostToolUse — chạy formatter sau khi ghi file. MẶC ĐỊNH TẮT.

Bật trong .agents/hooks.json bằng "enabled": true. Hook này không sửa file,
chỉ chạy formatter của project nếu tìm thấy; không tìm thấy thì im lặng.

Antigravity gửi stdin JSON, trong đó toolCall.args chứa đường dẫn file.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

# (tên chương trình, có cần package.json không, args)
FORMATTERS = [
    ("prettier", True, ["--write"]),
    ("ruff", False, ["format"]),
    ("gofmt", False, ["-w"]),
    ("rustfmt", False, []),
]


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        args = (payload.get("toolCall") or {}).get("args") or {}
        target = args.get("TargetFile")
        if not target:
            return
        p = Path(target)
        if not p.is_file():
            return
        root = Path(payload.get("workspacePaths", ["."])[0])
        for name, needs_node, extra in FORMATTERS:
            if not shutil.which(name):
                continue
            if needs_node and not (root / "package.json").is_file():
                continue
            if name == "prettier" and p.suffix not in {".js", ".jsx", ".ts", ".tsx",
                                                       ".css", ".json", ".md", ".html"}:
                continue
            if name == "ruff" and p.suffix != ".py":
                continue
            if name == "gofmt" and p.suffix != ".go":
                continue
            if name == "rustfmt" and p.suffix != ".rs":
                continue
            subprocess.run([name, *extra, str(p)], capture_output=True, timeout=25)
            return
    except Exception:
        pass


if __name__ == "__main__":
    main()
