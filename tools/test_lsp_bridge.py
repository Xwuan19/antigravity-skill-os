#!/usr/bin/env python3
"""Kiểm tra lsp_bridge.py bằng một language server giả.

Không cần gopls/pyright: mock nói đúng giao thức LSP (framing Content-Length),
trả lời cố định, để kiểm phần dễ sai nhất — bắc cầu hai loại framing khác nhau
(MCP một dòng \\n  ↔  LSP Content-Length).

    python3 tools/test_lsp_bridge.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIDGE = ROOT / "tools" / "lsp_bridge.py"

MOCK = r'''
import json, sys

def read():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.decode().strip()
        if not line:
            break
        k, v = line.split(":", 1)
        headers[k.strip().lower()] = v.strip()
    n = int(headers["content-length"])
    return json.loads(sys.stdin.buffer.read(n))

def write(o):
    d = json.dumps(o).encode()
    sys.stdout.buffer.write(b"Content-Length: %d\r\n\r\n" % len(d) + d)
    sys.stdout.buffer.flush()

while True:
    m = read()
    if m is None:
        break
    meth, rid = m.get("method"), m.get("id")
    if meth == "initialize":
        write({"jsonrpc":"2.0","id":rid,"result":{"capabilities":{
            "definitionProvider":True,"referencesProvider":True,
            "hoverProvider":True,"documentSymbolProvider":True,
            "workspaceSymbolProvider":True}}})
    elif meth == "textDocument/definition":
        write({"jsonrpc":"2.0","id":rid,"result":[
            {"uri":"file:///ws/src/target.py","range":{
                "start":{"line":9,"character":4},"end":{"line":9,"character":20}}}]})
    elif meth == "textDocument/references":
        write({"jsonrpc":"2.0","id":rid,"result":[
            {"uri":"file:///ws/src/a.py","range":{"start":{"line":1,"character":0},
             "end":{"line":1,"character":5}}},
            {"uri":"file:///ws/src/b.py","range":{"start":{"line":3,"character":2},
             "end":{"line":3,"character":7}}}]})
    elif meth == "textDocument/hover":
        write({"jsonrpc":"2.0","id":rid,"result":{"contents":{
            "kind":"markdown","value":"```python\\ndef run(x: int) -> str\\n```"}}})
    elif meth == "textDocument/documentSymbol":
        write({"jsonrpc":"2.0","id":rid,"result":[
            {"name":"Runner","kind":5,"range":{"start":{"line":0,"character":0},
             "end":{"line":30,"character":0}},
             "selectionRange":{"start":{"line":0,"character":6},
             "end":{"line":0,"character":12}},
             "children":[{"name":"run","kind":6,
               "range":{"start":{"line":5,"character":4},"end":{"line":9,"character":0}},
               "selectionRange":{"start":{"line":5,"character":8},
               "end":{"line":5,"character":11}}}]}]})
    elif meth == "workspace/symbol":
        write({"jsonrpc":"2.0","id":rid,"result":[
            {"name":"Runner","kind":5,"location":{"uri":"file:///ws/src/r.py",
             "range":{"start":{"line":0,"character":0},"end":{"line":0,"character":6}}}}]})
    elif rid is not None:
        write({"jsonrpc":"2.0","id":rid,"result":None})
'''


def mcp_session(bridge_cmd: list[str], root: str) -> list[dict]:
    """Chạy bridge như Antigravity sẽ chạy, gửi MCP request, thu response."""
    p = subprocess.Popen(bridge_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, bufsize=1, cwd=root)
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "lsp_definition",
                    "arguments": {"file": "src/a.py", "line": 3, "column": 5}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "lsp_references",
                    "arguments": {"file": "src/a.py", "line": 3, "column": 5}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "lsp_hover",
                    "arguments": {"file": "src/a.py", "line": 3, "column": 5}}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
         "params": {"name": "lsp_document_symbols",
                    "arguments": {"file": "src/a.py"}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
         "params": {"name": "lsp_workspace_symbols", "arguments": {"query": "Run"}}},
    ]
    for r in reqs:
        p.stdin.write(json.dumps(r) + "\n")
    p.stdin.flush()

    out, err = [], []
    t = threading.Thread(target=lambda: err.append(p.stderr.read()), daemon=True)
    t.start()
    while len(out) < 7:
        line = p.stdout.readline()
        if not line:
            break
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    p.stdin.close()
    try:
        p.wait(timeout=8)
    except subprocess.TimeoutExpired:
        p.kill()
    return out


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    mock = tmp / "mock_lsp.py"
    mock.write_text(MOCK, encoding="utf-8")
    (tmp / "src").mkdir()
    (tmp / "src" / "a.py").write_text("def run(x):\n    return str(x)\n", encoding="utf-8")

    cmd = [sys.executable, str(BRIDGE), "--command", sys.executable,
           "--root", str(tmp), "--", str(mock)]
    res = mcp_session(cmd, str(tmp))

    checks: list[tuple[str, bool]] = []
    by_id = {r.get("id"): r for r in res}

    init = by_id.get(1, {}).get("result", {})
    checks.append(("initialize trả capabilities.tools",
                   "tools" in (init.get("capabilities") or {})))

    tools = by_id.get(2, {}).get("result", {}).get("tools", [])
    checks.append(("tools/list có 5 tool", len(tools) == 5))

    def text(i: int) -> str:
        try:
            return by_id[i]["result"]["content"][0]["text"]
        except Exception:
            return ""

    d = text(3)
    checks.append(("lsp_definition trả đúng vị trí", "target.py:10:5" in d))
    r = text(4)
    checks.append(("lsp_references đếm đúng 2", "2 reference" in r))
    h = text(5)
    checks.append(("lsp_hover trả type signature", "def run(x: int) -> str" in h))
    s = text(6)
    checks.append(("document_symbols có cây lồng", "Runner" in s and "  run" in s))
    w = text(7)
    checks.append(("workspace_symbols trả kết quả", "Runner" in w))

    # Hồi quy 1: server args bắt đầu bằng "--" (--stdio, --api-version...)
    # phải được chuyển tiếp, không bị argparse của bridge nuốt.
    cmd2 = [sys.executable, str(BRIDGE), "--command", sys.executable,
            "--root", str(tmp), "--", str(mock), "--stdio"]
    res2 = mcp_session(cmd2, str(tmp))
    init2 = next((r for r in res2 if r.get("id") == 1), {}).get("result", {})
    checks.append(("chuyển tiếp được tham số '--stdio'",
                   "tools" in (init2.get("capabilities") or {})))

    # Hồi quy 2: thiếu language server → MCP vẫn sống, trả lỗi đọc được
    cmd3 = [sys.executable, str(BRIDGE), "--command", "khong_ton_tai_xyz",
            "--root", str(tmp)]
    res3 = mcp_session(cmd3, str(tmp))
    by3 = {r.get("id"): r for r in res3}
    e3 = (by3.get(3, {}).get("result", {}).get("content") or [{}])[0].get("text", "")
    checks.append(("thiếu server → báo lỗi rõ ràng",
                   "khong_ton_tai_xyz" in e3 and "tìm thấy" in e3.lower()))

    print()
    ok = True
    for name, passed in checks:
        print(f"  {'✓' if passed else '✗'} {name}")
        ok = ok and passed
    print(f"\n  {sum(1 for _, p in checks if p)}/{len(checks)} pass\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
