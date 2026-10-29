---
trigger: always_on
description: "C++: RAII, không new/delete trần, const& cho tham số lớn, cảnh báo bật hết."
---

# C++

## Trước khi sửa
- Đổi signature: `rg "<tên_hàm>\("` — kể cả trong test và benchmark.
- Sửa struct chia sẻ qua header: kiểm mọi translation unit include nó.

## Viết
- Tài nguyên bằng RAII: `std::unique_ptr`, `std::vector`, `std::string`.
- Tham số lớn: `const&`; trả về bằng value (copy elision).
- `const` đúng chỗ; hàm không sửa thì đánh `const`.
- Header có include guard hoặc `#pragma once`.

## Không được
- `new`/`delete` trần.
- `using namespace std;` trong header.
- Buffer thô + memcpy không kiểm kích thước.
- Bỏ qua cảnh báo trình biên dịch.

## Kiểm chứng
```bash
cmake --build build && ctest --test-dir build
# nếu là project nhỏ, tối thiểu:
g++ -std=c++20 -Wall -Wextra -Werror <file> -o /tmp/x
```
