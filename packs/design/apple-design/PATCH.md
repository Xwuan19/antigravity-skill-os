# apple-design — lưu ý khi dùng

Nguồn: `emilkowalski/skills` @ `e8a175de22ae1e49370fc144c1f3bb9aeedf988d`
License: MIT · Kích thước: 23.036 bytes

Bản `SKILL.md` trong thư mục này là **bản gốc, không sửa** (giữ đúng để đối chiếu upstream).

## Hai điểm cần biết

### 1. Mục `## Initial Response` chiếm lượt trả lời đầu

```markdown
When this skill is first invoked without a specific question, respond only with:
> I'm ready to help you build fluid, Apple-style interfaces on the web...
Do not provide any other information until the user asks a question.
```

Trong Antigravity skill được nạp **tự động theo description**, không có khái niệm
"invoked". Nếu model hiểu nhầm là vừa được invoke, nó có thể chỉ trả về đúng câu
giới thiệu đó và không làm gì khác. Không phải lỗi chặn, nhưng gây khó chịu.

Cách xử lý: nếu gặp, xoá mục này khỏi bản đã cài
(`.agents/skills/apple-design/SKILL.md`). Không xoá ở đây để giữ khả năng diff với upstream.

### 2. Sát trần kích thước

23.036 / 24.000 bytes. Antigravity cắt file vượt 24 KB, và bản upstream chỉ cần thêm
~1 KB nữa là vượt. Router đã pin commit nên bản của bạn sẽ không tự phình — chỉ cần
biết khi muốn cập nhật lên commit mới.

## Quan hệ với `frontend-design`

Không xung đột — khác trục:

| | frontend-design | apple-design |
|---|---|---|
| Trả lời câu hỏi | Trông như thế nào? | Cảm giác khi chạm vào thì sao? |
| Trục | Bề rộng: palette, type, layout, signature | Bề sâu: response, spring, gesture, interruptibility |
| Dùng khi | Bắt đầu một màn hình mới | Làm phần tương tác cho mượt |

Cài cả hai là hợp lý cho project cần cả ấn tượng thị giác lẫn chuyển động.
