# Port từ Claude Code — cái gì vào, cái gì không, vì sao

Ghi lại toàn bộ quyết định khi port hệ sinh thái Claude Code sang Antigravity.
Đối chiếu năng lực ở [claude-code-parity.md](claude-code-parity.md).

---

## 1. Plugin — 9 cái, đã port

Nguồn: `anthropics/claude-plugins-official` @ `f8c5e7a1dc` (Apache-2.0).

| Plugin | Skill sinh ra | Agent | Hook |
|---|---|---|---|
| `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` | — | — |
| `code-review` | `/code-review` | — | — |
| `feature-dev` | `/feature-dev` | `code-architect`, `code-explorer`, `code-reviewer` | — |
| `security-guidance` | — | — | ✅ chuyển được |
| `claude-md-management` | 2 | — | — |
| `plugin-dev` | 8 | 3 | — |
| `code-simplifier` | — | 1 | — |
| `mcp-server-dev` | 3 | — | — |
| `hookify` | 5 | 1 | ✅ chuyển được |

**Tổng: 23 skill, 8 agent, 2 bộ hook.**

### Bảng ánh xạ khi chuyển

| Claude Code | Antigravity | Ghi chú |
|---|---|---|
| `.claude-plugin/plugin.json` | `plugin.json` ở gốc | Antigravity chỉ nhận `name` + `description` |
| `commands/<x>.md` | `skills/<x>/SKILL.md` | **Quan trọng nhất.** Antigravity tự sinh `/<x>` từ tên skill, nên command thành slash command mà không cần cơ chế riêng |
| `` !`git status` `` | mục "Dữ liệu cần thu thập" | Antigravity không có inline exec. Mình thu các lệnh lên đầu skill và thay chỗ cũ bằng `(output của \`git status\`)` để phần Context vẫn đọc hiểu |
| `allowed-tools: Bash(git add:*)` | bỏ | Không có pattern scope theo lệnh. Ghi chú trong skill |
| `tools: Read, Write, ...` | **bỏ trống có chủ ý** | Docs cảnh báo tên tool sai làm subagent **treo**. Agent thừa hưởng toolset parent |
| `model: sonnet/opus/haiku` | `pro` / `pro` / `flash` | |
| `hooks/hooks.json` dạng `{hooks:{...}}` | `{tên: {enabled, Event:[...]}}` | |
| `${CLAUDE_PLUGIN_ROOT}` | `${PLUGIN_ROOT}` | |
| `UserPromptSubmit` | `PreInvocation` | Gần nhất về ngữ nghĩa |
| `Notification`, `SubagentStop`, `PreCompact` | — | Antigravity không có, đã bỏ |

Hook port sang **mặc định `enabled: false`** — script bên trong gọi Python của Claude
Agent SDK, chưa chắc chạy trong Antigravity. Bật sau khi tự kiểm.

---

## 2. Skill cộng đồng — 2 cái

