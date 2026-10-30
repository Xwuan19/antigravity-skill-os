#!/usr/bin/env python3
"""Test hồi quy cho `guess_profile` — dò profile của `--profile auto`.

Chạy: python3 tools/test_guess.py
Không cần mạng, không cần cài gì.
"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "inst", Path(__file__).resolve().parent / "install.py")
inst = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inst)

# (tên, {đường dẫn tương đối: nội dung}, profile mong đợi)
CASES = [
    ("giáo án", {"giao-an-tuan-3.docx": "x", "de-kiem-tra.docx": "x"}, "education-k12"),
    ("slide", {"bai-giang.pptx": "x"}, "docs-writer"),
    ("tài liệu", {"bao-cao.docx": "x", "so-lieu.xlsx": "x"}, "docs-writer"),
    ("tauri", {"tauri.conf.json": "{}", "src/main.rs": "fn main(){}"}, "desktop-app"),
    ("electron", {"package.json": '{"devDependencies":{"electron":"31"}}'}, "desktop-app"),
    ("react native", {"package.json": '{"dependencies":{"react-native":"0.74"}}'}, "mobile-app"),
    ("flutter", {"pubspec.yaml": "name: x"}, "mobile-app"),
    ("next", {"package.json": '{"dependencies":{"next":"14"}}',
              "app/page.tsx": "x"}, "web-admin"),
    ("vue", {"package.json": "{}", "src/App.vue": "x"}, "web-admin"),
    ("python cli", {"main.py": "print(1)", "lib/core.py": "x"}, "cli-tool"),
    ("go", {"main.go": "package main"}, "cli-tool"),
    ("shadcn", {"components.json": "{}", "src/components/ui/button.tsx": "x"},
     "design-system"),
    ("html tĩnh", {"index.html": "x", "style.css": "x"}, "static-site"),
    # Trang tĩnh rất hay có JS thuần — từng bị nhận thành cli-tool (134 skill, 78%)
    ("html + app.js", {"index.html": "x", "app.js": "console.log(1)",
                       "style.css": "x"}, "static-site"),
    ("html + index.js", {"index.html": "x", "index.js": "x"}, "static-site"),
    ("html + jsx", {"index.html": "x", "app.jsx": "x"}, "static-site"),
    # ...nhưng Node script không có HTML thì vẫn là CLI
    ("node script", {"cli.js": "#!/usr/bin/env node"}, "cli-tool"),
    ("node + tsconfig", {"index.html": "x", "main.ts": "x", "tsconfig.json": "{}"},
     "cli-tool"),
]

# Workspace nằm dưới thư mục cha tên trùng `skip` — từng làm mọi file bị loại và
# báo nhầm "thư mục trống" (lỗi thật gặp trên máy Windows có …/.gemini/…).
PARENT_TRAPS = ["", ".gemini/scratch", "build", "target", "node_modules", "packs"]


def main() -> int:
    ok = fail = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for trap in PARENT_TRAPS:
            base = root / trap / "ws" if trap else root / "ws"
            # một tín hiệu duy nhất, để phép thử nói về đường dẫn chứ không về ưu tiên
            (base / "main.py").parent.mkdir(parents=True, exist_ok=True)
            (base / "main.py").write_text("print(1)", encoding="utf-8")
            got, why = inst.guess_profile(base)
            want = "cli-tool"
            tag = f"dưới thư mục cha '{trap or '(gốc)'}'"
            if got == want:
                ok += 1
                print(f"  ✓ {tag}")
            else:
                fail += 1
                print(f"  ✗ {tag}: {got} ({why}), mong đợi {want}")

        for name, files, want in CASES:
            ws = root / "case" / name.replace(" ", "-")
            for rel, body in files.items():
                f = ws / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(body, encoding="utf-8")
            got, why = inst.guess_profile(ws)
            if got == want:
                ok += 1
                print(f"  ✓ {name:14} → {got}")
            else:
                fail += 1
                print(f"  ✗ {name:14} → {got} ({why}), mong đợi {want}")

        empty = root / "empty"
        empty.mkdir()
        got, _ = inst.guess_profile(empty)
        if got is None:
            ok += 1
            print("  ✓ thư mục trống   → None")
        else:
            fail += 1
            print(f"  ✗ thư mục trống   → {got}")

    print(f"\n  {ok}/{ok + fail} pass\n")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
