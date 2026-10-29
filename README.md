# antigravity-skill-os

Skill registry, workspace profiles, and installer for
[Google Antigravity](https://antigravity.google/).

**Ý tưởng cốt lõi:** skill được **phân loại**, mỗi project chỉ nhận đúng bộ nó cần.
Project web quản lý nhận design + code. Project giáo án nhận education + docs. Hai bên
không bao giờ thấy skill của nhau — không phải vì bị dặn đừng dùng, mà vì skill
**không tồn tại** trong workspace đó. Ponytail `full` thì luôn bật cho tất cả.

Repo **tự chứa**: 75 skill + 46 subagent + 9 plugin Claude Code đã port, pin commit.
Clone về là cài được, không cần mạng.

## Bắt đầu trong 3 lệnh

```bash
git clone <repo> antigravity-skill-os && cd antigravity-skill-os

python3 tools/install.py --core                                                # rules + 4 skill global
python3 tools/install.py --profile web-admin -w ~/p/admin --hooks --plugins    # đầy đủ
python3 tools/install.py --list                                                # xem đã cài gì
```

Có `--dry-run` cho mọi lệnh, `--uninstall` để gỡ, `--include-manual` để cài cả skill phải gọi bằng `/`.

## Hai tầng cài

| Tầng | Lệnh | Đích | Hiệu lực |
|---|---|---|---|
| Global | `--core` | `~/.gemini/AGENTS.md` + `~/.gemini/config/skills/` | Mọi project, mọi phiên, không cần `/` |
| Workspace | `--profile <id> -w <dir>` | `<dir>/.agents/skills/` + `.agents/agents/` | Cô lập cứng trong project đó |
| Hooks | `--hooks` | `<dir>/.agents/hooks.json` + `.agents/skill-os/` | SessionStart nhắc luật hệ thống |
| Plugins | `--plugins` | `<dir>/.agents/plugins/` | 9 plugin Claude Code đã port (23 skill) |

**Cô lập cứng:** mỗi project một `--profile`. Router loại toàn bộ skill không liên quan —
50 skill trong 73 bị loại khỏi workspace mobile. Muốn chắc chắn "folder design chỉ có skill
design" thì tách workspace, vì Antigravity **không** hỗ trợ skill theo sub-folder.

Skill `mode: manual` mặc định **không cài** — phải `--include-manual`, để danh sách
description trong workspace gọn lại.

## 8 profile

| Profile | Skill | Thành phần | Cho |
|---|---|---|---|
| `web-admin` | 28 | code 16, design 6, motion 6 | Dashboard, CRUD, SaaS |
| `landing` | 25 | code 8, design 6, motion 11 | Landing, marketing, portfolio |
| `mobile-app` | 17 | code 6, design 1, motion 10 | React Native, Expo, iOS/Android |
| `design-system` | 15 | design 5, motion 10 | UI kit, component library |
| `cli-tool` | 13 | code 13 | CLI, script, backend |
| `education-k12` | 19 | education 14, docs 5 | Giáo án phổ thông, đề kiểm tra |
| `education-language` | 11 | education 9, docs 2 | Trung tâm ngoại ngữ, gia sư |
| `docs-writer` | 6 | docs 5, design 1 | Báo cáo, thuyết trình, bảng tính |
| `meta` | — | meta | Nuôi chính hệ thống này (plugin-dev, hookify) |

Thêm profile = thêm 1 file JSON trong `profiles/`. Không sửa code.

## Vercel

10 skill từ 2 repo chính thức, **MIT**:

| Skill | Pack | Việc nó làm |
|---|---|---|
| `vercel-react-best-practices` | code | 70 rule React/Next.js, 8 nhóm, xếp theo tác động |
| `vercel-composition-patterns` | code | Compound component, render props, context, React 19 |
| `vercel-react-native-skills` | code | React Native + Expo, list performance, native module |
| `deploy-to-vercel` | code | Deploy; **mặc định preview**, trừ khi nói rõ production |
| `vercel-optimize` | code | Audit chi phí/hiệu năng trên project đã deploy, metrics-first |
| `vercel-cli-with-tokens` | code | CLI bằng token, không cần `vercel login` (manual) |
| `vercel-byoc` | code | Bring Your Own Cloud: function chạy trên AWS của bạn (manual) |
| `vercel-react-view-transitions` | motion | View Transition API native, không cần lib animation |
| `web-design-guidelines` | design | ~100 check a11y/UX — để **review** UI |
| `writing-guidelines` | design | Review copy/prose của trang |

Nguồn: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) @ `1a2c79d4`
(9 skill, nhóm chính thức: React / Vercel / Design) và
[vercel-labs/vercel-byoc](https://github.com/vercel-labs/vercel-byoc) (1 skill).

## Port từ Claude Code

9 plugin của Anthropic (Apache-2.0) đã chuyển sang định dạng Antigravity: **23 skill,
8 agent, 2 bộ hook**. Chi tiết + bảng ánh xạ ở
[docs/ported-from-claude-code.md](docs/ported-from-claude-code.md).

| Plugin | Cho ra |
|---|---|
| `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `code-review` | `/code-review` (multi-agent) |
| `feature-dev` | `/feature-dev` + 3 agent |
| `security-guidance` | cảnh báo bảo mật khi sửa file |
| `claude-md-management` | audit `AGENTS.md` |
| `plugin-dev` | 8 skill dạy viết plugin/skill/agent |
| `code-simplifier`, `mcp-server-dev`, `hookify` | đơn giản hoá code, dựng MCP, tạo hook |

Cộng thêm **`planning-with-files`** (MIT, 27k★ — repo đã native Antigravity) và
**`handoff`** (mình tự viết, vì mọi repo handoff đều không có license).

**Không port** — `context-mode` (Elastic License 2.0), `grill-me` và `taste-skill`
(không có license), `claude-mem` (là app Node, không phải skill). Lý do đầy đủ trong
tài liệu trên.

## Ngang Claude Code ở đâu

Đối chiếu đầy đủ: [docs/claude-code-parity.md](docs/claude-code-parity.md).

| Năng lực | Claude Code | Antigravity | |
|---|---|---|---|
| Skill / rules / subagent / hooks / plugin / slash | ✅ | ✅ | ngang |
| Hệ sinh thái nội dung | 15.000+ repo | nhỏ | **Claude Code thắng** |
| Điều phối đa agent | ✅ | ✅ `/boost` 3 tầng | **Antigravity nhỉnh** |
| Subagent workspace | — | `inherit` / `branch` / `share` | Antigravity |
| Agent → agent messaging | hạn chế | `send_message` theo ID | Antigravity |

**Đã port:** 46 subagent (VoltAgent, MIT) qua `tools/port_agents.py`, và 3 hook
(`SessionStart` bật sẵn, formatter + safety gate tắt sẵn).

> ⚠️ **Đính chính:** mình từng nói Antigravity không có lifecycle hook. **Sai** — docs
> 2.0 có 6 sự kiện hook. Quyết định khoá cứng ponytail `full` vẫn giữ, nhưng lý do đổi:
> không phải "không thể", mà là "không cần làm khác".

## Ponytail: FULL, khoá cứng

Luật hệ thống, không phải tuỳ chọn. `lite`, `ultra`, `off`, `/ponytail` đều **bị bỏ** —
không cài `argument-hint`, không dạy agent chuyển mức. Lý do: Antigravity không có
lifecycle hook nên mức không lưu qua lượt; chỉ cần tồn tại một mức khác là mức sẽ trôi.

Áp dụng cho mọi sản phẩm bàn giao — code, tài liệu, giáo án, slide, config.

## Ngôn ngữ

- **Skill, code, tên biến, comment, commit message: tiếng Anh** — model đọc chỉ dẫn tiếng
  Anh ổn định nhất, và giữ được diff sạch với upstream khi cập nhật.
- **Giao tiếp với bạn: tiếng Việt** — luật ở `core/AGENTS.md` §4, nạp mọi phiên.

## Cấu trúc

```
core/            rules always_on — ponytail FULL, skill-first, verify, language
registry/        skills.json (75) + agents.json (46) + plugins.json (9) + taxonomy.md
profiles/        9 kiểu project → skill + nhóm agent + plugin
packs/           72 skill đã vendor + VENDOR.json (sha256 từng cái)
agents/          46 subagent đã port sang định dạng Antigravity
plugins/         9 plugin Claude Code đã port (23 skill + 8 agent)
hooks/           hooks.json + session-start / format / safety
tools/route.py   xem router chọn gì (không cài)
tools/install.py cài app: skills + agents + plugins + hooks
tools/vendor.py  tải/cập nhật skill từ upstream, pin commit
tools/port_agents.py   chuyển subagent Claude Code → Antigravity
tools/port_plugins.py  chuyển plugin Claude Code → Antigravity
docs/            catalog + đối chiếu + nhật ký port
```

## Phân loại

Chi tiết ở [`registry/taxonomy.md`](registry/taxonomy.md). Bốn trục:

- `domain` — `code` · `design` · `motion` · `education` · `docs` · `meta`
- `phase` — `discover` · `plan` · `build` · `verify` · `review` · `ship`
- `artifact` — `web-ui` · `native-ui` · `code` · `document` · `slide` · `lesson` · `motion` · …
- `mode` — `system` (luôn bật) · `core` · `auto` · `manual` (phải `--include-manual`)

Thêm `families` (tách K-12 khỏi ngoại ngữ) và `forbid_domains` (loại cứng).

## Cập nhật skill từ upstream

```bash
python3 tools/vendor.py                 # tải lại toàn bộ theo registry
python3 tools/vendor.py --only code     # chỉ 1 pack
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
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | MIT | code, design, motion |
| [vercel-labs/vercel-byoc](https://github.com/vercel-labs/vercel-byoc) | MIT | code |
| [dh2211/edu-agents](https://github.com/dh2211/edu-agents) | MIT | education |
| [CristianHeyde/language-teaching-skills](https://github.com/CristianHeyde/language-teaching-skills) | MIT | education |
| [JayRHa/agent-skills](https://github.com/JayRHa/agent-skills) | MIT | education |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | MIT | 46 subagent (port) |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Apache-2.0 | 9 plugin (port) |
| [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | MIT | planning-with-files |

`vercel-labs/agent-skills` không có file `LICENSE` ở gốc, nhưng README mục *License* ghi
MIT và 4 SKILL.md tự khai `license: MIT`. Coi là MIT.

`core/AGENTS.md` phái sinh từ ponytail (`AGENTS.md` + `skills/ponytail/SKILL.md`),
đã sửa: bỏ mục Levels, khoá `full`, mở phạm vi sang sản phẩm phi code,
thêm §3 (phạm vi skill theo project) và §4 (ngôn ngữ).

## Tài liệu

- [registry/taxonomy.md](registry/taxonomy.md) — hệ phân loại và lý do
- [docs/skill-catalog.md](docs/skill-catalog.md) — danh mục đầy đủ, link + license
- [core/AGENTS.md](core/AGENTS.md) — core rules đang dùng
- [docs/claude-code-parity.md](docs/claude-code-parity.md) — đối chiếu năng lực
- [docs/ported-from-claude-code.md](docs/ported-from-claude-code.md) — port cái gì, bỏ cái gì, vì sao
- [packs/design/apple-design/PATCH.md](packs/design/apple-design/PATCH.md) — lưu ý riêng
