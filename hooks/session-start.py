#!/usr/bin/env python3
"""SessionStart hook — nhắc lại luật hệ thống trước lượt gọi model đầu tiên.

Vì sao cần: rules `always_on` có ngân sách 20.000 token; vượt trần thì Antigravity
thay file lớn nhất bằng một dòng trỏ, và luật biến mất mà không báo. Hook này là
lưới an toàn thứ hai, chỉ ~120 token.

Đọc stdin JSON (không dùng), ghi stdout JSON `injectSteps`. Không bao giờ crash:
hook lỗi sẽ làm hỏng phiên, nên mọi lỗi đều được nuốt và trả về object rỗng.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REMINDER = (
    "Skill OS active. Ponytail FULL is locked: smallest artifact that fully solves "
    "the task, no unrequested abstractions, never cut validation at trust boundaries, "
    "security, accessibility, or anything the user asked for. There is no lite/ultra/off "
    "mode and no /ponytail command — do not offer one. Before answering, scan the loaded "
    "skills and follow any that match. Reply to the user in Vietnamese; keep code, "
    "comments and commit messages in English. Verify before claiming done."
)


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # nếu workspace tắt bằng biến môi trường thì im lặng
    if os.environ.get("SKILL_OS_QUIET") == "1":
        print("{}")
        return

    try:
        ctx = []
        for p in payload.get("workspacePaths") or []:
            p = Path(p)
            if (p / ".agents" / "skill-os.json").is_file():
                ctx.append(f"workspace {p.name} đã cấu hình profile")
        msg = REMINDER + ((" (" + "; ".join(ctx) + ")") if ctx else "")
        print(json.dumps({"injectSteps": [{"systemMessage": {"systemMessage": msg}}]}))
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
