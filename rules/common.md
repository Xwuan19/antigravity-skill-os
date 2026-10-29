---
trigger: always_on
description: "Luật chung khi sửa code trong workspace này: hiểu trước khi sửa, sửa tối thiểu, tái hiện lỗi trước khi sửa, kiểm chứng bằng lệnh thật, không báo xong khi chưa có output."
---

# Luật chung khi làm code

## Sáu cổng, đúng thứ tự

1. **Hiểu** — đọc chỗ định sửa và mọi chỗ gọi tới nó. Không đoán từ tên file.
2. **Tối giản** — sửa ít dòng nhất giải quyết trọn vấn đề. Không dựng abstraction cho một chỗ dùng.
3. **Tái hiện** — lỗi phải tái hiện được trước khi sửa. Không tái hiện được nghĩa là chưa hiểu lỗi.
4. **Kiểm chứng** — chạy lệnh, dán output. "Chắc là chạy được" không phải bằng chứng.
5. **Review** — đọc lại diff của chính mình: mỗi dòng đổi phải có lý do, không có dòng thừa.
6. **Giao** — nói rõ đã đổi gì, kiểm bằng lệnh gì, còn chỗ nào chưa chắc.

## Bằng chứng

- Không báo "đã xong" khi chưa chạy thử.
- Không báo "đã sửa" khi chưa thấy hiện tượng lỗi biến mất.
- Không báo "test pass" khi chưa dán dòng summary của test.

## Phạm vi

- Chỉ sửa trong workspace này.
- Đổi API công khai, schema, hay format dữ liệu: nói trước, đừng lặng lẽ đổi.
- Không thêm dependency khi thư viện chuẩn làm được.
- Không sửa file test để test cũ pass — sửa code.
