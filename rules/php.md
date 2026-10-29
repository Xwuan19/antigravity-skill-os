---
trigger: always_on
description: "PHP: declare strict_types, so sánh ===, PSR-4, kiểm bằng phpunit."
---

# PHP

## Trước khi sửa
- Đổi hàm public: `rg "<tên_hàm>\("`.
- Sửa model: kiểm cả controller, validation và migration.

## Viết
- Đầu mỗi file PHP: `declare(strict_types=1);`.
- So sánh `===`, không `==`.
- Type ở tham số và return; nullable ghi rõ `?Type`.
- Namespace theo PSR-4, một class một file.

## Không được
- `@` để nuốt cảnh báo.
- `eval`, `extract`, `${$var}`.
- SQL nối chuỗi — dùng prepared statement.
- Sửa `composer.json` thêm package mà không hỏi.

## Kiểm chứng
```bash
vendor/bin/phpunit
php -l <file>        # kiểm cú pháp nhanh
```
