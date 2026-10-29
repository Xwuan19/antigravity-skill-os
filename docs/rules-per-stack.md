# Luật theo ngôn ngữ (`.agents/rules/`)

Skill phải **được chọn** mới chạy. Luật thì luôn chạy. Đó là lý do có tầng này: vài thứ
phải đúng ở *mọi* lần sửa code, không phụ thuộc agent có nhớ gọi skill hay không.

## Cài gì, ở đâu

```
<workspace>/.agents/rules/common.md     ← luôn cài
<workspace>/.agents/rules/<ngôn ngữ>.md ← chỉ khi dò thấy ngôn ngữ đó
```

Antigravity đọc rules theo thư mục: `AGENTS.md`, `.agents/AGENTS.md`,
`.agents/rules/*.md` ở bất kỳ cấp nào, và rule **cộng dồn** — thư mục cụ thể thắng.
Nên đây là tầng hẹp nhất, đúng chỗ nhất để nhét luật kỹ thuật.

Ngôn ngữ dò bằng đuôi file (`tools/skillselect.py: detect_stacks`) — từ **2 file** trở
lên mới tính, để một file lẻ không kéo cả bộ luật vào.

| File | Kích thước | Nội dung |
|---|---|---|
| `common.md` | ~1.1 KB | Sáu cổng, luật bằng chứng, phạm vi sửa |
| `<ngôn ngữ>.md` | ~0.7–1.1 KB | Viết thế nào, cấm gì, kiểm bằng lệnh nào |

14 ngôn ngữ: `python` `typescript` `go` `rust` `java` `kotlin` `csharp` `ruby` `php`
`swift` `cpp` `lua` `sql` `shell`.

Workspace Python thật: **2 file, ~2.1 KB**. Rẻ hơn nhiều so với việc nhét cả bộ
`python-strict` (skill, chỉ nạp khi cần) vào always-on.

## Vì sao không chép `rules/` của ECC

[`affaan-m/ECC`](https://github.com/affaan-m/ECC) có `rules/common` + 14 gói ngôn ngữ
cùng ý tưởng này, và là nguồn tham khảo — nhưng không chép được nguyên văn:

| Vấn đề | Hệ quả |
|---|---|
| Frontmatter `paths: ["**/*.go"]` | Cú pháp Claude Code; Antigravity dùng `trigger: always_on` |
| Nội dung generic (KISS, DRY, immutability) | Không phải chỗ khác biệt; đã nằm trong `common.md` |
| Trỏ tới skill của ECC (`golang-patterns`, `golang-testing`) | Repo này không có, hoặc có bản khác |
| Mỗi ngôn ngữ 5 file | Nạp 5 file always-on cho một ngôn ngữ là lãng phí ngân sách |

Nên luật ở đây viết theo **sáu cổng logic code** của repo, gộp một ngôn ngữ vào một file.

## Thêm ngôn ngữ mới

1. Tạo `rules/<tên>.md` với frontmatter:
   ```yaml
   ---
   trigger: always_on
   description: "Luật <ngôn ngữ>: …"
   ---
   ```
2. Tên file phải khớp tên stack trong `tools/skillselect.py: EXT_STACK`
   (thêm đuôi file vào `EXT_STACK` nếu là ngôn ngữ mới).
3. Không cần sửa `install.py` — nó tự thấy file và tự cài khi dò được stack đó.

Giữ mỗi file **dưới ~1.2 KB**. Đây là always-on, dài quá thì tốn ngân sách của mọi lượt.

## Ba thứ mỗi file ngôn ngữ phải có

| Mục | Câu hỏi nó trả lời |
|---|---|
| **Trước khi sửa** | Tìm chỗ nào bị ảnh hưởng bằng lệnh gì |
| **Không được** | 3–4 cái bẫy chết người của ngôn ngữ đó |
| **Kiểm chứng** | Lệnh chạy được để chứng minh là xong |

"Viết" ở giữa là phần phong cách — ngắn, chỉ những gì quyết định đúng/sai.

## Không đè file của bạn

`install.py` ghi danh sách file nó tạo vào `.agents/rules/.skill-os-rules.json`.
File nào đã có mà **không** nằm trong danh sách đó thì giữ nguyên và in cảnh báo —
luật riêng của bạn không bị ghi đè.

## Tắt

```bash
python3 tools/install.py --profile web-admin -w . --no-rules
bash bootstrap.sh web-admin ~/p/admin --no-rules
```

Chế độ `--system` **không** cài rules theo ngôn ngữ: lúc cài toàn máy chưa biết project
nào dùng ngôn ngữ gì. Tầng này chỉ có nghĩa ở phạm vi workspace.
