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
| **186** skill (60 skill chỉ dành cho project) | `config/skills/` |
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

## 3. Bắt Antigravity **dùng** tầng global (khác với cài)

Antigravity không có công tắc "bật global". Tầng global là **thư mục**:

```
~/.gemini/config/skills/<id>/SKILL.md   → mọi project, mọi phiên
~/.gemini/AGENTS.md                     → luật always_on, nạp trước mọi request
```

Áp dụng = file nằm đúng chỗ + khởi động lại. Không câu nói nào làm nó nạp nếu file chưa có,
và không câu nào cần thiết nếu file đã có. Ba việc **thật sự** cần nói:

### 3a. Cài / cập nhật tầng global

```
Áp dụng tầng skill global của Antigravity Skill OS cho máy này.

1. Kiểm tra hiện trạng: ls ~/.gemini/config/skills | wc -l
2. Chưa có repo thì: git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os
   Có rồi thì:      git -C ~/.antigravity-skill-os pull --ff-only
3. Chạy: bash ~/.antigravity-skill-os/bootstrap.sh --system
4. Báo lại: script in ra bao nhiêu skill, ngân sách token bao nhiêu %, và nhắc tôi khởi động lại.

Không sửa file nào trong repo. Không cài language server — thiếu thì chỉ in lệnh cho tôi.
```

Muốn bản global gọn hơn (bỏ hẳn pack giáo dục/tài liệu khỏi mọi project):

```
bash ~/.antigravity-skill-os/bootstrap.sh --system --exclude-pack education,docs
```

### 3b. Bắt nó thật sự tra skill trước khi làm

Luật này **đã nằm trong** `~/.gemini/AGENTS.md` §1 (skill-first), nên sau khi cài bạn không
phải nói. Chỉ dán lại khi phiên dài và nó bắt đầu làm ẩu:

```
Từ giờ trong phiên này:
1. Trước khi trả lời, đối chiếu việc cần làm với skill đang nạp — global ở
   ~/.gemini/config/skills/ và project ở .agents/skills/.
2. Khớp skill nào thì đọc SKILL.md của nó rồi làm theo. Không cần tôi gõ /tên-skill.
3. Mở đầu câu trả lời bằng một dòng: đang dùng skill nào (hoặc "không có skill khớp").
4. Không có file thì đừng bịa nội dung skill. Nói thẳng là không có.
```

### 3c. Kiểm chứng nó thấy tầng global

Khởi động lại Antigravity **một lần**, rồi dán:

```
Kiểm tra tầng skill global:
1. Đếm thư mục trong ~/.gemini/config/skills, nhóm theo lĩnh vực.
2. Kể tên 3 luật trong ~/.gemini/AGENTS.md.
3. Có skill nào để review UI không? Tên gì, đọc mô tả của nó.
```

Đáp án đúng của câu 3: `accessibility` hoặc `taste-skill` / `ui-ux-pro-max`. Nếu nó trả lời
"không có skill nào" thì tầng global chưa nạp — kiểm `ls ~/.gemini/config/skills | wc -l` rồi
khởi động lại lần nữa.

| Con số trên đĩa | Ứng với lệnh nào | Đồng hồ Antigravity |
|---|---|---|
| **156** | `--system --exclude-pack education,docs` (khuyên dùng) | ≈ 87% |
| **186** | `--system` (mặc định) | ≈ 103% → **vượt, bị loại bớt** |
| **190** | `--system --include-manual` | ≈ 105% |
| 190 thành 186 | 4 skill manual còn sót → `--prune` | — |

Panel có thể hiện thêm skill **không phải của repo** (`agy-customizations`, `antigravity-guide`…)
do Antigravity tự thêm từ GitHub. `install.py --system` liệt kê chúng kèm lệnh `rm -rf` nếu bạn
muốn dọn — `--prune` **không** đụng vào chúng.

Script cài in đúng số skill nó vừa cài; nếu số trên đĩa nhiều hơn thì đó là thư mục còn sót từ
bản cũ, `install.py` sẽ liệt kê tên.

## 3d. Chuyển sang "global mỏng + rót theo project"

Dùng khi bạn muốn mỗi project **chỉ** thấy skill của nó (đỡ trần ngữ cảnh), thay vì mọi project
đều thấy 186 skill. Dán:

