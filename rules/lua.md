---
trigger: always_on
description: "Lua: local cho mọi biến, không global, pcall ở biên, kiểm bằng luacheck."
---

# Lua

## Trước khi sửa
- Đổi hàm trong module: `rg "require\(['"]<tên>['"]\)"` để thấy chỗ dùng.
- Sửa config/table toàn cục: kiểm cả file init.

## Viết
- `local` cho mọi biến và hàm trong module; trả table ở cuối file.
- Lỗi: `error({code = ..., msg = ...})` hoặc `error("...")`; bắt bằng `pcall`/`xpcall` ở biên.
- So sánh `==` cho giá trị, `rawequal` chỉ khi thật cần.
- Chuỗi dài: `[[...]]`; nối bằng `table.concat`.

## Không được
- Gán biến global (không `local`).
- `pcall` bọc cả logic nghiệp vụ (che lỗi).
- Sửa `_G` hoặc thư viện chuẩn.
- `os.execute` với chuỗi ghép từ input.

## Kiểm chứng
```bash
luacheck .            # nếu có
lua <file_test>.lua   # hoặc: busted
```
