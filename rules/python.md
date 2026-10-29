---
trigger: always_on
description: "Python: type hint ở biên, không bắt Exception trần, không mutable default, kiểm bằng pytest."
---

# Python

## Trước khi sửa
- Tìm mọi chỗ import thứ định đổi: `rg "from .*<tên> import|import <tên>"`.
- Hàm public có test và script gọi: kiểm cả hai, đừng chỉ đọc chỗ định sửa.

## Viết
- Type hint ở mọi hàm public. File mới: `from __future__ import annotations`.
- Bọc lỗi phải giữ nguyên nhân: `raise ConfigError(f"bad {path}") from e`.
- Đường dẫn bằng `pathlib.Path`, không nối chuỗi.
- So `None` bằng `is None`.
- Code mới dùng f-string.

## Không được
- `except Exception: pass` — nuốt lỗi.
- Mutable default: `def f(x=[])`.
- `os.path` trong code mới.
- Sửa `sys.path` để vá import hỏng.

## Kiểm chứng
```bash
python -m pytest -q
ruff check . && ruff format --check .    # nếu repo có ruff
```
Chỗ vừa sửa không có test → viết test trước khi báo xong.
