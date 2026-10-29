# Logic code của Claude — nó nằm ở đâu và skill nào giữ nó

> Đọc xong tài liệu này bạn biết: "Claude Code mạnh ở logic code" thực chất là **sáu cổng
> chặn** trong quy trình, mỗi cổng có một câu từ chối. Repo này đã port 12 skill giữ các
> cổng đó, cộng 15 skill đã có sẵn.

---

## 0. Câu trả lời ngắn

Không có một skill nào tên là "logic". Claude Code viết code tốt vì nó bị **chặn ở những
chỗ người ta thường đi tắt**:

| Người ta hay làm | Claude Code bị buộc làm |
|---|---|
| Thấy bug → sửa luôn | Tái hiện trước, không tái hiện được thì không được gọi là đã sửa |
| Viết code theo yêu cầu mơ hồ | Nêu giả định ra, hỏi khi mơ hồ |
| "Chạy được rồi" | Chạy lệnh kiểm chứng, đọc output, rồi mới nói xong |
| Sửa 200 dòng cho 1 bug | Mỗi dòng thay đổi phải truy về đúng yêu cầu |
| Test để tăng coverage | Test phải chứng minh được nó **có thể fail** |
| Review bằng cảm giác | Mỗi phát hiện phải kèm kịch bản hỏng cụ thể |

Đó là **sáu cổng**: *hiểu → tối giản → tái hiện → kiểm chứng → review → giao*. Skill chỉ
là cách đóng gói từng cổng để nó tự bật đúng lúc.

---

## 1. Sáu cổng và skill giữ cổng

```
yêu cầu
  │
  ├─① HIỂU ......... karpathy-guidelines · brainstorming · onboard-repo
  │
  ├─② TỐI GIẢN ..... karpathy-guidelines (simplicity + surgical)
  │                   restructure (khi file đã phình)
  │
  ├─③ TÁI HIỆN ..... systematic-debugging · root-cause · parallel-debugging
  │                   triage-ci (build đỏ)
  │
  ├─④ KIỂM CHỨNG ... test-driven-development · test-gaps · perf-hunt
  │                   verification-before-completion  ← chặn cứng
  │
  ├─⑤ REVIEW ....... review-diff · requesting-code-review · receiving-code-review
  │                   audit-security · parallel-debugging
  │
  └─⑥ GIAO ......... ship-pr · finishing-a-development-branch · bump-deps
```

Cổng ④ là cổng quan trọng nhất. Nó là thứ khiến "xong" có nghĩa:

```
KHÔNG TUYÊN BỐ HOÀN THÀNH KHI CHƯA CÓ BẰNG CHỨNG KIỂM CHỨNG MỚI
```

Nếu chưa chạy lệnh kiểm chứng **trong chính lượt này**, không được nói nó pass.

---

## 2. 12 skill mới thêm

### 2.1 Cách suy luận — `karpathy-guidelines`

Nguồn: `multica-ai/andrej-karpathy-skills` (MIT, 226k★). Ngắn nhất trong bộ — 2.5 KB — và
là thứ ảnh hưởng rộng nhất. Bốn điều luật:

| # | Luật | Câu chốt |
|---|---|---|
| 1 | Nghĩ trước khi code | Nêu giả định. Mơ hồ thì dừng, đặt tên chỗ mơ hồ, hỏi |
| 2 | Đơn giản trước | Code tối thiểu giải đúng bài. Không abstraction cho code dùng một lần |
| 3 | Sửa phẫu thuật | Không "cải thiện" code bên cạnh. Mỗi dòng đổi phải truy về yêu cầu |
| 4 | Mục tiêu kiểm chứng được | "Sửa bug" → "viết test tái hiện, rồi làm nó pass" |

Luật 3 có phép thử rất cụ thể: *"Mỗi dòng đã đổi phải truy trực tiếp về yêu cầu của người
dùng."* Đây chính là thứ chặn căn bệnh LLM hay mắc nhất — sửa một chỗ, phá mười chỗ.

