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

---

## 4. Không port được — và vì sao

| Thứ | Lý do |
|---|---|
| `Task`, `TodoWrite` tool | Antigravity dùng `invoke_subagent` + `manage_task`; không có todo list riêng cho agent |
| `/deep-research` | Của Claude Code, dùng orchestration script riêng — Antigravity có `/boost` thay thế |
| Marketplace `/plugin install` từ Claude | Định dạng `plugin.json` khác (`$schema` Antigravity chỉ cho `name` + `description`) |
| Một số hook event của Claude | Antigravity thiếu `Notification`, `SubagentStop`, `PreCompact` |
| Skill cần hook để persist state | Chạy được, nhưng phải viết lại hook theo schema Antigravity |

---

## 5. Những skill Claude Code nên thêm tiếp

Đây là danh sách **chưa port**, xếp theo giá trị:

| Ưu tiên | Skill / plugin | Nguồn | Vì sao đáng |
|---|---|---|---|
| 1 | **handoff** | cộng đồng | Nén phiên thành 1 file markdown để tiếp tục phiên mới. Bù đúng chỗ context bị compact |
| 2 | **grill-me** | cộng đồng | Phỏng vấn ngược trước khi viết code — chống hiểu sai yêu cầu |
| 3 | **planning-with-files** | cộng đồng | Plan ghi ra file, sống sót khi mất context |
| 4 | **context-mode** / **claude-mem** | mksglu / cộng đồng | Bộ nhớ xuyên phiên — Claude Code không có sẵn, Antigravity cũng không |
| 5 | **commit-commands** | `claude-plugins-official` | Commit + PR nhất quán |
| 6 | **security-guidance** | `claude-plugins-official` | Cảnh báo bảo mật khi sửa file, review diff lúc Stop |
| 7 | **claude-md-management** | `claude-plugins-official` | Audit và dọn `AGENTS.md` khi nó phình |
| 8 | **hookify** | `claude-plugins-official` | Biến câu "từ giờ luôn..." thành hook thật |
| 9 | **code-review** (multi-agent) | `claude-plugins-official` | Review song song nhiều agent + chấm độ tin cậy |
| 10 | **LSP plugins** | `anthropics/claude-plugins-official` | Code intelligence theo ngôn ngữ — Antigravity không có |
| 11 | **taste-skill** | Leonxlnx | Design có "gu", dial chỉnh variance/motion |
| 12 | **wshobson/agents** | 42k★, MIT | **92 plugin** đã đóng gói sẵn skills + agents — nguồn lớn nhất chưa khai thác |

Ưu tiên 1–4 là thứ bù đúng điểm yếu lớn nhất của cả hai: **mất context giữa phiên**.

---

## 6. Kết luận

- **Ngang**: skill, rules, subagent, hooks, plugin, slash command.
- **Antigravity nhỉnh**: điều phối đa agent (`/boost`, workspace branch, agent-to-agent), rule theo thư mục.
- **Claude Code nhỉnh**: hệ sinh thái nội dung — và ta vừa port 46 agent từ đó sang.
- **"Mạnh hơn"** không đến từ việc copy thêm skill, mà từ: subagent chuyên biệt + hook
  chặn lỗi + cô lập theo profile + ponytail khoá cứng. Bốn thứ đó đã có.
