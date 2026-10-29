# antigravity-skill-os

Skill registry, workspace profiles, and installer for
[Google Antigravity](https://antigravity.google/).

**Ý tưởng cốt lõi:** skill được **phân loại**, mỗi project chỉ nhận đúng bộ nó cần.
Project web quản lý nhận design + code. Project giáo án nhận education + docs. Hai bên
không bao giờ thấy skill của nhau — không phải vì bị dặn đừng dùng, mà vì skill
**không tồn tại** trong workspace đó. Ponytail `full` thì luôn bật cho tất cả.

Repo **tự chứa**: 87 skill + 46 subagent + 9 plugin Claude Code đã port, pin commit.
Clone về là cài được, không cần mạng.

## Bắt đầu trong 3 lệnh

```bash
git clone <repo> antigravity-skill-os && cd antigravity-skill-os

python3 tools/install.py --core                                                # rules + 4 skill global
python3 tools/install.py --profile web-admin -w ~/p/admin --hooks --plugins    # đầy đủ
python3 tools/lsp.py --check                                                   # máy có language server nào
python3 tools/lsp.py -w ~/p/admin                                              # nối LSP vào MCP
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
| LSP | `--lsp` | `<dir>/.agents/mcp_config.json` + `.agents/lsp/` | code intelligence 12 ngôn ngữ qua MCP |

**Cô lập cứng:** mỗi project một `--profile`. Router loại toàn bộ skill không liên quan —
50 skill trong 73 bị loại khỏi workspace mobile. Muốn chắc chắn "folder design chỉ có skill
design" thì tách workspace, vì Antigravity **không** hỗ trợ skill theo sub-folder.

Skill `mode: manual` mặc định **không cài** — phải `--include-manual`, để danh sách
description trong workspace gọn lại.

## 9 profile

| Profile | Skill | Agent | LSP | Cho |
|---|---|---|---|---|
| `web-admin` | 41 | 43 | ✅ | Dashboard, CRUD, SaaS |
| `mobile-app` | 38 | 41 | ✅ | React Native, Expo, iOS/Android |
| `landing` | 26 | 43 | ✅ | Landing, marketing, portfolio |
| `cli-tool` | 26 | 41 | ✅ | CLI, script, backend |
| `education-k12` | 19 | — | — | Giáo án phổ thông, đề kiểm tra |
| `design-system` | 15 | 10 | ✅ | UI kit, component library |
| `education-language` | 11 | — | — | Trung tâm ngoại ngữ, gia sư |
| `docs-writer` | 6 | 3 | — | Báo cáo, thuyết trình, bảng tính |
| `meta` | 5 | 8 | ✅ | Nuôi chính hệ thống này (plugin-dev, hookify) |

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

## Logic code của Claude

Claude Code không giỏi vì có thêm một skill thần kỳ. Nó giỏi vì bị **chặn ở sáu cổng**
mà người ta hay đi tắt: *hiểu → tối giản → tái hiện → kiểm chứng → review → giao*.
Chi tiết và bảng ánh xạ: [docs/code-logic.md](docs/code-logic.md).

Đã port **12 skill** giữ các cổng đó:

| Skill | Giữ cổng gì | Từ chối điều gì |
|---|---|---|
| `karpathy-guidelines` | hiểu + tối giản | Code thừa, abstraction cho một lần dùng, "cải thiện" code bên cạnh |
| `root-cause` | tái hiện | Sửa khi chưa tái hiện; nới timeout / thêm retry cho bug biến mất |
| `parallel-debugging` | tái hiện | Đào một giả thuyết đến cùng rồi thiên kiến xác nhận |
| `test-gaps` | kiểm chứng | Đuổi % coverage; test không chứng minh được là nó fail được |
| `perf-hunt` | kiểm chứng | Tối ưu khi chưa có số trước |
| `triage-ci` | tái hiện | Làm xanh CI bằng cách tắt check |
| `review-diff` | review | Báo lỗi không kèm kịch bản hỏng cụ thể |
| `audit-security` | review | Liệt kê tên lỗ hổng thay vì nói ai chạm được, bằng input nào |
| `restructure` | tối giản | Tách file theo số dòng thay vì theo đường nối |
| `onboard-repo` | hiểu | Gọi thứ gì là "quy ước" khi chưa đếm |
| `ship-pr` | giao | Viết commit message từ trí nhớ |
| `bump-deps` | giao | Trộn major bump với refactor |

Nguồn: `tounsils/claude-code-skills` (MIT, 10 skill), `multica-ai/andrej-karpathy-skills`
(MIT, 226k★), `wshobson/agents` (MIT). Cộng với 15 skill `obra/superpowers` đã có từ trước —
trong đó `verification-before-completion` là `mode: core`, cài global nên workspace nào cũng có.

Skill logic đi theo **miền** chứ không theo artifact: `web-admin` 41, `mobile-app` 38,
`cli-tool` 26 đều nhận đủ 12. `landing` (logic mỏng) và `design-system` (ghi rõ "không cần
TDD") thì không.

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

## Code intelligence: LSP cho 12 ngôn ngữ

Claude Code có LSP gắn trong binary. Antigravity thì **nói MCP**, còn language server
thì nói **LSP** — hai giao thức khác nhau. Nên repo có một cầu nhỏ:

```
Antigravity  ──MCP (JSON/stdio)──►  tools/lsp_bridge.py  ──LSP (Content-Length)──►  gopls / pyright / jdtls / …
```

`lsp_bridge.py` chỉ dùng stdlib Python — không npm, không cargo, không pip. Nó mở 5 tool
cho agent: `lsp_definition`, `lsp_references`, `lsp_hover`, `lsp_document_symbols`,
`lsp_workspace_symbols`.

| Ngôn ngữ | Server | Cài |
|---|---|---|
| TypeScript / JavaScript / TSX | `typescript-language-server` | `npm i -g typescript-language-server typescript` |
| Python | `pyright-langserver` | `npm i -g pyright` |
| Go | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| Rust | `rust-analyzer` | `rustup component add rust-analyzer` |
| C / C++ | `clangd` | `apt install clangd` / `brew install llvm` |
| C# | `csharp-ls` | `dotnet tool install --global csharp-ls` |
| Java | `jdtls` | `brew install jdtls` |
| Kotlin | `kotlin-lsp` | `brew install JetBrains/utils/kotlin-lsp` |
| Lua | `lua-language-server` | `brew install lua-language-server` |
| PHP | `intelephense` | `npm i -g intelephense` |
| Ruby | `ruby-lsp` | `gem install ruby-lsp` |
| Swift | `sourcekit-lsp` | có sẵn trong Swift toolchain |

**Không cần chọn ngôn ngữ.** `--lsp` quét workspace, đếm file theo đuôi, đăng ký đúng
những server có mặt trên máy. Workspace đa ngôn ngữ thì nhiều server cùng lúc:

```bash
python3 tools/lsp.py --check                  # 12 dòng, cái nào thiếu thì in lệnh cài
python3 tools/lsp.py -w ~/p/mixed             # tự dò: ra python + go + typescript
python3 tools/lsp.py -w . --langs go,rust     # ép đăng ký, bỏ qua quét
python3 tools/lsp.py -w . --langs all         # đăng ký cả 12 (thiếu server sẽ báo)
python3 tools/lsp.py -w . --global            # ghi ~/.gemini/config/mcp_config.json
python3 tools/lsp.py -w . --remove            # gỡ lsp-*, giữ MCP server của bạn
```

Profile nào chạm code thì **tự bật**: `web-admin`, `landing`, `cli-tool`, `mobile-app`,
`design-system`, `meta`. `docs-writer` và 2 profile giáo dục thì tắt. Ghi đè bằng
`--lsp` / `--no-lsp`.

Cầu được **chép vào** `<ws>/.agents/lsp/lsp_bridge.py` và `mcp_config.json` trỏ vào bản
trong workspace — repo biến mất thì workspace vẫn chạy. Ghi vào `mcp_config.json` có sẵn
thì **merge**, server của bạn không bị xoá.

> Thiếu language server thì cầu vẫn sống và trả lời bằng câu hướng dẫn, không làm treo
> phiên. Đây là hành vi có test hồi quy.

## Ngang Claude Code ở đâu

Đối chiếu đầy đủ: [docs/claude-code-parity.md](docs/claude-code-parity.md).

| Năng lực | Claude Code | Antigravity | |
|---|---|---|---|
| Skill / rules / subagent / hooks / plugin / slash | ✅ | ✅ | ngang |
| Code intelligence (LSP: định nghĩa, tham chiếu, hover) | ✅ | ✅ 12 ngôn ngữ | ngang |
| Kỷ luật code (tái hiện trước, kiểm chứng trước khi nói xong) | ✅ trong binary | ✅ 12 skill + core | ngang |
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
registry/        skills.json (87) + agents.json (46) + plugins.json (9) + lsp.json (12) + taxonomy.md
profiles/        9 kiểu project → skill + nhóm agent + plugin
packs/           84 skill đã vendor + VENDOR.json (sha256 từng cái)
agents/          46 subagent đã port sang định dạng Antigravity
plugins/         9 plugin Claude Code đã port (23 skill + 8 agent)
hooks/           hooks.json + session-start / format / safety
tools/lsp_bridge.py    cầu LSP → MCP (stdlib, 5 tool)
tools/lsp.py           dò workspace, sinh mcp_config.json
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
- Antigravity **có** 6 lifecycle hook (`SessionStart`, `PreToolUse`, `PostToolUse`,
  `PreInvocation`, `PostInvocation`, `Stop`) — xem `hooks/hooks.json`. ponytail vẫn khoá
  cứng bằng rules `always_on`, hook chỉ là lưới an toàn.
- Antigravity **không tự cài** skill theo loại project — nó chỉ tự chọn trong số đã có.
  Vì vậy bước chọn phải tất định ở khâu cài (`install.py`), model chọn trong số đó mỗi lượt.
- MCP server nạp từ `<ws>/.agents/mcp_config.json` (workspace) và
  `~/.gemini/config/mcp_config.json` (global). Mỗi entry cần đúng **một** transport:
  `command` (stdio) hoặc `serverUrl` (HTTP).
- App còn có đường UI: **Settings → Customizations → Installed MCP Servers** (MCP Store).
  Ghi file là đường tất định, hợp với cài offline.
- Language server **không** phải MCP server — phải có cầu. `python3 tools/lsp.py --check`
  cho biết máy đang thiếu cái nào.
- `argparse` của cầu sẽ nuốt `--stdio` nếu không đặt sau `--`. Đây là bug thật đã gặp và
  đã có test hồi quy (`tools/test_lsp_bridge.py`).

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
| [tounsils/claude-code-skills](https://github.com/tounsils/claude-code-skills) | MIT | 10 skill kỷ luật kỹ thuật |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | MIT (README + frontmatter) | karpathy-guidelines |
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | parallel-debugging |
| language server (gopls, pyright, jdtls, …) | giấy phép riêng của từng server | **không vendor** — cài bằng trình quản lý gói của bạn |

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
- [docs/code-logic.md](docs/code-logic.md) — sáu cổng logic code, skill nào giữ cổng nào
- [packs/design/apple-design/SKILL.md](packs/design/apple-design/SKILL.md) — skill design gốc Apple, kèm LICENSE
