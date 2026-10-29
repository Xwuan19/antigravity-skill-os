# Nói gì với Antigravity để nó cài repo này

> Chép nguyên khối, đổi phần trong `[ngoặc]`, dán vào ô chat của Antigravity.

---

## 1. Cài cho toàn bộ máy (mặc định)

Dán **một lần**. Sau đó mọi project đều dùng được, không cần làm gì thêm.

```
Cài Antigravity Skill OS cho toàn bộ máy.

Chạy đúng hai lệnh sau:

git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os 2>/dev/null || git -C ~/.antigravity-skill-os pull --ff-only
bash ~/.antigravity-skill-os/bootstrap.sh --system

Lưu ý:
- Nếu lệnh đầu báo "already exists", cứ chạy tiếp lệnh thứ hai.
- Không sửa file nào trong repo vừa clone.
- Không tự cài language server; nếu script báo thiếu thì chỉ liệt kê lệnh cài cho tôi.

Xong thì báo lại: bao nhiêu skill đã cài, nằm ở đâu, và những gì cần làm tiếp.
```

Kết quả ghi vào `~/.gemini/`:

| Ghi gì | Ở đâu |
|---|---|
| Rules always_on (ponytail full, skill-first, verify) | `AGENTS.md` |
| Toàn bộ **144** skill | `config/skills/` |
| LSP cho mọi language server có trên máy | `config/mcp_config.json` |

Mở project nào cũng thấy. Project mới không phải cài lại.

## 2. Chỉ khi muốn cài hẹp cho một project

Dùng khi bạn muốn workspace đó **không** thấy skill ngoài lĩnh vực của nó.

```
Cài Antigravity Skill OS cho riêng project này.

git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os 2>/dev/null || git -C ~/.antigravity-skill-os pull --ff-only
bash ~/.antigravity-skill-os/bootstrap.sh [PROFILE] .

Không sửa file trong repo. Xong báo lại số skill và stack đã nhận.
```

| Project | `[PROFILE]` |
|---|---|
| Web quản lý, dashboard, CRUD, SaaS | `web-admin` |
| Landing page, marketing site, portfolio | `landing` |
| CLI, script, backend thuần, thư viện | `cli-tool` |
| Ứng dụng mobile (React Native, Expo) | `mobile-app` |
| Design system, component library | `design-system` |
| Viết tài liệu, báo cáo, thuyết trình | `docs-writer` |
| Giáo án phổ thông, đề kiểm tra | `education-k12` |
| Dạy ngoại ngữ, trung tâm, gia sư | `education-language` |
| Nuôi chính hệ thống skill/agent/hook | `meta` |

Đừng cài nhiều profile vào cùng một workspace.

---

## 3. Kiểm chứng sau khi khởi động lại

Cài xong **phải khởi động lại Antigravity** để nó nạp skill + MCP server. Rồi dán:

```
Kiểm tra Antigravity Skill OS đã nạp chưa:
1. Đọc ~/.gemini/AGENTS.md — tóm tắt 3 luật đang bật
2. Đếm số skill trong ~/.gemini/config/skills, nhóm theo lĩnh vực
3. Nói rõ: có skill nào về tái hiện bug trước khi sửa không, tên là gì
```

Câu 3 là phép thử thật. Nếu nó kể ra `root-cause` / `systematic-debugging` thì đã nạp.

Câu thử hành vi (không phải thử cài):

| Hỏi | Có skill | Không có skill |
|---|---|---|
| "Sửa bug này" (không nói thêm) | Hỏi hoặc tái hiện trước | Sửa luôn |
| "Xong chưa?" | Chạy lệnh kiểm chứng rồi trả lời kèm output | "Xong rồi" |
| "Review giúp" | Mỗi phát hiện kèm kịch bản hỏng | Góp ý chung chung |

---

## 4. Cập nhật lên bản mới

```
Cập nhật Antigravity Skill OS trên toàn máy:
git -C ~/.antigravity-skill-os pull --ff-only || git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os
bash ~/.antigravity-skill-os/bootstrap.sh --system
```

Chạy lại vô hại: skill mới thì chép, skill đã có thì bỏ qua.

## 5. Gỡ

```
Gỡ Antigravity Skill OS khỏi máy:
1. python3 ~/.antigravity-skill-os/tools/install.py --uninstall
2. python3 ~/.antigravity-skill-os/tools/lsp.py --global --remove
Giữ lại file nào không do Skill OS tạo.
```

Nếu đã cài hẹp cho project nào thì gỡ thêm trong project đó:

```
python3 ~/.antigravity-skill-os/tools/lsp.py -w . --remove
rồi xoá thư mục .agents/ của project
```

---

## 6. Vì sao phải chạy lệnh, không chỉ đưa link

Antigravity **không** tải skill từ URL. Skill phải là file trên đĩa:

```
~/.gemini/config/skills/<id>/SKILL.md     ← mọi project
<workspace>/.agents/skills/<id>/SKILL.md  ← chỉ project đó
```

Nói "hãy đọc repo này" thì model chỉ đọc được văn bản, không tạo ra file skill. Đó là lý do
prompt ở trên yêu cầu **chạy `bootstrap.sh`** chứ không phải "đọc repo".

Sau khi cài thì đúng là tự động: không slash command, agent tự chọn skill theo mô tả mỗi lượt.

| Việc | Ai làm |
|---|---|
| Chép skill vào đĩa | `bootstrap.sh --system`, **một lần cho cả máy** |
| Chọn skill theo ngữ cảnh | Antigravity, tự động mỗi lượt |
| Ponytail `full` | global rules, mọi phiên |
| Hook / plugin / MCP | tự nạp sau khi khởi động lại |
| Project mới | không phải làm gì — đã ở tầng global |
| Language server | **bạn** cài binary (`tools/lsp.py --check` in lệnh) |
