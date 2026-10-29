# Claude Code ↔ Antigravity: đối chiếu năng lực

Mục tiêu bạn đặt ra: *"biến Antigravity thành Claude Code thứ 2, hoặc mạnh hơn"*.

Câu trả lời thẳng: **không cần biến thành bản sao, vì Antigravity đã mạnh hơn ở một
trục và yếu hơn ở trục khác.** Việc đúng là port phần Antigravity thiếu, và khai thác
phần Antigravity có mà Claude Code không có.

---

## 0. Đính chính: mình đã nói sai một điều

Trước đó mình khẳng định *"Antigravity không có lifecycle hook, nên mức ponytail không
lưu qua lượt"*. **Sai.** Docs Antigravity 2.0 có hẳn trang Hooks với 6 sự kiện:

| Sự kiện | Chạy khi nào |
|---|---|
| `SessionStart` | Bắt đầu phiên, trước lượt gọi model đầu tiên |
| `PreToolUse` | Trước khi một tool chạy — sửa được, chặn được |
| `PostToolUse` | Sau khi tool xong |
| `PreInvocation` | Trước mỗi lượt gọi model |
| `PostInvocation` | Ngay sau mỗi lượt gọi model |
| `Stop` | Vòng thực thi kết thúc |

Đặt ở `.agents/hooks.json` (workspace), `~/.gemini/config/hooks.json` (global), hoặc
trong plugin. Có regex matcher trên tên tool.

Nguồn gốc sai: `INSTALL.md` của ponytail ghi *"No lifecycle hooks, so levels don't
persist"* — câu đó đúng với đường cài `agy plugin install` của **phiên bản CLI mà họ
kiểm**, không đúng với Antigravity App 2.0.

**Hệ quả:** quyết định "khoá cứng ponytail full" vẫn giữ nguyên — vì đó là điều bạn
muốn, và nó đơn giản hơn. Nhưng **lý do** đổi: không phải "không thể làm khác", mà là
"không cần làm khác". Nếu sau này muốn mức persist, đã có đường: `SessionStart` hook
đọc file cấu hình và inject system message.

---

## 1. Claude Code mạnh ở đâu

| Năng lực | Claude Code | Antigravity | Trạng thái |
|---|---|---|---|
| Skill (SKILL.md) | ✅ | ✅ cùng chuẩn mở | Ngang |
| Rules (CLAUDE.md) | ✅ | ✅ AGENTS.md, còn **theo từng thư mục** | Antigravity nhỉnh |
| Subagent | ✅ `.claude/agents/` | ✅ `.agents/agents/` + `mainAgent` | Ngang |
| Hooks | ✅ nhiều sự kiện | ✅ 6 sự kiện, cùng mô hình | Ngang |
| Plugin | ✅ marketplace lớn | ✅ `plugin.json` + skills/agents/rules/mcp/hooks | Ngang |
| Slash command | ✅ | ✅ tự sinh từ tên skill | Ngang |
| MCP | ✅ | ✅ | Ngang |
| **Hệ sinh thái** | 15.000+ repo, marketplace 314 plugin | nhỏ hơn nhiều | **Claude Code thắng** |
| Built-in `/deep-research` | ✅ | ❌ | Claude Code |
| Agent Teams | ✅ | ✅ `/teamwork-preview` | Ngang |

## 2. Antigravity mạnh hơn ở đâu

| Năng lực | Chi tiết |
|---|---|
| `/boost` | Orchestrator 3 tầng: `Orchestrator` → `DeepCoder` / `DeepInvestigator` → worker cô lập, có vòng kiểm chứng độc lập. Claude Code không có tương đương |
| Subagent workspace | `inherit` / `branch` (git worktree cách ly) / `share` — parent chọn cho từng subagent |
| `mainAgent` | Một subagent có thể **trở thành agent chính**, không chỉ được gọi |
| Built-in subagent | `research`, `browser` (sandbox trình duyệt thật), `self` |
| Model tier theo agent | `flash` / `pro` / `inherit` — rẻ cho việc nhẹ, mạnh cho việc khó |
| Rule theo thư mục | `AGENTS.md` ở bất kỳ sub-folder, cộng dồn, cụ thể thắng |
| Giao tiếp agent ↔ agent | `send_message` theo conversation ID, kể cả với **peer**, đọc được transcript của nhau |