Luật 4 là mẹo để agent tự lặp được: tiêu chí mạnh thì tự chạy đến khi xong; tiêu chí yếu
("làm cho nó chạy") thì phải hỏi liên tục.

### 2.2 Bộ kỷ luật kỹ thuật — 10 skill `tounsils`

Nguồn: `tounsils/claude-code-skills` (MIT, 10 skill, 101 KB). Repo ít sao nhưng đây là bộ
**đặc nhất** trong tất cả nguồn đã đọc: mỗi skill ứng với một việc cụ thể giữa "viết code
xong" và "giao được", và mỗi cái có một câu **từ chối**.

| Skill | Cổng | Điều nó từ chối làm |
|---|---|---|
| `root-cause` | ③ | Từ chối sửa khi chưa tái hiện. Từ chối nới timeout / thêm retry / skip test để bug biến mất |
| `review-diff` | ⑤ | Từ chối báo lỗi không kèm kịch bản hỏng cụ thể. Review **diff**, không review cả file |
| `test-gaps` | ④ | Từ chối đuổi theo % coverage. Test mới phải chứng minh nó **fail được** khi code sai |
| `restructure` | ② | Từ chối tách file theo số dòng. Tách theo **đường nối**, một lần di chuyển một commit |
| `ship-pr` | ⑥ | Từ chối viết commit message từ trí nhớ. Viết từ diff thật |
| `audit-security` | ⑤ | Từ chối liệt kê tên lỗ hổng OWASP. Phải nói *ai chạm được, bằng input nào, ra hậu quả gì* |
| `onboard-repo` | ① | Từ chối gọi thứ gì là "quy ước" khi chưa đếm số lần xuất hiện |
| `perf-hunt` | ④ | Từ chối tối ưu khi chưa có số **trước**. Mọi hằng số phải có phép suy ra |
| `triage-ci` | ③ | Từ chối làm xanh CI bằng cách tắt check. Phải tìm lỗi thật **đầu tiên**, không phải dòng log cuối |
| `bump-deps` | ⑥ | Từ chối trộn major bump với refactor trong một commit |

Ba cái đáng chú ý nhất:

**`root-cause`** — bắt đầu bằng "không tái hiện thì không sửa", rồi ba thứ rẻ tiền phải
loại trừ trước khi đọc code: *state cũ* (build cũ, cache, dev server không reload), *khác
môi trường* (version, env var, dấu phân cách đường dẫn, timezone), *không chạy đúng code
đang đọc* (module bị che, bản cài đặt lấn bản local, sai nhánh). Mỗi cái dưới một phút và
giải thích được phần lớn bug "không thể xảy ra".

Sau đó phải viết được **một câu**: *"X xảy ra vì Y."* Chưa viết được câu đó là chưa tìm ra
nguyên nhân.

**`review-diff`** — đọc **dòng bị xoá** trước, vì đó là phần bị bỏ qua nhiều nhất. Một guard
clause, null check, timeout, lock bị xoá là một phát hiện cho đến khi chứng minh ngược lại.
Rồi đọc **caller**: đổi signature mà không grep hết chỗ gọi là tự sát.

**`test-gaps`** — đảo ngược thứ tự ưu tiên: logic quyết định (giá, quyền, chuyển trạng thái,
validation, retry) → nhánh lỗi → biên → chỗ từng bị sửa. Bỏ hẳn: getter, code sinh tự động,
glue không có quyết định gì. Test những thứ đó tạo ra bộ 90% mà không bắt được gì.

### 2.3 Nhiều giả thuyết cạnh tranh — `parallel-debugging`

Nguồn: `wshobson/agents` (MIT, plugin `agent-teams`). Dùng phương pháp **ACH** — Analysis of
Competing Hypotheses. Khi bug có nhiều nguyên nhân khả dĩ, thay vì đào một giả thuyết đến
cùng, nó:

1. Sinh giả thuyết trải trên **6 nhóm lỗi** (logic, dữ liệu, đồng thời, môi trường, phụ
   thuộc, cấu hình)
2. Thu bằng chứng cho **từng** giả thuyết
3. Trọng tài: loại cái bị bằng chứng phủ định, giữ cái còn sống

