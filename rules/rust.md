---
trigger: always_on
description: "Rust: không unwrap ngoài test, dùng ? và thiserror, clippy sạch."
---

# Rust

## Trước khi sửa
- Đổi signature public: `rg "<fn_name>\("`.
- Sửa trait: kiểm mọi impl, kể cả trong test.

## Viết
- Lan truyền lỗi bằng `?`; lỗi của bạn dùng `thiserror`, lỗi ứng dụng dùng `anyhow`.
- Mượn trước, clone sau — clone là lựa chọn cuối, không phải mặc định.
- `&str`/`&[T]` cho tham số đọc; `String`/`Vec<T>` chỉ khi sở hữu thật.
- Nhánh lỗi phải có: `match` đủ nhánh, không `_ => unreachable!()` khi chưa chắc.

## Không được
- `unwrap()`/`expect()` ngoài test và `main`.
- `clone()` để né borrow checker mà không hiểu vì sao.
- `unsafe` không kèm `// SAFETY:`.
- `#[allow(...)]` để tắt cảnh báo clippy.

## Kiểm chứng
```bash
cargo clippy --all-targets -- -D warnings
cargo test
cargo fmt --check
```