```
Chuyển Antigravity Skill OS sang mô hình global mỏng, mỗi project một bộ skill riêng.

1. Chạy: bash ~/.antigravity-skill-os/bootstrap.sh --core --prune
   (global còn rules + 4 skill; bỏ 182 skill global của lần cài --system trước)

2. Rồi với từng project của tôi, mỗi cái một lần:
   bash ~/.antigravity-skill-os/bootstrap.sh auto <đường-dẫn-project>

   Project hiện có: [liệt kê đường dẫn]. Script tự dò profile theo nội dung thư mục
   và in lý do; nếu dò sai thì đổi sang profile tay (web-admin, landing, static-site,
   cli-tool, mobile-app, desktop-app, design-system, docs-writer, education-k12,
   education-language, meta).

3. Báo lại bảng: project → profile → số skill → % ngân sách script in ra.

Không sửa file trong repo. Không xoá skill nào không do Skill OS tạo.
```

Sau đó mỗi project mới chỉ cần một lệnh. Đổi profile cho một project thì thêm `--prune` để gỡ
skill của profile cũ.

## 4. Kiểm chứng sau khi khởi động lại

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

## 5. Cập nhật lên bản mới

```
Cập nhật Antigravity Skill OS trên toàn máy:
git -C ~/.antigravity-skill-os pull --ff-only || git clone --depth 1 https://github.com/Xwuan19/antigravity-skill-os ~/.antigravity-skill-os
bash ~/.antigravity-skill-os/bootstrap.sh --system
```

Chạy lại vô hại: skill mới thì chép, skill đã có thì bỏ qua.

## 6. Gỡ

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

## 7. Vì sao phải chạy lệnh, không chỉ đưa link

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

## 4. Cập nhật toàn bộ repo đã cài

Prompt dưới đây cập nhật **repo và cấu hình đang dùng**, không chỉ skill. Cần repo mới có
`--update-owned`. Trên Windows dùng `python` thay `python3` nếu phù hợp.

```
Cập nhật Antigravity Skill OS từ https://github.com/Xwuan19/antigravity-skill-os.
Hãy dùng run_command để thực hiện, không chỉ hướng dẫn.

1. Tìm repo đã cài. Kiểm tra nhánh và git status; nếu có thay đổi cục bộ,
   không xóa hay ghi đè. Báo tôi trước. Nếu sạch và đang ở main, ghi commit cũ,
   chạy git pull --ff-only, rồi báo commit mới. Nếu không ở main, dừng và báo tôi.

2. Đọc README, hướng dẫn nâng cấp và diff giữa hai commit. Xác định thay đổi ở
   skill, rules, profile, installer, agent, plugin, hook, MCP và thành phần mới.
   Xác định máy đang dùng --core hay --system, các workspace/profile và tùy chọn
   đã cài. Không tự thay đổi cấu hình, không đoán workspace nếu thiếu thông tin.

3. Trước khi cập nhật, sao lưu các skill tôi có thể đã sửa tay và file cấu hình
   liên quan. Chạy installer từ repo mới ở chế độ --dry-run, với cấu hình cũ,
   --update-owned và các tùy chọn cũ. Đọc output; chỉ dùng --prune khi đã xem
   các mục sẽ gỡ và xác nhận phù hợp. Nếu có xung đột hay thiếu thông tin, báo tôi.

4. Nếu an toàn, chạy lại không có --dry-run. --update-owned chỉ cập nhật skill có
   dấu Skill OS, vẫn ghi đè sửa tay trong các thư mục đó; nó không tự cập nhật
   agent/plugin/hook đã có. Kiểm tra từng phần theo hướng dẫn bản mới và báo tôi
   trước khi ghi đè các file không xác định được chủ sở hữu. Không dùng --force
   mù quáng. Rules global cũ được installer backup nhưng vẫn phải kiểm tra trước.

5. Chạy kiểm tra liên quan và đọc kết quả thật. Báo commit cũ/mới, thay đổi đã
   áp dụng, kiểm tra đã chạy, xung đột và phần chưa thể cập nhật hoặc xác minh.
   Không tuyên bố hoàn tất nếu chỉ pull. Nhắc tôi khởi động lại Antigravity và
   mở phiên mới để kiểm tra danh sách skill.
```