Giá trị thật của nó là chống **thiên kiến xác nhận**: một khi đã tin nguyên nhân là X, ta
chỉ tìm bằng chứng ủng hộ X. ACH buộc phải tìm bằng chứng *chống lại* các giả thuyết khác.

---

## 3. Đã có từ trước, không phải thêm

| Skill | Pack | Vì sao đã đủ |
|---|---|---|
| `systematic-debugging` | code | 4 pha, sau 3 lần sửa thất bại thì buộc xét lại kiến trúc thay vì vá tiếp |
| `test-driven-development` | code | Không có code production khi chưa có test fail trước |
| `verification-before-completion` | meta, **mode core** | Cài global, luôn có mặt. "Bằng chứng trước, tuyên bố sau" |
| `requesting-` / `receiving-code-review` | code | Cách xin review và cách nhận review không phòng thủ |
| `writing-plans` / `executing-plans` | code | Kế hoạch trước, thực thi theo kế hoạch |
| `brainstorming` | code | Làm rõ yêu cầu trước khi thiết kế |

`verification-before-completion` là `mode: core` nên nằm ở `~/.gemini/config/skills/`, không
phụ thuộc profile. Đây là lý do mọi workspace đều có cổng ④ kể cả khi profile không chọn nó.

---

## 4. Nguồn đã đọc: lấy gì, bỏ gì

Sau khi bỏ license khỏi tiêu chí lọc, tiêu chí còn lại là **có trùng chức năng không**.

### Đã lấy thêm

| Nguồn | Lấy | Vì sao |
|---|---|---|
| `tounsils/claude-code-skills` | cả 10 | Sắc nhất trong tất cả — mỗi skill một việc, mỗi cái một câu từ chối |
| `multica-ai/andrej-karpathy-skills` | 1 + `references/` | SKILL.md 2.5 KB + `EXAMPLES.md` 15 KB ví dụ cụ thể + `CLAUDE.md` 2.4 KB |
| `wshobson/agents` | 31 | Thư viện theo ngôn ngữ: Python 18, TypeScript 5, general 18 |
| `tjboudreaux/cc-thinking-skills` | 6 / 28 | Chỉ 6 cái gắn với gỡ lỗi và quyết định; 22 cái còn lại là mô hình kinh doanh/tổ chức, không phải logic code |
| `Leonxlnx/taste-skill` | 1 | Design taste, 39 KB SKILL.md + thư viện mẫu. Trước đây ghi "không license" — **sai**, repo là MIT |
| `ajbmachon/ajbm-skills` | 1 | `testing-best-practices` |
| `RobMitt/grill-me-skill` | 1 (viết lại) | Phỏng vấn ngược trước khi code. Bản gốc gọi `AskUserQuestion` — Antigravity không có tool đó |

### Bỏ vì trùng, không vì license

| Skill | Trùng với |
|---|---|
| `e2e-testing-patterns` | `webapp-testing` (Playwright) |
| `multi-reviewer-patterns` | plugin `code-review` (multi-agent) |
| `task-coordination-strategies` | `subagent-driven-development` |
| `dependency-upgrade` | `bump-deps` (sắc hơn) |
| `sast-configuration`, `attack-tree-construction`, `threat-mitigation-mapping`, `security-requirement-extraction` | `audit-security` + `stride-analysis-patterns` |
| `microservices-patterns` | `architecture-patterns` |
| `monorepo-management` | quá hẹp, không phải logic code |
| `debugging-strategies` | `root-cause` (sắc hơn) |
| `code-review-excellence` | `review-diff` (sắc hơn) |
| 22/28 `thinking-*` | Mô hình tư duy chung, không gắn với code |

Bỏ 10 skill trùng làm `web-admin` từ 74 xuống 64 — không mất năng lực nào, chỉ bỏ đường
gọi trùng tên.

### Vẫn bỏ vì nội dung