Kết luận: ở tầng **điều phối đa agent**, Antigravity không thua Claude Code. Cái thiếu
là **kho nội dung** — và đó là thứ port được.

---

## 3. Đã port gì

### 3.1 Subagent — 46 agent

Nguồn: [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
(MIT, 26k★, 10 nhóm chức năng).

Chuyển đổi bằng `tools/port_agents.py`:

| | Claude Code | Antigravity |
|---|---|---|
| Tool | `Read, Write, Edit, Bash, Glob, Grep` | `view_file, write_to_file, replace_file_content, run_command, find_by_name, grep_search` |
| Model | `sonnet` / `opus` / `haiku` | `pro` / `pro` / `flash` |
| Vị trí | `.claude/agents/` | `.agents/agents/` |

**Quyết định an toàn quan trọng:** mặc định converter **không ghi `tools`**.
Docs Antigravity cảnh báo nguyên văn: *"Specifying an unmapped or misspelled tool name
in the `tools` list may cause the subagent process to hang during execution."*
Ghi danh sách tool sai = treo subagent. Nên agent thừa hưởng toolset của parent.
Muốn giới hạn thì `--tools strict`, tự chịu rủi ro.

Phân bổ theo profile: `web-admin` / `landing` 43 agent, `mobile-app` / `cli-tool` ~39,
`design-system` 10, `docs-writer` 3, `education-*` **0** (đúng — soạn giáo án không cần
agent `kubernetes-specialist`).

### 3.2 Hooks — 3 hook

| Hook | Sự kiện | Mặc định | Việc |
|---|---|---|---|
| `skill-os-session-start` | `SessionStart` | **BẬT** | Inject ~120 token nhắc ponytail full + skill-first + tiếng Việt. Lưới an toàn nếu rules bị cắt vì vượt 20k token |
| `skill-os-format-on-write` | `PostToolUse` | TẮT | Chạy prettier/ruff/gofmt/rustfmt sau khi ghi file, nếu project có |
| `skill-os-safety-gate` | `PreToolUse` | TẮT | Chặn `rm -rf /`, fork bomb, `mkfs`, `curl \| sh`, force-push main |

Bật bằng `"enabled": true` trong `.agents/hooks.json`.

### 3.3 Code intelligence (LSP) — 12 ngôn ngữ

Đây là khoảng cách lớn nhất còn lại, và nó không phải chuyện "thiếu skill".

Claude Code nhúng sẵn LSP client trong binary: agent gọi tới là có định nghĩa, tham
chiếu, hover, symbol. Antigravity chỉ nói **MCP**; language server chỉ nói **LSP**. Hai
giao thức khác nhau, nên phải có cầu.

12 plugin `*-lsp` trong `anthropics/claude-plugins-official` — kiểm bằng `git ls-tree -r`
— **chỉ có `README.md` + `LICENSE`**. Không `mcp_config.json`, không `mcpServers`. Toàn
bộ phần nối nằm trong binary Claude Code, không có gì để chuyển.

Đã thử dùng cầu có sẵn: `jonrad/lsp-mcp` (TS, chưa publish npm), `blackwell-systems/agent-lsp`
(Go), `bug-ops/mcpls` (Rust) — **cả ba đều phải build toolchain**. Không hợp với nguyên
tắc cài offline, không cần mạng.

Nên tự viết: `tools/lsp_bridge.py`, stdlib Python, 380 dòng.

```
Antigravity ──MCP──► lsp_bridge.py ──LSP──► typescript-language-server
                                    ├─────► pyright-langserver
                                    ├─────► gopls
                                    └─────► … 9 server còn lại
```

| Mặt | Chi tiết |
|---|---|
| Tool mở ra | `lsp_definition`, `lsp_references`, `lsp_hover`, `lsp_document_symbols`, `lsp_workspace_symbols` |
| Phụ thuộc | không — `subprocess` + `json` + `pathlib` |
| Framing | `Content-Length` hai chiều: LSP ở trong, MCP (JSON một dòng) ở ngoài |
| Đăng ký | `<ws>/.agents/mcp_config.json`, khoá `lsp-<lang>` |
| Cầu nằm ở đâu | chép vào `<ws>/.agents/lsp/lsp_bridge.py` — repo mất vẫn chạy |
| Thiếu server | cầu vẫn sống, trả câu hướng dẫn thay vì treo phiên |
| Test | `python3 tools/test_lsp_bridge.py` → **9/9** |

12 ngôn ngữ: TypeScript/JS, Python, Go, Rust, C/C++, C#, Java, Kotlin, Lua, PHP, Ruby,
Swift. Không chọn một cái — `--lsp` quét workspace và bật **tất cả** cái đang có mặt.

Đối chiếu: Claude Code gắn LSP cho ~10 ngôn ngữ nhưng **không cấu hình được** server
ngoài danh sách. Antigravity + repo này phủ 12 và thêm được bằng `registry/lsp.json`.

---

## 4. Không port được — và vì sao

| Thứ | Lý do |
|---|---|
| `Task`, `TodoWrite` tool | Antigravity dùng `invoke_subagent` + `manage_task`; không có todo list riêng cho agent |
| `/deep-research` | Của Claude Code, dùng orchestration script riêng — Antigravity có `/boost` thay thế |
| Marketplace `/plugin install` từ Claude | Định dạng `plugin.json` khác (`$schema` Antigravity chỉ cho `name` + `description`) |
| Một số hook event của Claude | Antigravity thiếu `Notification`, `SubagentStop`, `PreCompact` |
| Skill cần hook để persist state | Chạy được, nhưng phải viết lại hook theo schema Antigravity |
| 12 plugin `*-lsp` | Chỉ có README + LICENSE, config nằm trong binary Claude Code → **tự viết cầu LSP→MCP** (xong, xem §3.3) |

---

## 5. Những skill Claude Code nên thêm tiếp

Cập nhật sau khi port xong đợt 3. Danh sách **còn lại**:

| Ưu tiên | Skill / plugin | Nguồn | Vì sao đáng |
|---|---|---|---|
| 1 | **`wshobson/agents`** | 42k★, MIT | **92 plugin** đã ở đúng định dạng Antigravity (`skills/` + `agents/`). Nguồn lớn nhất chưa khai thác — đủ để nhân đôi số skill hiện có |
| 2 | **`grill-me`** | cộng đồng | Phỏng vấn ngược trước khi code, chống hiểu sai yêu cầu. **Kẹt license** — repo không có LICENSE |
| 3 | **`taste-skill`** | Leonxlnx | Design có "gu", dial variance/motion. **Kẹt license** — không có LICENSE |
| 4 | `context-mode` | mksglu | Bộ nhớ xuyên phiên. **Elastic License 2.0** — không vendor |
| 5 | `claude-mem` | cộng đồng | Apache-2.0 nhưng là **app Node** (sqlite + UI), không phải skill trần |

### Đã xong trong đợt 3

| Thứ | Tình trạng |
|---|---|
| `handoff` | ✅ tự viết (MIT) — mọi bản cộng đồng đều không có license |
| `planning-with-files` | ✅ vendor MIT, repo đã native Antigravity |
| `security-guidance` | ✅ port từ `claude-plugins-official` |
| `claude-md-management` | ✅ port |
| `hookify` | ✅ port |
| `code-review`, `feature-dev`, `commit-commands` | ✅ port |
| **LSP** | ✅ tự viết cầu — xem §3.3 |

---

## 6. Kết luận

- **Ngang**: skill, rules, subagent, hooks, plugin, slash command, **code intelligence (LSP)**.
- **Antigravity nhỉnh**: điều phối đa agent (`/boost`, workspace branch, agent-to-agent), rule theo thư mục.
- **Claude Code nhỉnh**: hệ sinh thái nội dung — và ta vừa port 46 agent + 9 plugin từ đó sang.
- **LSP**: Claude Code gắn cứng trong binary cho ~10 ngôn ngữ, không cấu hình được server
  ngoài danh sách. Bản ở đây phủ 12, mở rộng bằng `registry/lsp.json`, và cấu hình được.
- **"Mạnh hơn"** không đến từ việc copy thêm skill, mà từ: subagent chuyên biệt + hook
  chặn lỗi + cô lập theo profile + ponytail khoá cứng. Bốn thứ đó đã có.