| Skill | Nguồn | License | Vì sao |
|---|---|---|---|
| `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) @ `5d29800b` | MIT | 27k★. **Repo này đã có sẵn `.agents/skills/`** — native Antigravity, chỉ cần copy. Plan ghi ra đĩa (`task_plan.md`, `findings.md`, `progress.md`), sống sót qua mất context |
| `handoff` | **tự viết** | MIT | Mọi repo handoff đều **không có license** → không được phép vendor. Viết bản riêng: `HANDOFF.md` 8 mục, có mục "Do not" ghi lại đường cụt đã thử |

`handoff` đặt `mode: core` → cài global, có mặt ở mọi phiên.

---

## 3. LSP — không port được, nên viết lại

12 plugin `*-lsp` của Anthropic (`pyright-lsp`, `gopls-lsp`, `rust-analyzer-lsp`, …) thoạt
nhìn giống thứ đáng port nhất: mỗi cái một ngôn ngữ, đúng nhu cầu "project đa dạng ngôn
ngữ". Nhưng đọc kỹ thì:

```
$ git ls-tree -r lsp/pyright-lsp
100644 README.md
100644 LICENSE
```

Hết. **Không `mcp_config.json`, không `mcpServers`, không `.lsp.json`.** Phần nối LSP nằm
trong binary Claude Code; plugin chỉ là tờ giấy ghi chú. Có thử 3 cầu LSP→MCP mã nguồn mở
(`lsp-mcp` TS chưa publish npm, `agent-lsp` Go, `mcpls` Rust) — cả ba đều phải build
toolchain, trái với nguyên tắc cài offline của repo.

Nên **tự viết** `tools/lsp_bridge.py` (stdlib, 380 dòng) + `tools/lsp.py` (dò và đăng ký).

| Thành phần | Vai trò |
|---|---|
| `tools/lsp_bridge.py` | một tiến trình: ngoài là MCP server stdio, trong giữ language server LSP. 5 tool. |
| `tools/lsp.py` | quét workspace theo đuôi file → sinh `<ws>/.agents/mcp_config.json` |
| `registry/lsp.json` | 12 ngôn ngữ: `command`, `args`, `ext`, `install`, `mcp_name` |
| `tools/test_lsp_bridge.py` | LSP server giả, **9/9 assertion** |

Ánh xạ so với Claude Code:

| Claude Code | Ở đây |
|---|---|
| LSP client trong binary | `tools/lsp_bridge.py` gọi qua MCP |
| Plugin `*-lsp` (chỉ README) | `registry/lsp.json`, 12 entry có lệnh cài thật |
| Tự bật khi thấy file | `tools/lsp.py` đếm file rồi đăng ký |
| ~10 ngôn ngữ cố định | 12, mở rộng bằng cách thêm entry vào `registry/lsp.json` |

## 4. Không port — và lý do

| Thứ | Lý do | Nên làm gì |
|---|---|---|
| **`mksglu/context-mode`** (32k★) | **Elastic License 2.0**, không phải open source. ELv2 cấm cung cấp như dịch vụ và cấm gỡ license key | Tự cài riêng nếu cần, không vendor vào repo này |
| **`RobMitt/grill-me-skill`** (1.2k★) | **Không có license** = giữ toàn bộ bản quyền. Vendor là vi phạm | Có thể tự viết bản tương đương: skill phỏng vấn ngược trước khi code |
| **`thedotmack/claude-mem`** (104k★, Apache-2.0) | License ổn, nhưng là **ứng dụng Node hoàn chỉnh** (794 file `src/`, sqlite, UI, hooks gọi service). Không phải skill — phải cài như app riêng | Cài độc lập theo README của họ; `plugin/skills/*` thì chép tay được |
| **`wshobson/agents`** (42k★, MIT) | 92 plugin — quá lớn để vendor toàn bộ, và phần lớn trùng với 46 agent đã port | **Chưa quyết.** Lấy lẻ từng plugin khi cần |
| Bộ LSP (`typescript-lsp`, `pyright-lsp`, ...) | Plugin **rỗng** — chỉ README + LICENSE, không config. Xem §3: đã tự viết cầu và phủ cả 12 ngôn ngữ | — (đã xong) |
| `/deep-research` | Là workflow của Claude Code, không phải skill | Antigravity có `/boost` thay thế |
| `taste-skill` | Repo phổ biến nhất **không có license** | Tự viết hoặc dùng `frontend-design` + `apple-design` đã có |

---

## 5. Cách dùng

```bash
# xem có plugin gì
python3 tools/port_plugins.py --list

# cài cho 1 project, kèm agent + hook + plugin + LSP
python3 tools/install.py --profile web-admin -w ~/p/admin --hooks --plugins --lsp

# riêng tầng LSP
python3 tools/lsp.py --check                     # máy đã cài server nào
python3 tools/lsp.py -w ~/p/admin                # tự dò ngôn ngữ trong project
```

Kết quả trong workspace:

```
.agents/
├── skills/     29 skill
├── agents/     43 subagent
├── plugins/    6 plugin (7 skill bên trong)
├── hooks.json
├── skill-os/   3 script hook
├── lsp/        lsp_bridge.py (cầu LSP → MCP)
└── mcp_config.json   server lsp-* đang bật
```

Plugin **mặc định không cài** (cần `--plugins`) vì mỗi plugin thêm vài dòng description
vào danh sách skill — nhiều quá thì model chọn sai.

## 6. Tái tạo

```bash
python3 tools/port_plugins.py --all              # 9 plugin, pin đúng commit
python3 tools/port_agents.py --all               # 46 subagent
python3 tools/vendor.py --check                  # kiểm sha256 toàn bộ skill
python3 tools/test_lsp_bridge.py                 # 9/9 — cầu LSP vẫn đúng
```
