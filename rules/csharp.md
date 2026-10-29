---
trigger: always_on
description: "C#: nullable reference type bật, không .Result/.Wait(), await using cho tài nguyên async."
---

# C#

## Trước khi sửa
- Đổi public API: `rg "<tênMethod>\("` — cả trong project test.
- Đổi model bind từ JSON/EF: kiểm cả migration và serializer.

## Viết
- `Nullable` bật; cảnh báo null là lỗi thật, không tắt bằng `!`.
- Async: `async Task`/`async ValueTask`, không `async void` trừ event handler.
- Tài nguyên async: `await using`.
- So chuỗi bằng `string.Equals(a, b, StringComparison.Ordinal)`.

## Không được
- `.Result` / `.Wait()` trên Task (deadlock).
- `catch (Exception) { }` rỗng.
- LINQ nhiều lượt trên cùng collection trong vòng lặp — `ToList()` một lần.
- `DateTime.Now` cho logic — dùng `TimeProvider`/`UtcNow`.

## Kiểm chứng
```bash
dotnet build --warnaserror
dotnet test
```
