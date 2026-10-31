# antigravity-skill-os

Skill registry, workspace profiles, and installer for
[Google Antigravity](https://antigravity.google/).

**Ý tưởng cốt lõi:** skill được **phân loại**, mỗi project chỉ nhận đúng bộ nó cần.
Project web quản lý nhận design + code. Project giáo án nhận education + docs. Hai bên
không bao giờ thấy skill của nhau — không phải vì bị dặn đừng dùng, mà vì skill
**không tồn tại** trong workspace đó. Ponytail `full` thì luôn bật cho tất cả.

Repo **tự chứa**: 253 skill + 46 subagent + 9 plugin Claude Code, pin commit.
Clone về là cài được, không cần mạng. Kết quả khảo sát và kiểm tra các nguồn vibe coding:
[docs/vibe-coding-review.md](docs/vibe-coding-review.md).

## Hai cách dùng — chọn theo mục tiêu

| | **Global mỏng + rót theo project** (khuyến nghị) | **Toàn bộ máy** |
|---|---|---|
| Lệnh | `bootstrap.sh --core --prune` rồi `bootstrap.sh auto <dir>` mỗi project | `bootstrap.sh --system` |
| Project của bạn thấy | đúng skill của nó: 20–171 | **tất cả 186**, kể cả skill không liên quan |
| Ngân sách một phiên | btvn 22%, slide 18%, landing 36%, cli-tool 78%, web-admin 95% (cắt bớt pack được) | **103% → Antigravity tự loại ~10 skill** |
| Việc phải làm | một lệnh cho mỗi project mới | không làm gì |
| Cô lập domain | có — skill ngoài domain **không có trên đĩa** | không — project giáo dục vẫn thấy `springboot-*` |

Global và project **cộng dồn** và Antigravity không cho project ẩn skill global. Nên muốn "project
nào dùng skill nấy" thì global phải mỏng đúng 4 skill — đó là toàn bộ lý do tồn tại của `--core`.

### Global mỏng + rót theo project

```bash
bash bootstrap.sh --core --prune        # global: rules + 4 skill (≈ 10% ngân sách)
bash bootstrap.sh auto  ~/p/btvn         # tự dò profile rồi rót
bash bootstrap.sh auto  ~/p/SlidePPT
bash bootstrap.sh auto  ~/p/web-shop
```

`auto` đọc nội dung thư mục — `giao-an.docx`/tên thư mục → `education-k12`, `.pptx` → `docs-writer`,
`tauri.conf.json` → `desktop-app`, `react-native` trong `package.json` → `mobile-app`, `.py` không
frontend → `cli-tool`, `next`/`.tsx` → `web-admin`. Nó **in lý do** rồi mới cài; sai thì chỉ định tay:

```bash
bash bootstrap.sh web-admin ~/p/admin --prune     # --prune: gỡ skill của profile cũ
bash bootstrap.sh web-admin ~/p/shop --exclude-pack motion,design --prune   # 95% → 82%
```

Mỗi lần cài xong script in ngân sách thật của workspace đó (cả hai đồng hồ). Đổi profile mà
quên `--prune` thì nó cũng cảnh báo.

## Cài toàn bộ máy (nếu bạn muốn mọi project giống nhau)

```bash
bash bootstrap.sh --system
```

Cài **một lần**, mọi project dùng được — không phải làm gì cho từng project nữa.

Nó ghi vào `~/.gemini/`:

| Ghi gì | Ở đâu |
|---|---|
| Rules always_on (ponytail full, skill-first, verify, chống treo task) | `~/.gemini/AGENTS.md` |
| **186 skill** (60 skill chỉ dành cho project) | `~/.gemini/config/skills/` |
| LSP cho mọi language server có trên máy | `~/.gemini/config/mcp_config.json` |

Quy tắc GitHub đa tài khoản phân biệt credential Git, tài khoản `gh` và author commit;
chi tiết cấu hình theo repo: [docs/github-multi-account.md](docs/github-multi-account.md).

Quy tắc chống treo yêu cầu agent phân biệt lệnh hữu hạn với server/watcher, kiểm tra
trạng thái và log khi chờ lâu, tránh chạy trùng và báo rõ khi bị chặn. Đây là chỉ dẫn,
không phải tiến trình giám sát độc lập: nếu Antigravity tự đơ thì không tự khôi phục được.
Chạy lại `--core` hoặc `--system` để cập nhật rules global; installer sao lưu `AGENTS.md` cũ.

> **Ngân sách — đọc kỹ chỗ này.** Ước lượng theo description: 186 skill + `AGENTS.md`
> ≈ **16.500 token**. Nhưng **đồng hồ trong Settings → Skills đếm cao hơn ~24%**: hồi quy từ
> máy thật (195 skill = 21.430 token, 204 skill = 22.350) ra `≈ 1.497 + 102,2 × số skill`.
> Nghĩa là **186 skill ≈ 103% trần 20k** — vượt, và Antigravity **tự loại bớt skill** (panel
> hiện "10 excluded"). Skill bị loại thì coi như không có.
>
> Vì vậy lệnh khuyên dùng cho toàn máy là **bỏ hai pack ít dùng lại**:
>
> ```bash
> bash bootstrap.sh --system --exclude-pack education,docs
> ```
>
> 156 skill ≈ **87%** theo đồng hồ đó — còn ~13% cho skill riêng của từng project. Project giáo
> dục/tài liệu cần thì rót đúng pack: `bash bootstrap.sh education-k12 ~/p/btvn`.
> Ai muốn giữ đủ 186 thì được, chỉ cần biết là vài skill sẽ bị loại ngẫu nhiên theo ngân sách.

Chạy lại nhiều lần vô hại — skill đã có thì bỏ qua. Bản cài cũ để lại thư mục skill đã bị bỏ
khỏi registry thì script in ra tên chúng; thêm `--prune` để dọn (chỉ xoá thư mục do Skill OS
tạo, skill của bạn giữ nguyên).

**Cập nhật bản đã cài:** sau khi cập nhật repo, dùng `--update-owned` để ghi lại skill do
Skill OS quản lý mà không đụng skill không có dấu sở hữu. Chạy trước với `--dry-run`, sau
đó bỏ cờ này khi đã xem kết quả. Ví dụ: `python3 tools/install.py --core --update-owned`;
với project, thêm `--profile <id> -w <dir> --update-owned`. Cờ này vẫn **ghi đè chỉnh sửa
thủ công bên trong skill do Skill OS quản lý**, nên sao lưu trước. Rules global được backup;
agent, plugin, hook cũ không tự cập nhật bằng cờ này và cần xem xét riêng. Chỉ dùng `--prune`
khi đã xem danh sách sẽ gỡ. Prompt cập nhật toàn repo: [docs/prompt-cho-antigravity.md](docs/prompt-cho-antigravity.md#4-cập-nhật-toàn-bộ-repo-đã-cài).

**186 hay 190?** Mặc định `--system` cài **186** và bỏ 4 skill `mode: manual` —
`vercel-byoc`, `vercel-cli-with-tokens`, `brand-guidelines`, `skill-creator` (cần token thật,
hoặc là brand của Anthropic, hoặc người dùng tự sửa trước khi dùng). Thêm `--include-manual`
thì đĩa có 190, ngân sách 16.842 token ≈ 84%. Cả hai đều đúng; chỉ cần biết con số nào ứng với
lệnh nào.

Chưa có repo trên máy:

```bash
curl -fsSL https://raw.githubusercontent.com/Xwuan19/antigravity-skill-os/main/bootstrap.sh -o bootstrap.sh
bash bootstrap.sh --system
```

## Hoặc cài hẹp cho một project

Dùng khi bạn muốn workspace đó **không** thấy skill ngoài lĩnh vực:

```bash
bash bootstrap.sh web-admin ~/p/admin      # 102 skill, không có skill Python
bash bootstrap.sh cli-tool ~/p/bot         # 69 skill, không có skill design
```

Cách này cài thêm vào `<project>/.agents/skills/`, chỉ project đó thấy. Xem bảng profile bên dưới.

### Từng bước, nếu không dùng script

```bash
git clone https://github.com/Xwuan19/antigravity-skill-os && cd antigravity-skill-os

python3 tools/install.py --system                                  # toàn bộ máy
python3 tools/install.py --core                                    # chỉ rules + 4 skill tối thiểu
python3 tools/install.py --profile web-admin -w ~/p/admin --hooks --plugins
python3 tools/lsp.py --check                                       # máy có language server nào
python3 tools/lsp.py --global --langs all                          # LSP cho mọi project
python3 tools/install.py --list                                    # xem profile
```

Có `--dry-run` cho mọi lệnh, `--uninstall` để gỡ, `--include-manual` để cài cả skill phải gọi bằng `/`.

## ⚠ Đọc trước: "đưa link repo cho Antigravity" **không** đủ

Không có cơ chế nào để Antigravity tự tải skill từ một URL GitHub. Skill phải **là file
trên đĩa** ở đúng một trong hai chỗ:

```
~/.gemini/config/skills/<id>/SKILL.md     ← mọi project
<workspace>/.agents/skills/<id>/SKILL.md  ← chỉ project đó
```

Nên chuỗi thật là:

```
chạy installer  →  file nằm trên đĩa  →  Antigravity tự nạp từ đó, mọi project
 (một lần/cả máy)    (~/.gemini/)         (từ đây mới tự động)
```

Sau bước cài thì **đúng là tự động**: không slash command, không cần nhắc, agent tự chọn
skill theo mô tả khi việc khớp. Nhưng bước cài phải chạy — nói "hãy đọc repo này" trong
chat thì model chỉ đọc được văn bản, không tạo ra file skill.

| Việc | Tự động? |
|---|---|
| Cài skill vào đĩa | ❌ `bash bootstrap.sh --system`, **một lần cho cả máy** |
| Chọn skill theo ngữ cảnh | ✅ tự động, mỗi lượt |
| Ponytail `full` khoá cứng | ✅ global rules, mọi phiên |
| Hook / plugin / MCP | ✅ sau khi cài, khởi động lại Antigravity một lần |
| Project mới | ✅ **không làm gì cả** — đã nằm ở tầng global |
| Language server (LSP) | ⚠️ phải cài binary trên máy (`--check` in lệnh cài) |

## Hai tầng cài

| Tầng | Lệnh | Đích | Hiệu lực |
|---|---|---|---|
| System | `--system` | `~/.gemini/AGENTS.md` + **toàn bộ** skill vào `~/.gemini/config/skills/` | Mọi project, mọi phiên. Không cần cài lại cho từng project |
| Global | `--core` | `~/.gemini/AGENTS.md` + 4 skill tối thiểu | Như trên nhưng danh sách skill gọn hơn |
| Workspace | `--profile <id> -w <dir>` | `<dir>/.agents/skills/` + `.agents/agents/` | Cô lập cứng trong project đó |
| Hooks | `--hooks` | `<dir>/.agents/hooks.json` + `.agents/skill-os/` | SessionStart nhắc luật hệ thống |
| Plugins | `--plugins` | `<dir>/.agents/plugins/` | 9 plugin Claude Code đã port (23 skill) |
| LSP | `--lsp` | `<dir>/.agents/mcp_config.json` + `.agents/lsp/` | code intelligence 12 ngôn ngữ qua MCP |
| Stack | `--stacks` | (lọc, không chép gì) | skill theo ngôn ngữ: tự dò đuôi file, hoặc ép `python,go` |

**Cô lập cứng:** mỗi project một `--profile`. Router loại toàn bộ skill không liên quan —
`education-k12` chỉ nhận 24/253 skill (`docs` + `education`), không một dòng code nào. Muốn
chắc chắn "folder design chỉ có skill design" thì tách workspace, vì Antigravity **không**
hỗ trợ skill theo sub-folder.

Skill `mode: manual` mặc định **không cài** — phải `--include-manual`, để danh sách
description trong workspace gọn lại.

## Luật theo ngôn ngữ

Cài theo project, tự dò ngôn ngữ, chép vào `.agents/rules/`:

```
<workspace>/.agents/rules/common.md      ← luôn
<workspace>/.agents/rules/python.md      ← khi dò thấy Python
<workspace>/.agents/rules/go.md          ← khi dò thấy Go
```

Skill phải **được chọn** mới chạy; luật thì luôn chạy. Vài thứ phải đúng ở mọi lần sửa
code, không phụ thuộc agent có nhớ gọi skill hay không — đó là chỗ của tầng này.

14 ngôn ngữ: `python` `typescript` `go` `rust` `java` `kotlin` `csharp` `ruby` `php`
`swift` `cpp` `lua` `sql` `shell`. Workspace Python: **2 file, ~2.1 KB** always-on.
Tắt bằng `--no-rules`. Chi tiết: [docs/rules-per-stack.md](docs/rules-per-stack.md).

## 11 profile

| Profile | Skill | Agent | LSP | Cho |
|---|---|---|---|---|
| `desktop-app` | 109 | 43 | ✅ | App cài trên máy: macOS, Tauri, Electron, WPF |
| `web-admin` | 102 | 43 | ✅ | Dashboard, CRUD, SaaS |
| `mobile-app` | 85 | 41 | ✅ | React Native, Expo, iOS/Android |
| `cli-tool` | 69 | 41 | ✅ | CLI, script, backend |
| `landing` | 52 | 43 | ✅ | Landing, marketing, portfolio |
| `design-system` | 29 | 10 | ✅ | UI kit, component library, token |
| `static-site` | 29 | 2 | — | Trang tĩnh HTML/CSS, không framework, không build tool |
| `education-k12` | 24 | — | — | Giáo án phổ thông, đề kiểm tra |
| `education-language` | 16 | — | — | Trung tâm ngoại ngữ, gia sư |
| `docs-writer` | 16 | 3 | — | Báo cáo, thuyết trình, bảng tính |
| `meta` | 8 | 8 | ✅ | Nuôi chính hệ thống này (plugin-dev, hookify) |

Đo trên workspace TypeScript, có `--stacks` tự dò. Project Python nhiều hơn (`web-admin` 111
thay vì 102, `desktop-app` 118); workspace chưa có file nào thì không lọc stack (lấy hết).

Thêm profile = thêm 1 file JSON trong `profiles/`. Không sửa code.

## Thiết kế: web, mobile, desktop, slide

37 skill thiết kế trong pack `design`. Chọn theo việc, không theo tool.

| Cần gì | Skill |
|---|---|
| **UI/UX tổng** — style, palette, font, UX rule, chart | `ui-ux-pro-max` (22 stack: react → wpf/winui/avalonia/javafx), `design-system` |
| **Web** — dựng giao diện | `frontend-design`, `ui-styling` (shadcn + Tailwind), `shadcn-ui`, `web-design-guidelines`, `extract-static-html` |
| **Mobile** — iOS/Android/RN | `apple-hig` (123 trang HIG), `react-native`, `swiftui-pro`, `liquid-glass-design` |
| **Desktop** — macOS/Tauri/Electron/WPF | `mac-design`, `mac-design-kit`, `mac-layout-grid`, `mac-ux-design`, `mac-design-system`, `mac-app-icon`, `mac-design-from-app` |
| **Slide / thuyết trình** | `slides`, `frontend-slides` |
| **Nhận diện** — logo, icon, brand, banner | `design`, `brand`, `brand-guidelines` |
| **Chống nhạt** — UI trông như template | `taste-design`, `taste-skill`, `apple-design`, `emil-design-eng`, `make-interfaces-feel-better` |
| **Rút hệ thống từ code có sẵn** | `extract-design-md`, `mac-design-from-app` |
| **A11y** — WCAG 2.2 AA web + iOS + Android | `accessibility` |

`ui-ux-pro-max` tra cứu offline bằng `search.py` trên CSV: 79 style, 192 palette,
74 cặp font, 119 UX rule, 105 icon, 25 loại chart. Không cần mạng.

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
**`handoff`** (mình tự viết — các bản cộng đồng đều quá mỏng, chỉ 1 file không có mục "đường cụt đã thử").

**Không port** — `context-mode` (44 MB, là **ứng dụng** chứ không phải skill),
`claude-mem` (app Node + sqlite). `grill-me` và `taste-skill` **đã port**: `grill-me` viết
lại (bản gốc gọi tool `AskUserQuestion` mà Antigravity không có), `taste-skill` ghi chú cũ
của mình sai — repo là **MIT**. Lý do đầy đủ trong tài liệu trên.

## Lọc theo ngôn ngữ (`--stacks`)

Skill Python không nên nằm trong project TypeScript. `install.py` **tự dò** ngôn ngữ bằng
cách đếm đuôi file trong workspace rồi chỉ cài skill đúng stack:

```
workspace toàn .py   → lấy 18 skill python, không lấy skill typescript
workspace toàn .ts   → lấy 5 skill typescript, không lấy skill python
```

```bash
python3 tools/install.py --profile web-admin -w ~/p/admin               # tự dò
python3 tools/install.py --profile web-admin -w ~/p/admin --stacks go,rust   # ép
```

Skill khai `stack: ["general"]` hoặc không khai stack thì vào mọi project. Đây là lý do
`web-admin` trên project TS ra 68 skill còn trên project Python ra 79 — khác nhau đúng phần
ngôn ngữ, không phải hai bộ khác nhau.

**Phủ ngôn ngữ:**

| Ngôn ngữ | Skill | Nguồn |
|---|---|---|
| Python | 22 — Django (patterns/tdd/security), FastAPI, `python-*`, `uv-package-manager`, `async-python-patterns` | ECC, wshobson |
| TypeScript / JS | 13 — NestJS, Vue, Nuxt 4, Vite, Prisma, Angular, `typescript-strict`, `javascript-strict` | ECC, 0xMassi, wshobson |
| Java | 9 — Spring Boot (patterns/tdd/security), Quarkus (patterns/tdd/security), JPA, MyBatis | ECC |
| Kotlin | 5 — patterns, Ktor, Exposed, testing | ECC |
| C / C++ | 4 — `cpp`, `cpp-coding-standards`, `cpp-testing`, `memory-safety-patterns` | ECC, Mindrally, wshobson |
| PHP | 4 — Laravel (patterns/tdd/security), `php-*` | ECC |
| Rust | 4 (`rust-strict`, `rust-skills` 265 rule, `rust-async-patterns`) | 0xMassi, leonardomso, wshobson |
| Shell | 3 (`bash-defensive-patterns`, `bats-testing-patterns`, `shellcheck-configuration`) | wshobson |
| C# | 3 — `c-sharp`, `dotnet-backend-patterns`, `csharp-testing` | ECC, Mindrally, wshobson |
| Go | 3 — `go-strict`, `go-concurrency-patterns`, `golang-testing` | ECC, 0xMassi, wshobson |
| Perl | 2 — `perl-patterns`, `perl-testing` | ECC |
| Ruby | 2 — Rails patterns, `ruby-*` | ECC, Mindrally |
| Swift | 2 — SwiftUI, Apple design | twostraws, dickwu |
| Dart / Flutter | 1 — `flutter-dart-code-review` | ECC |
| F# | 1 — `fsharp-testing` | ECC |
| Lua · SQL | 1 mỗi cái | Mindrally, 0xMassi |

18 ngôn ngữ có skill riêng. LSP phủ 12 (`dart`, `perl`, `fsharp`, `lua`, `sql`, `ruby`, `swift`
chưa có language server trong repo).

**Chi phí thật:** mỗi workspace mang 52–109 skill tuỳ profile; `--system` mang 186 ≈ 16.500
token description mỗi phiên (xem mục ngân sách ở trên). Đây là giá của việc có nhiều skill —
`route.py` in ra con số này trước khi bạn cài.

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
rules/           15 luật ngôn ngữ + common.md (always-on, cài theo workspace)
registry/        skills.json (253) + agents.json (46) + plugins.json (9) + lsp.json (12) + taxonomy.md
profiles/        10 kiểu project → skill + nhóm agent + plugin
packs/           250 skill đã vendor + VENDOR.json (sha256 từng cái)
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
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | 31 skill (developer-essentials, backend, python, typescript, security) |
| [tjboudreaux/cc-thinking-skills](https://github.com/tjboudreaux/cc-thinking-skills) | MIT | 6 mô hình tư duy gắn với gỡ lỗi |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | MIT | taste-skill (design) |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT | 7 skill design (ui-ux-pro-max, ui-styling, design-system, slides, design, brand, banner-design) |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | Apache-2.0 | 6 skill (shadcn-ui, react-native, extract-design-md, extract-static-html, enhance-prompt, taste-design) |
| [daveebbelaar/bama](https://github.com/daveebbelaar/bama) | MIT | 7 skill macOS (mac-design, mac-design-kit, …) |
| [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | MIT | frontend-slides |
| [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | MIT | swiftui-pro |
| [dickwu/apple-design-skill](https://github.com/dickwu/apple-design-skill) | **không có LICENSE** | `apple-hig` — 123 trang HIG |
| [RobMitt/grill-me-skill](https://github.com/RobMitt/grill-me-skill) | **không có LICENSE** | `grill-me` — viết lại, xem ghi chú dưới |
| [ajbmachon/ajbm-skills](https://github.com/ajbmachon/ajbm-skills) | NOASSERTION | testing-best-practices |
| language server (gopls, pyright, jdtls, …) | giấy phép riêng của từng server | **không vendor** — cài bằng trình quản lý gói của bạn |

`vercel-labs/agent-skills` không có file `LICENSE` ở gốc, nhưng README mục *License* ghi
MIT và 4 SKILL.md tự khai `license: MIT`. Coi là MIT.

**Chính sách license (đổi sau khi bạn yêu cầu):** không dùng license làm bộ lọc nữa — lấy
cái hiệu quả. Cột license ở trên để bạn biết mình đang dùng cái gì, không phải để loại.
Hai chỗ vẫn ghi rõ vì chúng khác biệt về bản chất:

- `grill-me` — repo gốc **không có LICENSE**. Không chép nguyên văn: viết lại cho Antigravity
  (tool `ask_question` thay `AskUserQuestion`) và ghi nguồn trong SKILL.md.
- `ajbm-skills` — license `NOASSERTION` (không xác định được). Đã lấy 1 skill.
- `dickwu/apple-design-skill` — repo **không có LICENSE**. Lấy nguyên văn vì nội dung là
  bản tóm tắt HIG công khai của Apple; nếu bạn cần sạch pháp lý thì xoá pack `apple-hig`.
- `google-labs-code/stitch-skills` — chỉ lấy 6 skill chạy được **không cần** Stitch MCP.

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
- [docs/hermes-filter.md](docs/hermes-filter.md) — lọc 44 skill của `hermes-agent` xuống 10, cách làm từng bước
- [docs/rules-per-stack.md](docs/rules-per-stack.md) — luật theo ngôn ngữ, vì sao không chép của ECC
- [docs/ecc-skills.md](docs/ecc-skills.md) — lấy 53 skill từ kho 313 của ECC, cách port từng loại
- [docs/global-vs-project.md](docs/global-vs-project.md) — global hay theo-project: số đo thật của 3 mô hình, cái nào hợp việc gì
- [docs/prompt-cho-antigravity.md](docs/prompt-cho-antigravity.md) — câu để dán vào Antigravity, nó tự cài
- [packs/design/apple-design/SKILL.md](packs/design/apple-design/SKILL.md) — skill design gốc Apple, kèm LICENSE
