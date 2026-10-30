# Lọc skill của `NousResearch/hermes-agent`

Repo này **không phải** kho skill. Nó là một agent runtime: 60.738 commit, TUI, desktop,
gateway, ACP adapter, providers, MCP. `skills/` là phần **phụ** của runtime đó.

Nhưng câu hỏi đúng là: trong 44 skill đó, cái nào là *hướng dẫn viết/vẽ/làm* thuần, cái nào
là *lớp mỏng gọi tool riêng của Hermes*? Lọc ra được — dưới đây là cách làm và kết quả.

## Cách lọc

Ba vòng, mỗi vòng loại một loại phụ thuộc:

| Vòng | Tìm gì | Loại cái gì |
|---|---|---|
| 1. Regex runtime | `hermes <cmd>`, `$HERMES_HOME`, `spawn_subagent`, `kanban`, `session_id` | Skill điều khiển chính Hermes |
| 2. Quét lệnh trong code fence | lệnh ngoài danh sách chuẩn (`python`, `node`, `git`, `curl`…) | Skill cần CLI lạ: `remindctl`, `memo`, `imsg`, `himalaya`, `xurl`, `peekaboo`, `cua-driver` |
| 3. Đọc tay phần còn lại | tool name trong thân bài (`view_file`, `web_extract`…), API key, MCP riêng | Skill chạy được nhưng phải **vá** |

Kết quả: 44 → **10 giữ**, 34 loại.

## 10 cái đã lấy

| Skill | Pack | Vì sao đáng |
|---|---|---|
| `humanizer` | docs | 34 KB, MIT, dựa trên *Signs of AI writing* của Wikipedia. 29 mẫu nhận diện + ví dụ trước/sau. Bộ chống văn AI tốt nhất tìm được |
| `popular-web-designs` | design | 54 design system thật (Stripe, Linear, Vercel, Airbnb…) kèm template HTML/CSS từng cái |
| `grounded-citations` | docs | Ledger `url → [n]`, quote nguyên văn, `verify` bản nháp. Trích dẫn kiểm được, không phải "nguồn: Google" |
| `baoyu-infographic` | design | 21 layout × 21 style + framework phân tích. Của 宝玉 (JimLiu) |
| `architecture-diagram` | design | Sơ đồ kiến trúc SVG nền tối, xuất HTML, có template |
| `spike` | code | Thí nghiệm vứt đi để kiểm ý trước khi xây. Bổ trợ cổng *tái hiện* |
| `meeting-action-items` | docs | Biên bản họp → quyết định có trích dẫn, owner, ticket |
| `document-to-action-items` | docs | Tài liệu dài → nghĩa vụ, deadline, việc phải làm |
| `weekly-review-planning` | docs | Cam kết nào treo, việc nào kẹt, tuần sau làm gì |
| `codebase-inspection` | code | Đo LOC, tỉ lệ ngôn ngữ, code vs comment bằng `pygount` |

## Đã vá gì

Không chép nguyên văn. Bảng vá (áp tự động qua `vendor.py --patch`):

| Của Hermes | Thay bằng |
|---|---|
| `read_file` | `view_file` |
| `write_file` | `write_to_file` |
| `patch` | `replace_file_content` |
| `skill_view(name=…, file_path=…)` | `view_file("templates/…")` cạnh SKILL.md |
| `web_search` / `web_extract` / `browser_exec` | "search" / "page fetch" / `run_command` |
| `terminal` | `run_command` |
| `$HERMES_HOME/cache/citations/ledger.json` | `~/.gemini/cache/citations/ledger.json` |
| `~/.hermes/skills/…/scripts/sources.py` | `<thư mục chứa SKILL.md>/scripts/sources.py` |
| `hermes skills install official/…` | bỏ (không có kho đó ở đây) |
| đoạn "If the user has the full GSD system installed" | bỏ |

Còn lại chữ "Hermes" chỉ ở dòng `author:` và metadata — giữ để đúng nguồn gốc.

## 34 cái đã loại

| Nhóm | Skill | Lý do |
|---|---|---|
| Điều khiển Hermes | `hermes-agent`, `computer-use`, `sdlc-review`, `dogfood` | Gọi tool nội bộ: `hermes pm`, `cua-driver`, `kanban`, `screenshot` |
| CLI riêng của macOS | `apple-notes`, `apple-reminders`, `imessage`, `findmy` | Cần `memo`, `remindctl`, `imsg`, `peekaboo` — không có trên máy thường |
| OAuth / API trả phí | `google-workspace`, `teams-meeting-pipeline`, `xurl`, `himalaya`, `product-price-monitor`, `competitor-news-monitor` | Cần tài khoản, key, hoặc subscription |
| Dịch vụ ngoài | `maps`, `arxiv`, `youtube-content`, `obsidian` | Cần OSM/OSRM, API arXiv, transcript, vault Obsidian |
| Uỷ thác agent khác | `claude-code` (35 KB), `codex`, `simplify-code`, `requesting-code-review` | Điều phối fleet 4 agent của Claude/Codex; Antigravity có `invoke_subagent` nhưng luồng khác hẳn |
| Trùng skill đã có | `test-driven-development`, `systematic-debugging`, `pdf` | Đã có bản từ `obra/superpowers` và `anthropics/skills` |
| Nặng thư viện | `manim-video`, `ascii-video`, `p5js` | Cần manim / ffmpeg / p5 + CDN; giá trị thấp so với `canvas-design` đang có |
| Trùng địa hạt | `claude-design` | `ui-ux-pro-max` + `web-artifacts-builder` đã phủ, và bản này gắn workflow Hermes |
| Niche | `songwriting-and-ai-music`, `email-inbox-triage`, `blocked-page-recovery`, `spike`-adjacent | Quá hẹp, hoặc chỉ có nghĩa trong bối cảnh có tool tương ứng |

## Bài học cho lần sau

Muốn biết một repo có phải "kho skill" hay không, đừng đọc README — đếm tỉ lệ:

```bash
grep -rl "hermes \|HERMES_HOME\|spawn_subagent" skills/*/*/SKILL.md | wc -l
```

Repo này: 9/44 skill chạm runtime trực tiếp, 25/44 cần dịch vụ ngoài. Chỉ 10/44 là hướng
dẫn thuần. Tỉ lệ đó nói đúng bản chất repo hơn mọi mô tả.
