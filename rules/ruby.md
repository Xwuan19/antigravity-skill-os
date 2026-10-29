---
trigger: always_on
description: "Ruby: không monkey-patch core, frozen_string_literal, raise lớp lỗi cụ thể."
---

# Ruby

## Trước khi sửa
- Đổi method trên class dùng chung: `rg "\.<tên_method>"` — Ruby khó thấy caller.
- Gem: kiểm `Gemfile.lock` trước khi thêm.

## Viết
- Mỗi file mới: `# frozen_string_literal: true`.
- Lỗi: subclass `StandardError` có tên riêng, `raise` kèm thông điệp.
- Block: `each`/`map` rõ ý; tránh `for`.
- `!` method chỉ khi có bản không `!` an toàn.

## Không được
- Monkey-patch `String`, `Array`, `Hash`, `Object`.
- `rescue => e` rồi bỏ qua.
- `method_missing` cho logic thường.
- `eval` / `send` với chuỗi từ ngoài.

## Kiểm chứng
```bash
bundle exec rspec       # hoặc: bundle exec rake test
bundle exec rubocop     # nếu repo có
```
