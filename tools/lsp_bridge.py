#!/usr/bin/env python3
"""LSP → MCP bridge. Cho Antigravity code intelligence của bất kỳ ngôn ngữ nào.

Antigravity nói MCP; language server nói LSP. Hai giao thức khác nhau ở **framing**:

    MCP stdio : JSON một dòng, phân cách bằng \\n
    LSP       : "Content-Length: N\\r\\n\\r\\n" + N byte JSON

Cầu này chạy như một MCP server (stdio), và bên trong giữ một language server
(stdio, framing Content-Length).

    python3 tools/lsp_bridge.py --command gopls --root .

Chỉ dùng stdlib. Không phụ thuộc npm/cargo/pip.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote, unquote

DEBUG = os.environ.get("LSP_BRIDGE_DEBUG") == "1"


def log(*a) -> None:
    if DEBUG:
        print("[lsp-bridge]", *a, file=sys.stderr, flush=True)


# ------------------------------------------------------------------ framing

class LspClient:
    """Nói LSP với language server qua stdio."""

    def __init__(self, command: list[str], cwd: str):
        self.error: str | None = None
        self.command = command
        try:
            self.proc = subprocess.Popen(
                command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, bufsize=0)
        except FileNotFoundError:
            self.proc = None
            self.error = (f"Không tìm thấy language server `{command[0]}` trên PATH. "
                          f"Cài rồi thử lại; xem hướng dẫn bằng "
                          f"`python3 tools/lsp.py --check`.")
            return
        except Exception as e:
            self.proc = None
            self.error = f"Không khởi động được `{command[0]}`: {e}"
            return
        self._id = 0
        self._lock = threading.Lock()
        self._pending: dict[int, dict] = {}
        self._pending_lock = threading.Lock()
        self._docs: dict[str, int] = {}
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    # --- đọc: LSP dùng header Content-Length
    def _read_message(self) -> dict | None:
        headers = {}
        while True:
            line = self.proc.stdout.readline()
            if not line:
                return None
            line = line.decode("utf-8", "replace").strip()
            if not line:
                break
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        try:
            n = int(headers.get("content-length", "0"))
        except ValueError:
            return None
        if n <= 0:
            return None
        body = b""
        while len(body) < n:
            chunk = self.proc.stdout.read(n - len(body))
            if not chunk:
                return None
            body += chunk
        try:
            return json.loads(body.decode("utf-8", "replace"))
        except Exception:
            return None

    def _read_loop(self) -> None:
        while True:
            msg = self._read_message()
            if msg is None:
                return
            if "id" in msg and ("result" in msg or "error" in msg):
                with self._pending_lock:
                    ev = self._pending.get(msg["id"])
                if ev:
                    ev["result"] = msg
                    ev.setdefault("event", threading.Event()).set()
            # notification từ server (diagnostics…) bỏ qua

    # --- ghi: LSP dùng header
    def _write(self, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        with self._lock:
            self.proc.stdin.write(b"Content-Length: %d\r\n\r\n" % len(data))
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def notify(self, method: str, params: dict | None = None) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def request(self, method: str, params: dict | None = None,
                timeout: float = 20.0) -> dict:
        if self.proc is None:
            return {"error": {"message": self.error or "language server không chạy"}}
        self._id += 1
        rid = self._id
        ev: dict = {"event": threading.Event()}
        with self._pending_lock:
            self._pending[rid] = ev
        self._write({"jsonrpc": "2.0", "id": rid, "method": method,
                     "params": params or {}})
        ok = ev["event"].wait(timeout)
        with self._pending_lock:
            self._pending.pop(rid, None)
        if not ok:
            return {"error": {"message": f"{method} timeout sau {timeout}s"}}
        return ev.get("result", {})

    # --- vòng đời
    def initialize(self, root: str) -> dict:
        if self.proc is None:
            return {"error": {"message": self.error}}
        r = self.request("initialize", {
            "processId": os.getpid(),
            "rootUri": Path(root).resolve().as_uri(),
            "capabilities": {
                "textDocument": {
                    "definition": {"linkSupport": True},
                    "references": {},
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "publishDiagnostics": {},
                },
                "workspace": {"symbol": {}},
            },
            "workspaceFolders": [{"uri": Path(root).resolve().as_uri(),
                                  "name": Path(root).name}],
        }, timeout=60)
        self.notify("initialized", {})
        return r

    def open(self, path: str) -> None:
        if self.proc is None:
            return
        p = Path(path).resolve()
        uri = p.as_uri()
        if uri in self._docs:
            return
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        self._docs[uri] = 1
        self.notify("textDocument/didOpen", {"textDocument": {
            "uri": uri, "languageId": _lang_id(p.suffix), "version": 1, "text": text}})

    def uri(self, path: str) -> str:
        return Path(path).resolve().as_uri()

    def close(self) -> None:
        if self.proc is None:
            return
        try:
            self.request("shutdown", {}, timeout=3)
            self.notify("exit", {})
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


_LANG = {
    ".ts": "typescript", ".tsx": "typescriptreact", ".js": "javascript",
    ".jsx": "javascriptreact", ".mts": "typescript", ".cts": "typescript",
    ".mjs": "javascript", ".cjs": "javascript",
    ".py": "python", ".pyi": "python",
    ".go": "go", ".rs": "rust", ".lua": "lua", ".php": "php", ".rb": "ruby",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp",
    ".cs": "csharp", ".java": "java", ".kt": "kotlin", ".swift": "swift",
}


def _lang_id(suffix: str) -> str:
    return _LANG.get(suffix.lower(), suffix.lstrip(".").lower() or "plaintext")


# --------------------------------------------------------------------- tools

def make_tools() -> list[dict]:
    loc = {"type": "object", "properties": {
        "file": {"type": "string", "description": "Đường dẫn file, tuyệt đối hoặc tương đối với workspace"},
        "line": {"type": "integer", "description": "Số dòng, 1-based"},
        "column": {"type": "integer", "description": "Số cột, 1-based"},
    }, "required": ["file", "line", "column"]}

    return [
        {"name": "lsp_definition", "description":
         "Jump to the definition of the symbol at a position. Use instead of grepping "
         "when you need the real target (handles overloads, re-exports, interfaces).",
         "inputSchema": loc},
        {"name": "lsp_references", "description":
         "Find all references to the symbol at a position, across the whole workspace. "
         "Use before changing a signature or renaming.",
         "inputSchema": loc},
        {"name": "lsp_hover", "description":
         "Type signature and docs for the symbol at a position. Cheaper than reading the "
         "whole file to learn a type.",
         "inputSchema": loc},
        {"name": "lsp_document_symbols", "description":
         "Outline of one file: functions, classes, methods with their ranges.",
         "inputSchema": {"type": "object", "properties": {
             "file": {"type": "string"}}, "required": ["file"]}},
        {"name": "lsp_workspace_symbols", "description":
         "Search symbols by name across the whole workspace. Use to locate a class or "
         "function when you know the name but not the file.",
         "inputSchema": {"type": "object", "properties": {
             "query": {"type": "string"}}, "required": ["query"]}},
    ]


def _pos(params: dict, root: str) -> tuple[str, dict]:
    f = params["file"]
    p = Path(f) if Path(f).is_absolute() else Path(root) / f
    return p.as_uri(), {
        "line": int(params.get("line", 1)) - 1,
        "character": int(params.get("column", 1)) - 1,
    }


def _loc_text(loc: dict, root: str) -> str:
    if "targetUri" in loc:  # LocationLink
        uri, rng = loc["targetUri"], loc.get("targetSelectionRange") or loc.get("targetRange", {})
    else:
        uri, rng = loc.get("uri", ""), loc.get("range", {})
    path = unquote(uri.replace("file://", ""))
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        rel = path
    s = (rng.get("start") or {})
    return f"{rel}:{s.get('line', 0) + 1}:{s.get('character', 0) + 1}"


def _hover_text(h: dict) -> str:
    c = h.get("contents")
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        return c.get("value", "")
    if isinstance(c, list):
        return "\n\n".join(x if isinstance(x, str) else x.get("value", "") for x in c)
    return ""


def _symbols(syms: list, depth: int = 0) -> list[str]:
    out = []
    for s in syms or []:
        kind = s.get("kind")
        rng = s.get("selectionRange") or s.get("range") or {}
        line = (rng.get("start") or {}).get("line", 0) + 1
        out.append(f"{'  ' * depth}{s.get('name', '?')} (kind {kind}) @{line}")
        if s.get("children"):
            out += _symbols(s["children"], depth + 1)
    return out


def call_tool(client: LspClient, root: str, name: str, args: dict) -> str:
    if client.proc is None:
        return client.error or "language server không chạy"
    try:
        if name == "lsp_definition":
            uri, pos = _pos(args, root)
            client.open(unquote(uri.replace("file://", "")))
            r = client.request("textDocument/definition",
                               {"textDocument": {"uri": uri}, "position": pos})
            res = r.get("result") or []
            if isinstance(res, dict):
                res = [res]
            if not res:
                return "Không tìm thấy definition. Kiểm tra lại vị trí hoặc language server đã index xong chưa."
            return "Definition:\n" + "\n".join(f"- {_loc_text(x, root)}" for x in res)

        if name == "lsp_references":
            uri, pos = _pos(args, root)
            client.open(unquote(uri.replace("file://", "")))
            r = client.request("textDocument/references", {
                "textDocument": {"uri": uri}, "position": pos,
                "context": {"includeDeclaration": True}})
            res = r.get("result") or []
            if not res:
                return "Không có reference nào."
            return f"{len(res)} reference:\n" + "\n".join(f"- {_loc_text(x, root)}" for x in res)

        if name == "lsp_hover":
            uri, pos = _pos(args, root)
            client.open(unquote(uri.replace("file://", "")))
            r = client.request("textDocument/hover",
                               {"textDocument": {"uri": uri}, "position": pos})
            h = r.get("result") or {}
            txt = _hover_text(h).strip() if isinstance(h, dict) else ""
            return txt or "Không có thông tin hover ở vị trí này."

        if name == "lsp_document_symbols":
            f = args["file"]
            p = Path(f) if Path(f).is_absolute() else Path(root) / f
            uri = p.as_uri()
            client.open(str(p))
            r = client.request("textDocument/documentSymbol", {"textDocument": {"uri": uri}})
            syms = r.get("result") or []
            return "\n".join(_symbols(syms)) or "File không có symbol."

        if name == "lsp_workspace_symbols":
            r = client.request("workspace/symbol", {"query": args.get("query", "")})
            syms = r.get("result") or []
            if not syms:
                return "Không tìm thấy symbol."
            out = []
            for s in syms[:60]:
                loc = s.get("location") or {}
                out.append(f"- {s.get('name', '?')} (kind {s.get('kind')}) "
                           f"{_loc_text(loc, root) if loc else ''}")
            return "\n".join(out)

        return f"Tool không tồn tại: {name}"
    except Exception as e:  # không để lỗi tool làm chết bridge
        return f"Lỗi {name}: {type(e).__name__}: {e}"


# ----------------------------------------------------------------------- MCP

def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="LSP → MCP bridge",
        epilog="Tham số của language server đặt sau `--`, ví dụ: "
               "--command pyright-langserver --root . -- --stdio")
    ap.add_argument("--command", required=True,
                    help="Lệnh language server, ví dụ: gopls")
    ap.add_argument("--root", default=".")
    # REMAINDER để nhận cả tham số bắt đầu bằng "--" (--stdio, --api-version…)
    ap.add_argument("server_args", nargs=argparse.REMAINDER)
    a = ap.parse_args()

    server_args = list(a.server_args or [])
    if server_args and server_args[0] == "--":
        server_args = server_args[1:]
    # argparse.REMAINDER có thể nuốt cả --root; chặn lại cho an toàn
    if "--root" in server_args:
        i = server_args.index("--root")
        if i + 1 < len(server_args):
            a.root = server_args[i + 1]
        server_args = server_args[:i]

    root = str(Path(a.root).resolve())
    client = LspClient([a.command, *server_args], cwd=root)
    info = client.initialize(root)
    caps = (info.get("result") or {}).get("capabilities", {})
    if client.proc is None:
        log(client.error)
    log("server capabilities:", sorted(caps.keys())[:10])

    initialized = False
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except Exception:
            continue
        method = msg.get("method")
        rid = msg.get("id")

        if method == "initialize":
            initialized = True
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "antigravity-lsp-bridge",
                               "version": "1.0.0"},
            }})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": make_tools()}})
        elif method == "tools/call":
            p = msg.get("params", {})
            out = call_tool(client, root, p.get("name", ""), p.get("arguments") or {})
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": out}], "isError": False}})
        elif method in ("notifications/initialized", "notifications/cancelled"):
            continue
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid, "result": {}})

    client.close()


if __name__ == "__main__":
    main()
