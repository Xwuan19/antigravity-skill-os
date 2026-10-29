---
trigger: always_on
description: "SQL: migration phải lùi được, không SELECT * trong code mới, index cho cột WHERE/JOIN."
---

# SQL

## Trước khi sửa
- Đổi schema: tìm mọi câu query chạm bảng đó (`rg "<tên_bảng>"`).
- Migration: xác định có rollback không, có chạy được khi bảng đang có dữ liệu không.

## Viết
- Migration: lên và xuống đều có; thêm cột cho phép NULL hoặc có default trước, backfill sau, đặt NOT NULL cuối.
- Query trong code: liệt kê cột cần dùng, không `SELECT *`.
- Cột trong `WHERE`/`JOIN`/`ORDER BY` phải có index (kiểm bằng EXPLAIN).
- Xoá/sửa hàng loạt: chạy `SELECT` cùng điều kiện trước, xem số dòng.

## Không được
- Chạy migration trên production mà chưa thử trên bản sao.
- Đổi kiểu cột theo cách cắt dữ liệu âm thầm.
- Nối chuỗi SQL bằng input người dùng.
- `DELETE`/`UPDATE` không `WHERE`.

## Kiểm chứng
```bash
# luôn chạy trên bản sao trước
psql <db> -f migration.sql
EXPLAIN ANALYZE <query>       # xem có dùng index không
```
