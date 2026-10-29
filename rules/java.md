---
trigger: always_on
description: "Java: Optional ở biên, trả collection rỗng thay vì null, try-with-resources, kiểm bằng mvn/gradle test."
---

# Java

## Trước khi sửa
- Đổi public method: `rg "<tênMethod>\("` — kể cả caller trong module khác.
- Đổi DTO/entity: kiểm cả chỗ serialize (JSON/DB).

## Viết
- Trả `Optional<T>` cho "có thể không có"; không trả `null` cho method mới.
- Trả collection rỗng (`List.of()`), không `null`.
- Đóng tài nguyên bằng try-with-resources.
- `equals`/`hashCode` đi cùng nhau; dùng `record` khi chỉ chở dữ liệu.

## Không được
- `catch (Exception e) {}` rỗng.
- Nối chuỗi trong vòng lặp — dùng `StringBuilder`.
- `Optional.get()` không kiểm tra.
- Sửa `pom.xml`/`build.gradle` thêm thư viện nặng mà không hỏi.

## Kiểm chứng
```bash
mvn -q test          # hoặc: gradle test
mvn -q compile       # bắt lỗi kiểu sớm
```
