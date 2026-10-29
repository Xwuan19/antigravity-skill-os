#!/usr/bin/env python3
"""PreToolUse — chặn lệnh shell nguy hiểm. MẶC ĐỊNH TẮT.

Bật bằng "enabled": true. Trả JSON {"decision": "deny"|"allow", "reason": ...}.
Chặn theo mẫu chứ không phân tích cú pháp — đây là lưới an toàn, không phải sandbox.
"""
from __future__ import annotations

import json
import re
import sys

DENY = [
    (r"rm\s+-rf?\s+/(\s|$)", "xoá toàn bộ filesystem"),
    (r"rm\s+-rf?\s+~(\s|$)", "xoá toàn bộ home"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"mkfs\.", "format ổ đĩa"),
    (r"dd\s+if=.*of=/dev/[sh]d", "ghi thô lên ổ đĩa"),
    (r">\s*/dev/[sh]d", "ghi thô lên ổ đĩa"),
    (r"chmod\s+-R\s+777\s+/(\s|$)", "mở quyền toàn hệ thống"),
    (r"git\s+push\s+.*--force.*\s+(main|master)\b", "force-push lên nhánh chính"),
    (r"curl[^|]*\|\s*(ba)?sh", "pipe script từ internet vào shell"),
]


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        cmd = ((payload.get("toolCall") or {}).get("args") or {}).get("CommandLine", "")
        for pat, why in DENY:
            if re.search(pat, cmd, re.IGNORECASE):
                print(json.dumps({"decision": "deny",
                                  "reason": f"Skill OS safety gate: {why}"}))
                return
        print(json.dumps({"decision": "allow"}))
    except Exception:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