| Nguồn | Vì sao |
|---|---|
| `obra/superpowers` → `diagnosing-superpowers` | Công cụ viết bug report cho chính superpowers |
| `etemigarba/Debug-and-Fix-Bugs-Skill` | 6 pha nặng bàn giấy, đã bị phủ gọn |
| `mksglu/context-mode` (44 MB) | Là **ứng dụng**, không phải skill trần |
| `thedotmack/claude-mem` (104k★) | Cũng là app Node (sqlite + UI), không phải skill |

## 5. Nối vào workspace thế nào

12 skill có `domain: ["code"]`, `families: ["logic"]`, `mode: auto`. Chúng đi theo **miền**
chứ không theo **artifact** — nên profile nào có `domain` chứa `code` là nhận.

| Profile (project TS) | Skill | Có logic skill? | Vì sao |
|---|---|---|---|
| `web-admin` | 68 | ✅ cả 12 | Dashboard/CRUD: logic là phần chính |
| `mobile-app` | 64 | ✅ cả 12 | App thật: state, navigation, API, offline |
| `cli-tool` | 52 | ✅ cả 12 | Không UI, toàn logic |
| `landing` | 34 | ❌ | Rationale: "logic mỏng". Vẫn có `verify-before-done` global |
| `design-system` | 16 | ❌ | Rationale ghi rõ: "không cần superpowers/TDD" |
| `docs-writer` | 6 | ❌ | Không viết code |
| `education-*` | 19 / 11 | ❌ | `forbid_domains: code` |

Trên project Python, `web-admin` ra 79 skill (cộng 18 skill `python-*`) và **không** có
skill `typescript-*`. Xem mục `--stacks` ở README.

### Một lỗ hổng đã sửa trong lúc làm

`mobile-app` trước đây **không có một skill debug nào**. Nguyên nhân: `select()` lọc theo
`artifact`, mà danh sách artifact của profile là `native-ui, motion` — nên mọi skill thuần
`code` bị loại, dù `domain` của profile có `code`.

Nói cách khác: khai `domain: code` rồi chặn `artifact: code` là tự vô hiệu hoá domain đó.
Đã thêm `code` vào artifact của `mobile-app`. `landing` thì **không** — rationale của nó
là "logic mỏng", và profile hẹp là điều đúng cho một landing page.

---

## 6. Kiểm chứng nó có tác dụng

Không có cách đo "logic tốt hơn" bằng máy. Nhưng kiểm được **skill có mặt và tự bật**:

```bash
# 12 skill logic nằm trong project code
python3 tools/install.py --profile web-admin -w ~/p/admin
ls ~/p/admin/.agents/skills | grep -E '^(karpathy-guidelines|root-cause|review-diff|test-gaps|restructure|ship-pr|audit-security|onboard-repo|perf-hunt|triage-ci|bump-deps|parallel-debugging)$' | wc -l
# → 12

# project design không nhận
ls ~/p/landing/.agents/skills | grep -c 'root-cause'
# → 0
```

Thử trong phiên thật, ba câu này phân biệt được có skill và không có:

| Câu thử | Có skill | Không có skill |
|---|---|---|
| "Sửa bug này" (không nói thêm) | Hỏi/tái hiện trước, hoặc nêu rõ "chưa tái hiện được" | Sửa luôn |
| "Xong chưa?" | Chạy lệnh kiểm chứng rồi trả lời kèm output | Trả lời "xong rồi" |
| "Review giúp" | Mỗi phát hiện kèm kịch bản hỏng | Liệt kê góp ý chung chung |

---

## 7. Ánh xạ sang Claude Code

| Của Claude Code | Ở đây |
|---|---|
| Kỷ luật nằm trong system prompt + binary | Đóng gói thành skill, cài vào workspace theo profile |
| Không chọn được, không tắt được | `--profile` quyết định; skill ngoài domain **vắng khỏi đĩa** |
| `verification-before-completion` là một plugin | `mode: core` → cài global, luôn bật |
| Không có skill tái hiện/nhiều giả thuyết | Thêm `root-cause` + `parallel-debugging` |
| Không có bộ kỷ luật theo từng việc | 10 skill `tounsils`, mỗi cái một việc |
