# ECC: lấy 53 skill từ kho 313

Repo [`affaan-m/ECC`](https://github.com/affaan-m/ECC) (MIT) @
`91b5f6a371f7b06d2c3e0c208147c559e11f022c`.

## Vì sao phải khảo sát lại

Lần đầu (sub-task 10) mình chỉ nhìn `.agents/skills/` — **47** skill — và kết luận repo
không dùng được mấy. Sai. `git ls-tree -r --name-only | grep -c 'SKILL\.md$'` trên **toàn
cây** ra **1.066** file; thư viện chính nằm ở **`skills/` gốc: 313 skill**, gấp 6,7 lần con
số đã xem. Bài học ghi vào đây để không lặp lại: đếm trên toàn cây trước khi đánh giá.

Sau khi trừ trùng tên với registry cũ (5) và quét từ khoá Claude/slash/hook, còn **244** ứng
viên. Đọc description từng cái, loại tiếp phần trùng **chủ đề** (không chỉ trùng tên), còn
**53 skill** được lấy — trong đó 3 skill đã có từ trước được dời sang commit mới.

## Đã đổi gì khi port

Skill của ECC viết cho Claude Code, nên port không phải copy:

| Vấn đề | Cách xử lý | Số skill |
|---|---|---|
| Trỏ `~/.claude/skills`, `${CLAUDE_SKILL_DIR}` | `patch`: thay bằng `~/.gemini/config/skills/…`, `${SKILL_DIR:-$HOME/.gemini/config/skills/<id>}` — `eval-harness`, `rules-distill`, `skill-scout`, `issue-review`, `planning-with-files` | 5 |
| Cả một khối cài đặt/hook riêng của ECC nằm giữa bài | `cut`: xoá từ mốc đầu tới mốc cuối (`docker-patterns` mất khối installer, `planning-with-files` mất toàn bộ phần hook/slash) | 2 |
| Frontmatter mang `hooks:`, `allowed-tools:`, `user-invocable:` của Claude Code | `fm_desc`: viết lại frontmatter chỉ còn `name` + `description` | 5 |
| Description dài 700–2.800 ký tự, ăn ngân sách always-on | gộp vào `fm_desc` ở trên | 5 |
| `.claude/reviews/` trong ví dụ | `patch` → `.agents/reviews/` (`issue-review`) | 1 |

Sau khi port, quét lại **toàn bộ 234 `SKILL.md`**: `0` file còn `CLAUDE_`, `~/.claude/`
hay `.claude/`. Hai lần vendor cuối còn sửa thêm 3 skill cũ (`mac-design`,
`mac-design-from-app`, `writing-skills`) vẫn dùng `${CLAUDE_SKILL_DIR}` — lệnh trong đó sẽ
fail trên Antigravity. Quét này là quét **rộng** — lần đầu mình quét hẹp
(`ecc-cmd|slash|claude|subagent|hooks`) và nó báo "0 sót", trong khi vẫn còn 3 file dính
`.claude/`.

## 9 skill vào toàn máy (`--system`)

Đây là skill kiến trúc/quy trình/design — có nghĩa với mọi project, không phụ thuộc stack.

| Skill | Pack | Stack | Việc nó làm |
|---|---|---|---|
| `accessibility` | design | — | WCAG 2.2 AA cho web + iOS + Android: ARIA, focus, tương phản, screen reader. |
| `agent-introspection-debugging` | meta | — | Agent lặp tool, đốt token không tiến triển: capture → chẩn đoán → gỡ rối có kiểm soát. |
| `architecture-decision-records` | code | — | Ghi quyết định kiến trúc thành ADR đánh số trong docs/adr/ + index. |
| `change-impact` | code | — | Đo tác động trước khi sửa: call path, schema, API, test, migration, rollback. So bản kế hoạch với diff thật sau khi xong. |
| `contract-first` | code | — | Một hợp đồng máy kiểm được (OpenAPI/AsyncAPI) làm nguồn chân lý cho cả hai phía. |
| `eval-harness` | code | — | Khung eval chính thức: định nghĩa tiêu chí, chạy, chấm, chốt trước khi tin một workflow. |
| `hexagonal-architecture` | code | — | Ports & Adapters: domain sạch, phụ thuộc đảo chiều, use-case test được. |
| `issue-review` | code | — | Review GitHub issue như review PR: kiểm báo cáo với code thật rồi mới kết luận. |
| `production-audit` | code | — | Audit sẵn sàng production từ bằng chứng cục bộ, trước khi phát hành. |

## 44 skill chỉ vào project đúng stack

Bật toàn máy những skill này là sai: `springboot-security` không có nghĩa trong project
Python, mà lại chiếm một dòng description trong **mọi** phiên. Nên chúng khai
`"global": false` — `--system` bỏ qua, `--profile` cài khi workspace đúng ngôn ngữ.

| Skill | Pack | Stack | Việc nó làm |
|---|---|---|---|
| `angular-developer` | code | typescript | Angular hiện đại: standalone, signal, routing, DI. |
| `cpp-coding-standards` | code | cpp | C++ Core Guidelines: ownership, RAII, const, lỗi. |
| `cpp-testing` | code | cpp | GoogleTest/Catch2, sanitizer, coverage trong C++. |
| `csharp-testing` | code | csharp | xUnit/NUnit, mock, test async, coverage trong C#. |
| `deployment-patterns` | code | — | Chiến lược triển khai: blue-green, canary, rollback, health check. |
| `django-patterns` | code | python | Django + DRF: cấu trúc project, ORM, cache, signal, middleware. |
| `django-security` | code | python | Auth, phân quyền, CSRF, XSS, SQLi cho Django. |
| `django-tdd` | code | python | pytest-django, factory_boy, mock, coverage. |
| `docker-patterns` | code | — | Dockerfile nhiều tầng, Compose, bảo mật container, volume, mạng. |
| `fastapi-patterns` | code | python | FastAPI: Pydantic v2, DI, async, cấu trúc project. |
| `flutter-dart-code-review` | code | dart | Review Flutter/Dart: widget, state, layout, hiệu năng. |
| `fsharp-testing` | code | fsharp | xUnit/Expecto, property-based trong F#. |
| `golang-testing` | code | go | Bảng test, benchmark, fuzz, mock, coverage trong Go. |
| `jpa-patterns` | code | java | JPA/Hibernate: mapping, fetch, transaction, N+1. |
| `kotlin-exposed-patterns` | code | kotlin | Exposed ORM: DSL, DAO, transaction, pool. |
| `kotlin-ktor-patterns` | code | kotlin | Ktor: routing DSL, plugin, auth, Koin, serialization. |
| `kotlin-patterns` | code | kotlin | Kotlin hiện đại: null-safety, data class, coroutine, DSL. |
| `kotlin-testing` | code | kotlin | Kotest, MockK, test coroutine, property-based, Kover. |
| `kubernetes-patterns` | code | — | Workload, resource limit, probe, RBAC, autoscaling, Secret. |
| `laravel-patterns` | code | php | Laravel: cấu trúc, Eloquent, queue, event. |
| `laravel-security` | code | php | Auth, phân quyền, Eloquent an toàn, CSRF, XSS. |
| `laravel-tdd` | code | php | PHPUnit/Pest, factory, HTTP test, Sanctum. |
| `liquid-glass-design` | design | — | Liquid Glass iOS 26: vật liệu, blur, phản chiếu, morph, cho SwiftUI và web. |
| `make-interfaces-feel-better` | design | — | Chi tiết làm giao diện 'xịn': nhịp khoảng cách, trạng thái, chuyển động nhỏ. |
| `mcp-server-patterns` | code | — | Viết MCP server: khai báo tool, schema, lỗi, phân quyền. |
| `mybatis-patterns` | code | java | MyBatis: mapper, XML, result map, dynamic SQL an toàn. |
| `mysql-patterns` | code | — | MySQL: index, explain, transaction, isolation, schema design. |
| `nestjs-patterns` | code | typescript | NestJS: module, provider, guard, interceptor, pipe. |
| `nuxt4-patterns` | code | typescript | Nuxt 4: cấu trúc thư mục, data fetching, SSR/ISR. |
| `perl-patterns` | code | perl | Perl hiện đại: strict/warnings, object, xử lý lỗi. |
| `perl-testing` | code | perl | Test::More, prove, mock trong Perl. |
| `prisma-patterns` | code | typescript | Prisma: schema, migration, quan hệ, transaction. |
| `quarkus-patterns` | code | java | Quarkus 3.x + Camel: REST, CDI, data access. |
| `quarkus-security` | code | java | Quarkus security: OIDC, JWT, vai trò. |
| `quarkus-tdd` | code | java | Quarkus test: JUnit 5, Mockito, REST Assured, JaCoCo. |
| `rails-patterns` | code | ruby | Rails: MVC, ActiveRecord, concern, service object. |
| `redis-patterns` | code | — | Redis: khoá, TTL, cache-aside, lock, rate limit, pipeline. |
| `rules-distill` | meta | — | Quét skill rồi chưng cất nguyên tắc cắt ngang thành file rule. |
| `skill-scout` | meta | — | Tìm skill có sẵn ở local/GitHub/web trước khi viết skill mới. |
| `springboot-patterns` | code | java | Spring Boot: REST, service tầng, data access, cache, async. |
| `springboot-security` | code | java | Spring Security: xác thực, phân quyền, JWT, CORS. |
| `springboot-tdd` | code | java | JUnit 5 + Mockito + MockMvc cho Spring Boot. |
| `vite-patterns` | code | typescript | Vite: cấu hình, plugin, tối ưu build, chia chunk. |
| `vue-patterns` | code | typescript | Vue 3: composition API, reactivity, composable, router. |

Stack ở trên chính là cái router dùng (`tools/skillselect.py`): workspace có `.java` thì mới
nhận 9 skill Java, có `.dart` mới nhận `flutter-dart-code-review`, có `.pl`/`.pm` mới nhận
`perl-*`, `.fs`/`.fsx` mới nhận `fsharp-testing`.

## Đã cân nhắc và loại

| Loại vì | Skill |
|---|---|
| Trùng chủ đề đã có | `golang-patterns` (đã có `go-strict` + rules), `react-patterns`/`nextjs-turbopack`/`vercel-react-view-transitions` (đã có 5 skill React + rules TS), `error-handling-patterns` (đã có `error-handling`), `codebase-onboarding`/`code-tour` (đã có `codebase-inspection`), `database-migration` (đã có `database-migrations`) |
| Quá mỏng | `*‑verification` của springboot/quarkus/laravel/django (3,8–6 KB, rules đã phủ), `web-design-guidelines` (1,2 KB) |
| Cần hạ tầng Claude Code | `gateguard` (hook `PreToolUse`), `security-scan` (quét `.claude/`), `repo-scan` (con trỏ cài skill ngoài), `context-budget` (đo meter Codex/Claude), `continuous-learning` (đã DEPRECATED), `golang-verification` |
| Cần MCP ngoài | `deep-research` (firecrawl + exa) |
| Riêng của ECC | `frontend-design-direction` ("ECC-specific"), `token-budget-advisor`, `coding-standards`, `intent-driven-development`, `verification-loop`, `iterative-retrieval` |

## Ngân sách sau khi thêm

`--system` từ 180 → **186 skill** (193 global − 3 skill hệ thống − 4 manual), cộng `AGENTS.md`
5.185 ký tự → **16.481 token ≈ 82% trần 20k** (con số `install.py --system` in ra). Đây là
lý do 44 skill kia **không** được đưa vào toàn máy: thêm nữa là vượt trần, và phần vượt
toàn là skill không bao giờ dùng trong project hiện tại.
