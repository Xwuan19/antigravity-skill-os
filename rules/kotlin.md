---
trigger: always_on
description: "Kotlin: val trước var, không !!, sealed class cho state, when phải đủ nhánh."
---

# Kotlin

## Trước khi sửa
- Đổi data class: kiểm `copy(`, `componentN`, và chỗ destructuring.
- Coroutine: tìm `scope.launch` quanh chỗ sửa để biết ngữ cảnh huỷ.

## Viết
- `val` mặc định, `var` chỉ khi thật sự đổi.
- State bằng `sealed interface`, xử lý bằng `when` đủ nhánh.
- Nullable: `?.`, `?:`, `requireNotNull` kèm thông điệp.
- Coroutine: `suspend` cho hàm I/O, không `GlobalScope`.

## Không được
- `!!` trong code mới.
- `runBlocking` trong code ứng dụng.
- Bắt `Throwable`.
- `lateinit var` khi có thể khởi tạo ngay.

## Kiểm chứng
```bash
./gradlew test
./gradlew compileKotlin     # bắt lỗi kiểu sớm
```
