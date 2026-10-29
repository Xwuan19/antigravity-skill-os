---
trigger: always_on
description: "Go: wrap lỗi bằng %w, không panic, context là tham số đầu, kiểm bằng go test -race."
---

# Go

## Trước khi sửa
- Đổi signature hàm: `rg "<tên hàm>\("` để thấy hết chỗ gọi.
- Interface thay đổi: kiểm cả mock trong test.

## Viết
- Lỗi có ngữ cảnh: `fmt.Errorf("load config: %w", err)`.
- `context.Context` là tham số đầu, không nhét vào struct.
- Nhận interface, trả struct. Interface 1–3 method.
- Zero value phải dùng được; constructor chỉ khi thật cần.

## Không được
- `panic` ngoài `main`/lúc khởi tạo.
- Bỏ qua `err` bằng `_`.
- Goroutine không có đường thoát (không select với `ctx.Done()`).
- `time.Sleep` để "chờ" trong test.

## Kiểm chứng
```bash
go vet ./...
go test -race ./...
gofmt -l .        # phải rỗng
```
