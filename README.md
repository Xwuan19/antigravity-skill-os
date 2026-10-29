# antigravity-skill-os

Skill registry, workspace profiles, and installer for
[Google Antigravity](https://antigravity.google/).

**Ý tưởng cốt lõi:** skill được **phân loại**, mỗi project chỉ nhận đúng bộ nó cần.
Project web quản lý nhận design + code. Project giáo án nhận education + docs. Hai bên
không bao giờ thấy skill của nhau — không phải vì bị dặn đừng dùng, mà vì skill
**không tồn tại** trong workspace đó. Ponytail `full` thì luôn bật cho tất cả.

Repo **tự chứa**: toàn bộ 63 skill đã vendor, pin commit. Clone về là cài được, không cần mạng.

## Bắt đầu trong 3 lệnh

```bash
git clone <repo> antigravity-skill-os && cd antigravity-skill-os

python3 tools/install.py --core                                  # rules + 3 skill global
python3 tools/install.py --profile web-admin -w ~/projects/admin # skill cho 1 project
python3 tools/install.py --list                                  # xem đã cài gì
```

Có `--dry-run` cho mọi lệnh, và `--uninstall` để gỡ sạch.

## Hai tầng cài

| Tầng | Lệnh | Đích | Hiệu lực |
|---|---|---|---|
| Global | `--core` | `~/.gemini/AGENTS.md` + `~/.gemini/config/skills/` | Mọi project, mọi phiên, không cần `/` |
| Workspace | `--profile <id> -w <dir>` | `<dir>/.agents/skills/` | Cô lập cứng trong project đó |

**Cô lập cứng:** chọn `--profile` khác nhau cho từng project. Router xoá cả 38 skill
không liên quan khỏi workspace web. Muốn chắc chắn "folder design chỉ có skill design"
thì tách workspace — vì Antigravity **không** hỗ trợ skill theo sub-folder.

## 7 profile

| Profile | Skill | Thành phần | Cho |
|---|---|---|---|
| `web-admin` | 25 | code 13, design 7, motion 5 | Dashboard, CRUD, SaaS |
| `landing` | 22 | code 5, design 7, motion 10 | Landing, marketing, portfolio |
| `design-system` | 16 | design 6, motion 10 | UI kit, component library |
| `cli-tool` | 11 | code 11 | CLI, script, backend |
| `education-k12` | 19 | education 14, docs 5 | Giáo án phổ thông, đề kiểm tra |
| `education-language` | 11 | education 9, docs 2 | Trung tâm ngoại ngữ, gia sư |
| `docs-writer` | 7 | docs 5, design 2 | Báo cáo, thuyết trình, bảng tính |

Thêm profile = thêm 1 file JSON trong `profiles/`. Không sửa code.

## Ponytail: FULL, khoá cứng

Luật hệ thống, không phải tuỳ chọn. `lite`, `ultra`, `off`, `/ponytail` đều **bị bỏ** —
không cài `argument-hint`, không dạy agent chuyển mức. Lý do: Antigravity không có
lifecycle hook nên mức không lưu qua lượt; chỉ cần tồn tại một mức khác là mức sẽ trôi.

Áp dụng cho mọi sản phẩm bàn giao — code, tài liệu, giáo án, slide, config.

## Ngôn ngữ

- **Skill, code, tên biến, comment, commit message: tiếng Anh** — model đọc chỉ dẫn tiếng
  Anh ổn định nhất, và giữ được diff sạch với upstream khi cập nhật.
- **Giao tiếp với bạn: tiếng Việt** — ghi thành luật trong `core/AGENTS.md` §4, nạp mọi phiên.

## Cấu trúc

```
core/            rules always_on — ponytail FULL, skill-first, verify, language
registry/        skills.json (66 skill, 4 trục) + taxonomy.md
profiles/        7 kiểu project → tập skill
packs/           63 skill đã vendor + VENDOR.json (sha256 từng cái)
tools/route.py   chọn & cài skill vào workspace
tools/install.py cài vào Antigravity App (~/.gemini) + workspace
tools/vendor.py  tải/cập nhật skill từ upstream, pin commit
docs/            catalog để duyệt
```

## Phân loại

Chi tiết ở [`registry/taxonomy.md`](registry/taxonomy.md). Bốn trục:

- `domain` — `code` · `design` · `motion` · `education` · `docs` · `meta`
- `phase` — `discover` · `plan` · `build` · `verify` · `review` · `ship`
- `artifact` — `web-ui` · `code` · `document` · `slide` · `lesson` · `native-ui` · …
- `mode` — `system` (luôn bật) · `core` · `auto` · `manual`

Thêm `families` (tách K-12 khỏi ngoại ngữ) và `forbid_domains` (loại cứng).

## Cập nhật skill từ upstream

```bash
python3 tools/vendor.py                 # tải lại toàn bộ theo registry
python3 tools/vendor.py --only design   # chỉ 1 pack
python3 tools/vendor.py --check         # kiểm sha256, phát hiện sửa tay
```

Mỗi bản ghi trong `packs/VENDOR.json` có `source` (repo@commit), `sha256`, `bytes`.

## Ghi chú kỹ thuật đã xác nhận

- Skill **chỉ** có phạm vi workspace-root và global — không có skill theo sub-folder.
  Nên "mỗi folder một bộ skill" phải làm bằng **tách workspace**, không bằng sub-folder.
- Rule **có** phạm vi theo thư mục bất kỳ, và là cộng dồn (global + workspace + directory).
- Plugin là global và nạp **toàn bộ** thư mục con của `skills/` → phải tách plugin theo pack.
- Ngân sách: 20.000 token cho global + `always_on`; 24 KB mỗi file rule; description ≤ 1024 ký tự.
- Antigravity **không** có lifecycle hook → mọi cơ chế "mức/phím tắt" sẽ trôi giữa các lượt.
- Antigravity **không tự cài** skill theo loại project — nó chỉ tự chọn trong số đã có.
  Vì vậy bước chọn phải tất định ở khâu cài (`install.py`), model chọn trong số đó mỗi lượt.

## Nguồn và license

| Repo | License | Pack |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 (từng skill) | design, docs, meta, code |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | MIT | motion (cả 14) |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | code, meta |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | core |
| [dh2211/edu-agents](https://github.com/dh2211/edu-agents) | MIT | education |
| [CristianHeyde/language-teaching-skills](https://github.com/CristianHeyde/language-teaching-skills) | MIT | education |
| [JayRHa/agent-skills](https://github.com/JayRHa/agent-skills) | MIT | education |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | ⚠ repo không khai license | code, design |

`core/AGENTS.md` phái sinh từ ponytail (`AGENTS.md` + `skills/ponytail/SKILL.md`),
đã sửa: bỏ mục Levels, khoá `full`, mở phạm vi sang sản phẩm phi code,
thêm §3 (phạm vi skill theo project) và §4 (ngôn ngữ).

## Tài liệu

- [registry/taxonomy.md](registry/taxonomy.md) — hệ phân loại và lý do
- [docs/skill-catalog.md](docs/skill-catalog.md) — danh mục đầy đủ, link + license
- [core/AGENTS.md](core/AGENTS.md) — core rules đang dùng
- [packs/design/apple-design/PATCH.md](packs/design/apple-design/PATCH.md) — lưu ý riêng
