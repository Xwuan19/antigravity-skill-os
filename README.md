# antigravity-skill-os

Personal skill registry, scoped workspace profiles, and bootstrapper for
[Google Antigravity](https://antigravity.google/).

**Ý tưởng cốt lõi:** skill được **phân loại**, và mỗi project chỉ nhận đúng bộ skill
nó cần. Project web quản lý nhận design + code. Project giáo án nhận education + docs.
Hai bên không bao giờ thấy skill của nhau — không phải vì bị dặn, mà vì skill không có
trong workspace. Ponytail `full` thì luôn bật cho tất cả.

## Trạng thái

| | |
|---|---|
| Core rules (ponytail FULL + skill-first + verify) | ✅ [`core/AGENTS.md`](core/AGENTS.md) |
| Registry phân loại, 59 skill | ✅ [`registry/skills.json`](registry/skills.json) |
| Router chọn/cài skill | ✅ [`tools/route.py`](tools/route.py) · đã test |
| 7 profile project | ✅ [`profiles/`](profiles) · đã test |
| Skill vendored (pin commit) | ✅ frontend-design, apple-design |
| Installer cho toàn bộ skill | ✅ `--install`, sparse-clone đúng commit |

## Nhanh: một lệnh

```bash
python3 tools/route.py --list-profiles                      # 7 kiểu project
python3 tools/route.py --profile web-admin                  # xem chọn gì, chưa cài
python3 tools/route.py --profile web-admin --install ~/p/admin   # cài thật
```

Output cho `web-admin`: 22 skill (design + code), **0 skill giáo dục**, 34 skill bị loại.
Output cho `education-k12`: 19 skill, **0 skill code**, 0 skill motion.

## Cài core rules

Chọn **một**, không cài cả hai:

```bash
cp core/AGENTS.md ~/.gemini/AGENTS.md                                   # đầy đủ: ponytail + skill-first + verify + routing
cp core/rules/ponytail-full.md ~/.gemini/config/rules/                  # chỉ ponytail, dạng module
```

| Surface | Global rules | Global skills |
|---|---|---|
| App / IDE | `~/.gemini/AGENTS.md`, `~/.gemini/config/rules/` | `~/.gemini/config/skills/` |
| CLI | như trên | `~/.gemini/antigravity-cli/skills/` |

## Cấu trúc

```
core/           rules always_on — ponytail FULL, skill-first, verify
registry/       skills.json (phân loại) + taxonomy.md (cách phân loại)
profiles/       7 kiểu project → tập skill
packs/          skill đã vendor, pin commit
tools/route.py  router: profile → danh sách skill → cài vào workspace
docs/           catalog để duyệt
```

## Phân loại

Mỗi skill khai 4 trục — chi tiết ở [`registry/taxonomy.md`](registry/taxonomy.md):

- `domain` — `code` · `design` · `motion` · `education` · `docs` · `meta`
- `phase` — `discover` · `plan` · `build` · `verify` · `review` · `ship`
- `artifact` — `web-ui` · `code` · `document` · `slide` · `lesson` · …
- `mode` — `system` (luôn bật) · `core` · `auto` · `manual`

Thêm `families` để tách K-12 khỏi dạy ngoại ngữ, và `forbid_domains` để loại cứng.

## Ponytail: FULL, không có mức khác

Luật hệ thống, không phải tuỳ chọn. `lite`, `ultra`, `off`, `/ponytail` đều bị bỏ —
không cài `argument-hint`, không dạy agent chuyển mức. Lý do: Antigravity không có
lifecycle hook nên mức không lưu qua lượt; chỉ cần tồn tại một mức khác là mức sẽ trôi.

## Tài liệu

- [registry/taxonomy.md](registry/taxonomy.md) — hệ phân loại và lý do
- [docs/skill-catalog.md](docs/skill-catalog.md) — danh mục để duyệt, có link + license
- [core/AGENTS.md](core/AGENTS.md) — core rules
- [core/rules/ponytail-full.md](core/rules/ponytail-full.md) — biến thể module
- [packs/design/apple-design/PATCH.md](packs/design/apple-design/PATCH.md) — lưu ý về skill này

## Tham chiếu chính thức

- Skills: <https://antigravity.google/docs/skills>
- Rules: <https://antigravity.google/docs/rules/>
- Plugins: <https://antigravity.google/docs/plugins>
- Agent Skills spec: <https://agentskills.io/home>

## Ghi chú kỹ thuật đã xác nhận

- Skill **chỉ** có phạm vi workspace-root và global — không có skill theo sub-folder.
  Nên "mỗi folder một bộ skill" phải làm bằng tách workspace, không bằng sub-folder.
- Rule **có** phạm vi theo thư mục bất kỳ, và là cộng dồn (global + workspace + directory).
- Plugin là global và nạp **toàn bộ** thư mục con của `skills/` → phải tách plugin theo pack.
- Ngân sách: 20.000 token cho global + `always_on`; 24 KB mỗi file rule; description ≤ 1024 ký tự.
- Antigravity **không** có lifecycle hook → mọi cơ chế "mức/phím tắt" sẽ trôi giữa các lượt.
- Antigravity **không tự cài** skill theo loại project — nó chỉ tự chọn trong số đã có.
  Vì vậy bước chọn phải tất định ở khâu cài (`route.py`), còn model chọn trong số đó mỗi lượt.

## Nguồn

| Repo | License | Dùng cho |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 (từng skill) | frontend-design, docs suite, meta |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | MIT | apple-design, motion pack |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | code workflow |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | core rule |
| [dh2211/edu-agents](https://github.com/dh2211/edu-agents) | MIT | education K-12 |
| [CristianHeyde/language-teaching-skills](https://github.com/CristianHeyde/language-teaching-skills) | MIT | education language |
| [JayRHa/agent-skills](https://github.com/JayRHa/agent-skills) | MIT | learning, general |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | ⚠ repo không khai license | react, web guidelines |

`core/AGENTS.md` phái sinh từ ponytail (`AGENTS.md` + `skills/ponytail/SKILL.md`),
đã sửa: bỏ mục Levels, khoá `full`, mở phạm vi sang sản phẩm phi code.
