---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree one question at a time. Use when the user wants to stress-test a plan, be grilled on a design, or says "grill me", "hỏi ngược tôi", "vặn tôi về kế hoạch này".
---

# Grill Me

Phỏng vấn ngược người dùng về kế hoạch cho đến khi hai bên hiểu giống nhau. Đi hết từng
nhánh của cây quyết định, gỡ phụ thuộc giữa các lựa chọn theo thứ tự.

Mục đích không phải làm khó. Mục đích là **lộ ra chỗ chưa quyết** trước khi viết code —
chỗ mà nếu để tới lúc code mới phát hiện thì đã tốn công.

## Cách hỏi

**Hỏi từng câu một.** Đợi trả lời rồi mới sang câu tiếp. Dồn 5 câu vào một lượt là làm
người dùng bỏ qua 3 câu cuối.

Mỗi câu đưa 2–4 lựa chọn cụ thể, sát với thứ người dùng thật sự có thể chọn. Lựa chọn kiểu
"Có / Không" là vô dụng, trừ khi câu hỏi đúng là nhị phân.

**Cách trình bày — chọn theo bối cảnh:**

| Bối cảnh | Cách hỏi |
|---|---|
| Mặc định | Ghi câu hỏi + lựa chọn thành **bảng trong một file** (`GRILL.md`), rồi nói ngắn trong chat là đã có câu hỏi ở đó. Người dùng trả lời bằng cách sửa file hoặc nói lại |
| Người dùng gọi `ask_question` / muốn bấm chọn | Dùng tool `ask_question` với các lựa chọn đã soạn |
| Câu hỏi đã có thể tự trả lời bằng cách đọc code | **Tự đọc, không hỏi.** Hỏi cái mình tra được là làm mất thời gian của người dùng |

## Luồng

1. Nhận câu trả lời → xác nhận lại quyết định trong 1–2 câu → hỏi câu tiếp.
2. Nếu trả lời được bằng cách khám phá code hoặc file: tự khám phá, không hỏi.
3. Đi tiếp cho tới khi hết nhánh.
4. Xong: tóm tắt gọn **toàn bộ quyết định** đã chốt, dạng danh sách, để làm đầu vào cho
   `writing-plans`.

## Hỏi cái gì

Đi theo cây, không theo danh sách kiểm tra:

| Nhánh | Câu hỏi điển hình |
|---|---|
| Phạm vi | Cái gì **không** nằm trong lần này? |
| Người dùng | Ai chạm vào đây, và họ đang làm gì khi cần nó? |
| Dữ liệu | Dữ liệu từ đâu, ai sở hữu, sai thì sao? |
| Biên | Đầu vào xấu nhất là gì? Chuyện gì xảy ra khi nó xảy ra? |
| Thất bại | Nếu phần này chết, người dùng thấy gì? |
| Không đảo ngược | Cái gì đã chốt thì sau này sửa rất đắt? |
| Kiểm chứng | Làm sao biết nó chạy đúng — cụ thể là lệnh gì? |

Câu cuối cùng luôn là câu quan trọng nhất: **"Làm sao biết cái này xong?"** Không có câu
trả lời kiểm chứng được thì chưa được bắt đầu code.

## Nguồn

Dựa trên `RobMitt/grill-me-skill` (1.2k★, repo không có file LICENSE). Bản này viết lại:
thay `AskUserQuestion` bằng cách trình bày phù hợp Antigravity, thêm bảng nhánh câu hỏi.
