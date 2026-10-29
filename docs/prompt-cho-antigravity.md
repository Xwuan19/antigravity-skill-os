# Nói gì với Antigravity để nó cài repo này

> Chép nguyên khối, đổi phần trong `[...]`, dán vào ô chat của Antigravity.

---

## 1. Cài vào project đang mở

Dùng cái này 90% trường hợp. Antigravity sẽ chạy lệnh qua tool `run_command`.

```
Cài Antigravity Skill OS cho project này.

Chạy đúng hai lệnh sau trong thư mục project hiện tại:

git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os 2>/dev/null || git -C ~/.antigravity-skill-os pull --ff-only
bash ~/.antigravity-skill-os/bootstrap.sh [PROFILE] .

Lưu ý:
- Nếu lệnh đầu báo "already exists", cứ chạy tiếp lệnh thứ hai.
- Không sửa file nào trong repo vừa clone.
- Không tự cài language server; nếu script báo thiếu thì chỉ liệt kê lệnh cài cho tôi.

Xong thì báo lại: bao nhiêu skill đã cài, stack gì, và những gì cần làm tiếp.
```

Đổi `[PROFILE]` theo bảng dưới. Không chắc thì để `web-admin` hoặc `cli-tool`.

## 2. Chọn profile

| Project của bạn | `[PROFILE]` |
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

Mỗi project một profile. **Đừng cài nhiều profile vào cùng một workspace** — mục đích của
repo là mỗi workspace chỉ có skill đúng lĩnh vực của nó.

Antigravity tự dò ngôn ngữ trong project (`.py`, `.ts`, `.go`…) nên không cần khai báo.
Muốn ép: thêm `--stacks python,go` vào lệnh thứ hai.

---

## 3. Kiểm chứng sau khi khởi động lại

Cài xong **phải khởi động lại Antigravity** để nó nạp skill + MCP server. Rồi dán:

```
Kiểm tra Antigravity Skill OS đã nạp chưa:
1. Đọc ~/.gemini/AGENTS.md — tóm tắt 3 luật đang bật
2. Liệt kê skill đang có trong .agents/skills, nhóm theo lĩnh vực
3. Nói rõ: có skill nào về tái hiện bug trước khi sửa không, tên là gì
```

Câu 3 là phép thử thật. Nếu nó kể ra `root-cause` / `systematic-debugging` thì skill đã nạp.

Câu thử hành vi (không phải thử cài):

| Hỏi | Có skill | Không có skill |
|---|---|---|
| "Sửa bug này" (không nói thêm) | Hỏi hoặc tái hiện trước | Sửa luôn |
| "Xong chưa?" | Chạy lệnh kiểm chứng rồi trả lời kèm output | "Xong rồi" |
| "Review giúp" | Mỗi phát hiện kèm kịch bản hỏng | Góp ý chung chung |

---

## 4. Cập nhật lên bản mới

```
Cập nhật Antigravity Skill OS và cài lại cho project này.
Chạy: bash ~/.antigravity-skill-os/bootstrap.sh [PROFILE] .
Nếu chưa có ~/.antigravity-skill-os thì clone trước như lần đầu.
```

`bootstrap.sh` chạy lại vô hại: skill mới thì chép, skill đã có thì bỏ qua.

## 5. Gỡ

```
Gỡ Antigravity Skill OS khỏi project này và khỏi máy:
1. python3 ~/.antigravity-skill-os/tools/install.py --uninstall
2. python3 ~/.antigravity-skill-os/tools/lsp.py -w . --remove
3. Xoá thư mục .agents/ trong project này
Giữ lại file nào không do Skill OS tạo.
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
| Chép skill vào đĩa | `bootstrap.sh`, một lần |
| Chọn skill theo ngữ cảnh | Antigravity, tự động mỗi lượt |
| Ponytail `full` | global rules, mọi phiên |
| Hook / plugin / MCP | tự nạp sau khi khởi động lại |
| Language server | **bạn** cài binary (`tools/lsp.py --check` in lệnh) |
