# Skill Catalog — Antigravity Skill OS

Bản tổng hợp các skill/bộ skill để bạn duyệt trước khi mình đóng gói vào repo.
Đánh dấu `[x]` vào ô bạn muốn giữ, gạch bỏ ô không cần, và thêm link của bạn vào
mục [Chờ link từ bạn](#-chờ-link-từ-bạn).

Cập nhật: 2026-10-29 · Nguồn chuẩn: [docs skills](https://antigravity.google/docs/skills) · [docs rules](https://antigravity.google/docs/rules/)

---

## 0. Phân loại: chọn lúc cài, không phải lúc chạy

Đã dựng xong hệ phân loại — chi tiết ở [registry/taxonomy.md](../registry/taxonomy.md).
Mỗi skill khai `domain` / `phase` / `artifact` / `mode`, thêm `families` và `forbid_domains`.
Router [`tools/route.py`](../tools/route.py) biến profile project thành danh sách skill và cài
vào `.agents/skills/`. Skill không được chọn thì **không tồn tại** trong project đó.

Ba ràng buộc kỹ thuật dưới đây là lý do phải làm theo cách đó:

## 0.1. Ba ràng buộc kỹ thuật

Đây là lý do bên dưới mình chia thành **Core / Pack / Workspace** thay vì "một túi skill".

| # | Sự thật (từ docs chính thức) | Hệ quả cho thiết kế |
|---|---|---|
| 1 | **Skill chỉ có 2 phạm vi**: `<workspace-root>/.agents/skills/` và `~/.gemini/config/skills/`. **Không có skill theo sub-folder.** | Không thể "folder `design/` tự có skill riêng" trong cùng 1 workspace. Muốn cô lập thật → **tách workspace**, hoặc dùng **rules theo thư mục** để làm hàng rào mềm. |
| 2 | **Rule thì theo thư mục**: `AGENTS.md`, `.agents/AGENTS.md`, `.agents/rules/*.md` đặt ở **bất kỳ sub-folder nào**, và rule là **cộng dồn** (global + workspace + directory), thư mục cụ thể thắng khi xung đột. | Đây là công cụ duy nhất để "mỗi folder một luật". Isolation = core global thật mỏng + hàng rào ở folder. |
| 3 | **Plugin là global** và Antigravity nạp **mọi folder dưới `<plugin-root>/skills/`** — không chọn lẻ được. `always_on` + global rules chung **ngân sách 20.000 token**, mỗi file cắt ở 24KB; description skill nên ≤ 1024 ký tự. | Không làm 1 plugin khổng lồ. Phải **tách plugin theo pack** và cài skill vào workspace bằng copy, không bằng plugin, khi cần cô lập. |

**Mô hình 3 tầng mình đề xuất:**

```
TẦNG 0 — CORE (global, mọi phiên, không cần gõ /)
   ~/.gemini/AGENTS.md            ← luật always_on, cực mỏng (~800–1200 token)
                                   ponytail FULL khoá cứng ở đây (không lite/ultra)
   ~/.gemini/config/skills/       ← 3–5 skill "luôn có mặt" (bootstrap, verify, meta)

TẦNG 1 — PACK (cài vào từng workspace, chọn theo lĩnh vực)
   <workspace>/.agents/skills/    ← coding | design | education | docs | security

TẦNG 2 — WORKSPACE (hàng rào + override)
   <workspace>/AGENTS.md          ← luật riêng của project
   <workspace>/design/AGENTS.md   ← luật riêng của sub-folder (nếu cần)
   <workspace>/.agents/rules/*.md ← rule theo glob: "*.tsx", "*.proto"...
```

> Vì skill **không** tách theo folder được, "folder thiết kế chỉ dùng skill thiết kế" đạt được bằng:
> **(a)** workspace thiết kế chỉ cài pack design (cô lập cứng), hoặc
> **(b)** nếu dùng chung 1 workspace: `AGENTS.md` trong folder `design/` ghi rõ *"các skill coding không thuộc phạm vi, không dùng"* (cô lập mềm). Mình sẽ làm cả hai và bạn chọn.

---

## 1. CORE — luôn bật, mọi project, không cần `/`

Đây là phần implement bằng **rules** (vì chỉ rules mới `always_on` được), không phải skill.

| ☐ | Thành phần | Từ đâu | Vai trò | Ghi chú |
|---|---|---|---|---|
| ☑ | `ponytail` **FULL — khoá cứng** | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) · MIT | Thang 7 bước YAGNI: có cần tồn tại → đã có trong repo → stdlib → native → dependency → 1 dòng → tối thiểu | **Đã chốt:** luôn mức `full`, mọi phiên, mọi yêu cầu. Không `lite`, không `ultra`, không `off`, không cần gõ `/ponytail`. Không cắt validation/security/a11y. |
| ☐ | `skill-first bootstrap` | tự viết (lấy ý [obra/superpowers](https://github.com/obra/superpowers) `using-superpowers`) | Trước khi trả lời: quét danh sách skill, nếu có skill khớp thì đọc và làm theo | Đây chính là cơ chế "tự dùng skill, không cần gõ /". ~200 token. |
| ☐ | `verify-before-done` | rút từ superpowers `verification-before-completion` | Không tuyên bố "xong" khi chưa chạy lệnh và đọc output thật | 3 dòng. Rất đáng luôn bật. |
| ☐ | `honesty / no-invent` | tự viết | Không bịa API, không bịa số liệu; thiếu thì nói thiếu | Tuỳ bạn, mình thấy hữu ích cho cả code và giáo dục. |
| ☐ | `caveman` (nói ngắn) | [awesome-skills](https://awesome-skills.com/) meta | Trả lời ngắn, không lan man | Xung đột nhẹ với phong cách giải thích dài; mình **không** khuyến nghị bật mặc định. |

> **Đã chốt:** ponytail `full` là **skill hệ thống**, không phải tuỳ chọn của người dùng.
> Nó sống trong `AGENTS.md` global dưới dạng `always_on` → mọi phiên, mọi project, mọi
> yêu cầu đều chịu thang YAGNI, kể cả khi bạn không nhắc tên. Slash command `/ponytail`
> **bị bỏ** — không cài `argument-hint`, không dạy agent chuyển mức.

**Tổng ngân sách core:** ~1.000–1.300 token / 20.000 → thừa nhiều cho rules từng project.

---

## 2. CORE SKILLS — global, tự kích hoạt ở mọi phiên

Vẫn cài vào `~/.gemini/config/skills/` nhưng ở tầng skill (progressive disclosure → chỉ tốn 1 dòng description khi rảnh).

| ☐ | Skill | Nguồn | Khi nào tự chạy |
|---|---|---|---|
| ☐ | `using-superpowers` | [obra/superpowers](https://github.com/obra/superpowers) · MIT | Đầu mọi phiên: bắt buộc kiểm tra skill trước khi trả lời |
| ☐ | `verification-before-completion` | obra/superpowers | Trước khi nói "xong / đã sửa / pass" |
| ☐ | `writing-skills` | obra/superpowers | Khi tạo/sửa skill — rất cần cho chính repo này |
| ☐ | `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | Tạo skill mới + eval |
| ☐ | `discernment-nudge` | anthropics/skills | Chèn câu hỏi kiểm chứng sau câu trả lời quan trọng |

---

## 3. PACK CODING — cài vào workspace code

### 3.1 Superpowers (bộ khung quy trình)

| ☐ | Skill | Việc nó ép làm |
|---|---|---|
| ☐ | `brainstorming` | Trước khi build: hỏi intent, chốt design, dừng lại chờ duyệt |
| ☐ | `writing-plans` | Design → plan từng task, không có "TBD" |
| ☐ | `executing-plans` | Chạy plan, checkpoint review giữa các task |
| ☐ | `test-driven-development` | RED → GREEN → REFACTOR; code viết trước test bị xoá |
| ☐ | `systematic-debugging` | 4 pha tìm root cause; 2 lần fix fail = dừng lại |
| ☐ | `requesting-code-review` | Review theo mức độ nghiêm trọng trước khi merge |
| ☐ | `receiving-code-review` | Kiểm chứng feedback, không đồng ý cho có |
| ☐ | `using-git-worktrees` | Cô lập nhánh trước khi làm |
| ☐ | `finishing-a-development-branch` | Chỉ merge/PR khi test xanh |
| ☐ | `dispatching-parallel-agents` | 2+ việc độc lập → chạy song song |
| ☐ | `subagent-driven-development` | Mỗi task 1 subagent + 1 review |

### 3.2 Ponytail (bộ đầy đủ — 6 skill)

| ☐ | Skill | Việc nó làm |
|---|---|---|
| ☐ | `ponytail` | Chế độ "senior dev lười": diff nhỏ nhất giải trọn vấn đề |
| ☐ | `ponytail-review` | Soi diff, chỉ ra chỗ nên xoá |
| ☐ | `ponytail-audit` | Audit repo, **không sửa file** |
| ☐ | `ponytail-debt` | Lập sổ nợ từ các comment `// ponytail:` |
| ☐ | `ponytail-gain` | Bảng điểm benchmark (không bịa số cho repo của bạn) |
| ☐ | `ponytail-help` | Trợ giúp |

#### Trạng thái: FULL khoá cứng — không có bảng chuyển mức

Upstream có 3 mức (`lite` / `full` / `ultra`) + tắt (`off`). **Repo này bỏ hết phần đó.**

| | |
|---|---|
| Mức dùng | **`full`** — chỉ `full` |
| Áp dụng khi nào | **Mọi phiên, mọi project, mọi yêu cầu** — kể cả câu hỏi nhỏ, kể cả phiên không liên quan code |
| Cách kích hoạt | **Không cần.** Nằm trong `AGENTS.md` global, `always_on`, nạp từ lượt đầu tiên |
| `lite` | ❌ bỏ — không cài `argument-hint`, agent không được dạy chuyển mức |
| `ultra` | ❌ bỏ — hành vi "chất vấn yêu cầu" gây ma sát, không phải thứ nên luôn bật |
| `off` / `normal mode` | ❌ bỏ — không có đường thoát, kể cả khi bạn nói "stop ponytail" |
| `/ponytail lite\|full\|ultra` | ❌ bỏ — slash command không được đăng ký |

Vì sao phải xoá hẳn chứ không chỉ "mặc định full": Antigravity **không có lifecycle
hook**, nên mức không lưu qua lượt (`INSTALL.md`: *"No lifecycle hooks, so levels don't
persist"*). Nếu để `argument-hint` trong skill, agent sẽ có đường ghi đè và mức sẽ trôi.
Cách duy nhất giữ `full` vĩnh viễn là **không tồn tại mức nào khác để chọn**.

`full` được hiện thực thành **một file rule `always_on` duy nhất** — xem
[`core/rules/ponytail-full.md`](../core/rules/ponytail-full.md).

### 3.3 Kỹ thuật khác

| ☐ | Skill | Nguồn | Việc nó làm |
|---|---|---|---|
| ☐ | `webapp-testing` | anthropics/skills | Playwright: tự test UI local, chụp màn hình, đọc console |
| ☐ | `mcp-builder` | anthropics/skills | Dựng MCP server |
| ☐ | `claude-api` | anthropics/skills | Viết code gọi Claude API đúng chuẩn |
| ☐ | `doc-coauthoring` | anthropics/skills | Quy trình 3 pha viết tài liệu |
| ☐ | bộ security | [trailofbits/skills](https://github.com/trailofbits/skills) | CodeQL + Semgrep + workflow audit |

---

## 4. PACK DESIGN — cài vào workspace thiết kế

| ☐ | Skill | Nguồn | Việc nó làm |
|---|---|---|---|
| ☑ | `frontend-design` **đã vendor** @ `2235be7` | anthropics/skills · Apache-2.0 | Ép chọn hướng thẩm mỹ + typography trước khi viết UI; chống "AI slop" |
| ☐ | `web-design-guidelines` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) · MIT | Audit UI/a11y theo Web Interface Guidelines |
| ☐ | `writing-guidelines` | vercel-labs/agent-skills | Copy/microcopy cho trang |
| ☐ | `canvas-design` | anthropics/skills | Ấn phẩm/visual chất lượng tạp chí |
| ☐ | `theme-factory` | anthropics/skills | 10 theme màu chuyên nghiệp |
| ☐ | `brand-guidelines` | anthropics/skills | Chuẩn brand (mẫu của Anthropic — thay bằng brand của bạn) |
| ☐ | `web-artifacts-builder` | anthropics/skills | React + Tailwind artifact tương tác |
| ☐ | `algorithmic-art` | anthropics/skills | Generative art p5.js |
| ☐ | `slack-gif-creator` | anthropics/skills | GIF cho Slack |
| ☐ | nhóm diagram (Excalidraw / Mermaid / D3) | chưa chốt nguồn — xem [top-agent-skills](https://top-agent-skills.com/) | Vẽ sơ đồ kiến trúc từ mô tả |

### 4.1 Motion pack — [emilkowalski/skills](https://github.com/emilkowalski/skills) · MIT

14 skill, trong đó 6 cái đã đưa vào registry. Đây là bộ mạnh nhất về chuyển động web.

| ☐ | Skill | Việc nó làm |
|---|---|---|
| ☑ | `apple-design` | 17 mục từ WWDC: response, direct manipulation, interruptibility, spring, momentum, rubber-banding, materials, typography, reduced-motion. **23KB — sát trần 24KB.** Đã vendor, xem [PATCH.md](../packs/design/apple-design/PATCH.md) |
| ☐ | `emil-design-eng` | Quan điểm design-engineering của tác giả |
| ☐ | `animate` | Viết animation |
| ☐ | `improve-animations` | Nâng animation có sẵn |
| ☐ | `review-animations` | Review animation |
| ☐ | `find-animation-opportunities` | Tìm chỗ nên thêm chuyển động |
| ☐ | `break-ui` | Cố tình phá UI để tìm lỗi |
| ☐ | `animation-vocabulary` · `prototype` · `pick-ui-library` · `mobile-native` · `write-swift` · `animate-expo` · `ask-sonner` | Chưa xếp — chờ bạn chọn |

> `frontend-design` và `apple-design` **không xung đột**: một cái lo "trông thế nào",
> một cái lo "chạm vào thấy thế nào". Khác trục, cài cả hai là hợp lý.

> Design pack **không** nên chứa superpowers/TDD. Nhưng vẫn nên giữ `verification-before-completion` và ponytail.

---

## 5. PACK EDUCATION — cài vào workspace giáo dục

### 5.1 K-12 / giáo viên — [dh2211/edu-agents](https://github.com/dh2211/edu-agents) (11 skill)

| ☐ | Skill | Việc nó làm |
|---|---|---|
| ☐ | `edu-learning-objectives` | Mục tiêu đo được + success criteria theo Bloom/DOK |
| ☐ | `edu-unit-planner` | Unit theo backward design (UbD) |
| ☐ | `edu-lesson-planner` | Giáo án có thời lượng, I do / we do / you do |
| ☐ | `edu-slide-outline` | Outline slide + speaker notes |
| ☐ | `edu-worksheet-builder` | Worksheet + answer key |
| ☐ | `edu-assessment-builder` | Đề kiểm tra có blueprint + rubric chấm |
| ☐ | `edu-formative-checks` | Exit ticket, hinge question |
| ☐ | `edu-rubric-builder` | Rubric (analytic / single-point / holistic) |
| ☐ | `edu-differentiation` | UDL, tier hỗ trợ/mở rộng, hỗ trợ EL |
| ☐ | `edu-student-work-feedback` | Feedback bài học sinh (strength / next step / question) |
| ☐ | `edu-family-message` | Thư cho phụ huynh bằng ngôn ngữ dễ hiểu |

### 5.2 Ngoại ngữ — [CristianHeyde/language-teaching-skills](https://github.com/CristianHeyde/language-teaching-skills) (6 skill)

| ☐ | Skill | Việc nó làm |
|---|---|---|
| ☐ | `task-design` | Thiết kế & review task/hoạt động |
| ☐ | `lesson-planning` | Giáo án + tài liệu GV/HS |
| ☐ | `course-architecture` | Khung khoá học / syllabus |
| ☐ | `study-planning` | Kế hoạch tự học thực tế |
| ☐ | `submission-review` | Chấm bài + feedback formative |
| ☐ | `staff-assistance` | Trả lời câu hỏi học vụ |

### 5.3 Học tập tổng quát — [JayRHa/agent-skills](https://github.com/JayRHa/agent-skills) (nhóm Learning)

| ☐ | Skill | Việc nó làm |
|---|---|---|
| ☐ | `study-plan-builder` | Lộ trình học theo deadline + quỹ thời gian/tuần |
| ☐ | `concept-explainer` | Giải thích khái niệm từ ELI5 → chuyên gia |
| ☐ | `flashcard-generator` | Flashcard spaced-repetition (Anki) |
| ☐ | `language-tutor` | Gia sư hội thoại có chấm lỗi |
| ☐ | `book-summarizer` | Tóm sách nhiều mức độ sâu |

### 5.4 Khác

| ☐ | Skill | Nguồn | Việc nó làm |
|---|---|---|---|
| ☐ | `lesson-plan` (giảng viên doanh nghiệp) | [jiangfire/lesson-plan-skills](https://github.com/jiangfire/lesson-plan-skills) | Giáo án + slide HTML 1 file, 6 nguyên tắc sư phạm |
| ☐ | `academy-guide` | anthropics/skills | Gợi ý khoá học/tutorial phù hợp |

> Chồng lấn cần bạn quyết: edu-agents `edu-lesson-planner` **vs** language-teaching `lesson-planning` **vs** jiangfire `lesson-plan`. Cùng chức năng, 3 nguồn. Mình đề xuất giữ **edu-agents** (K-12, phổ thông) + **jiangfire** (doanh nghiệp), bỏ language-teaching `lesson-planning` nếu bạn không dạy ngoại ngữ.

---

## 6. PACK DOCS — tài liệu văn phòng

| ☐ | Skill | Nguồn | Việc nó làm |
|---|---|---|---|
| ☐ | `docx` | anthropics/skills | Tạo/sửa Word |
| ☐ | `pdf` | anthropics/skills | Đọc/tạo/merge/OCR/form PDF |
| ☐ | `pptx` | anthropics/skills | Tạo PowerPoint |
| ☐ | `xlsx` | anthropics/skills | Excel có công thức |
| ☐ | `internal-comms` | anthropics/skills | Mẫu thông tin nội bộ |

> Pack này rất hợp với workspace giáo dục (giáo án Word, slide PPTX) → mình đề xuất **cho phép kèm** docs pack vào workspace education.

---

## 7. META — dùng để nuôi chính hệ thống này

| ☐ | Thành phần | Nguồn |
|---|---|---|
| ☐ | `skill-creator` | anthropics/skills |
| ☐ | `writing-skills` | obra/superpowers |
| ☐ | `testing-skills-with-subagents` | obra/superpowers |
| ☐ | Spec Agent Skills | [agentskills/agentskills](https://github.com/agentskills/agentskills) · [agentskills.io](https://agentskills.io/home) |
| ☐ | Danh mục để tìm thêm | [uhub/awesome-agent-skills](https://github.com/uhub/awesome-agent-skills) · [top-agent-skills.com](https://top-agent-skills.com/) · [awesome-skills.com](https://awesome-skills.com/) |

---

## 8. Chờ link từ bạn

Điền vào đây — mình sẽ tự tải về, đọc `SKILL.md`, kiểm license, rồi xếp vào pack.

| # | Link bạn gửi | Ghi chú của bạn | Xếp vào pack |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |
| 6 |  |  |  |
| 7 |  |  |  |
| 8 |  |  |  |
| 9 |  |  |  |
| 10 |  |  |  |

---

## 9. Đề xuất "cài trước" — 12 món, làm được ngay hôm nay

1. ✅ `ponytail` **FULL** (core rule) — đã dựng: [`core/AGENTS.md`](../core/AGENTS.md)
2. ✅ `skill-first bootstrap` (core rule) — đã dựng
3. ✅ `verify-before-done` (core rule) — đã dựng
4. `using-superpowers`
5. `verification-before-completion`
6. `writing-skills`
7. `brainstorming`
8. `writing-plans`
9. `test-driven-development`
10. `systematic-debugging`
11. `requesting-code-review`
12. `frontend-design`

Bốn món đầu là **rules** → có hiệu lực ngay, mọi phiên, không cần gõ `/`.

---

## 10. Việc cần bạn quyết để mình bắt tay vào code

| # | Câu hỏi | Lựa chọn |
|---|---|---|
| A | Repo tên `antigravity-skill-os` | ✔ **đã chốt: giữ** |
| A2 | Mức ponytail | ✔ **đã chốt: `full` khoá cứng, mọi phiên, mọi yêu cầu, không `/`, không lite/ultra/off** |
| B | Cô lập folder: **cứng** (mỗi lĩnh vực 1 workspace) hay **mềm** (1 workspace + hàng rào rule)? | ▢ cứng · ▢ mềm · ▢ cả hai |
| C | Vendor skill vào repo (copy, chạy offline, pin commit) hay để installer tải từ upstream? | ▢ vendor · ▢ tải · ▢ hybrid |
| D | Antigravity của bạn là **App**, **CLI**, hay **IDE**? (đường dẫn global khác nhau) | ▢ App · ▢ CLI · ▢ IDE |
| F | 7 profile đã đủ chưa? Thiếu kiểu project nào của bạn? | ▢ đủ · ▢ thiếu: ______ |
| G | Skill nào trong motion pack muốn giữ? (mặc định 6) | ▢ 6 cái · ▢ tất cả 14 · ▢ chỉ apple-design |
| E | Ngôn ngữ trong skill: giữ tiếng Anh (model hiểu tốt nhất) hay Việt hoá phần diễn giải? | ▢ EN · ▢ VI · ▢ EN + VI |
