---
trigger: always_on
description: "Swift: không force unwrap, guard let sớm, struct trước class, kiểm bằng swift test."
---

# Swift

## Trước khi sửa
- Đổi property trong View/Model: kiểm cả Preview và test.
- Sửa protocol: mọi kiểu tuân thủ phải sửa theo.

## Viết
- `guard let`/`if let` để thoát sớm, không lồng `if` sâu.
- `struct` mặc định; `class` chỉ khi cần tham chiếu hoặc kế thừa.
- `@MainActor` cho UI; I/O bằng `async`/`await`, không callback lồng.
- Lỗi bằng `throws` + `Error` enum có ca rõ ràng.

## Không được
- `!` force unwrap trong code mới.
- `try!` ngoài test.
- `DispatchQueue.main.asyncAfter` để "đợi" dữ liệu.
- `@objc` tràn lan cho logic thuần Swift.

## Kiểm chứng
```bash
swift build && swift test
xcodebuild -scheme <scheme> test      # project Xcode
```
