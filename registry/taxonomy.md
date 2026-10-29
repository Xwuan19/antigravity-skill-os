# Taxonomy — cách phân loại skill

Mục tiêu: khi mở một project, Antigravity **chỉ thấy** những skill liên quan. Skill giáo
dục không bao giờ xuất hiện trong project web quản lý — không phải vì bị dặn "đừng dùng",
mà vì **nó không tồn tại trong workspace đó**.

## Điểm mấu chốt: chọn lúc cài, không phải lúc chạy

| Thời điểm | Cơ chế | Ai quyết |
|---|---|---|
| **Lúc cài** (1 lần / project) | `tools/route.py` đọc profile rồi copy đúng skill vào `<workspace>/.agents/skills/` | Router (tất định, script) |
| **Lúc chạy** (mỗi lượt) | Antigravity progressive disclosure: thấy tên + description, tự đọc `SKILL.md` khi khớp | Model (xác suất) |

Antigravity **không tự cài** skill theo loại project — nó chỉ tự *chọn trong số đã có*.
Nên bước tất định phải nằm ở khâu cài. Cô lập bằng **vắng mặt** mạnh hơn cô lập bằng
**mệnh lệnh**: một skill không có trong `.agents/skills/` thì không có cách nào được gọi.

## Bốn trục

Mỗi skill khai báo trong [`registry/skills.json`](skills.json):

### 1. `domain` — lĩnh vực

| Giá trị | Nghĩa | Gói |
|---|---|---|
| `code` | Viết/sửa/debug code, quy trình phát triển | superpowers, vercel-react |
| `design` | Hướng thẩm mỹ, typography, layout, copy | frontend-design, theme-factory |
| `motion` | Chuyển động, gesture, spring, interruptibility | emilkowalski |
| `education` | Sư phạm, giáo án, đánh giá | edu-agents, language-teaching |
| `docs` | Xuất Word/PDF/PPTX/XLSX | anthropics doc suite |
| `meta` | Nuôi chính hệ thống skill | writing-skills, skill-creator |

`*` = áp dụng mọi domain.

### 2. `phase` — pha công việc

`discover` → `plan` → `build` → `verify` → `review` → `ship`

Trùng với 7 bước của superpowers. Cho phép chọn theo giai đoạn: project mới cần
`discover`+`plan`, project đang bảo trì cần `verify`+`review`.

### 3. `artifact` — sản phẩm chạm tới

`code` · `web-ui` · `native-ui` · `motion` · `api` · `document` · `slide` · `sheet` ·
`pdf` · `lesson` · `image` · `video`

Đây là trục **lọc tinh** — thứ phân biệt "web quản lý" với "design system":
cùng domain `design`, nhưng design-system cần `motion`, web-admin thì ưu tiên `web-ui` thuần.

### 4. `mode` — cách nạp

| mode | Nơi nằm | Chi phí | Ai kích hoạt |
|---|---|---|---|
| `system` | `~/.gemini/AGENTS.md` | Luôn tốn (~1.300 token) | Không cần — luôn bật |
| `core` | global `.agents/skills` | 1 dòng description | Model tự chọn |
| `auto` | theo workspace, do router cài | 1 dòng khi idle | Model tự chọn, khớp description |
| `manual` | như trên | 0 dòng (mặc định không cài) | Chỉ khi `--include-manual` rồi gõ `/tên` |

Ponytail nằm ở `system`. **Không có mode nào khác cho nó.**

## Trục phụ: `families`

Dùng khi hai bộ skill cùng domain nhưng không được trộn:

- `families: ["k12"]` — edu-agents (soạn giáo án phổ thông)
- `families: ["language"]` — language-teaching (dạy ngoại ngữ)

Skill **không khai** `families` = khớp mọi họ. Skill **có khai** = chỉ khớp profile cùng họ.
Không có trục này thì mở project K-12 sẽ thấy cả `lesson-planning` của bộ ngoại ngữ.

## Hàng rào cứng: `forbid_domains`

Profile khai domain bị cấm, router loại **tuyệt đối** — kể cả skill khớp ở trục khác.

```json
"forbid_domains": ["education"]
```

Đây là chốt chặn cho yêu cầu "chắc chắn không lấy skill giáo dục ra". Ba lớp bảo vệ:

1. Router không chọn → không cài
2. Không có file → Antigravity không thấy trong danh sách skill
3. Không có tên → không thể gõ `/` để gọi

## Profile

9 kiểu project dựng sẵn trong [`profiles/`](../profiles):

| Profile | Skill | Thành phần | Dùng cho |
|---|---|---|---|
| `web-admin` | 28 | code 16, design 6, motion 6 | Dashboard, CRUD, SaaS |
| `landing` | 25 | code 8, design 6, motion 11 | Landing, marketing, portfolio |
| `mobile-app` | 17 | code 6, design 1, motion 10 | React Native, Expo, iOS/Android |
| `design-system` | 15 | design 5, motion 10 | UI kit, component library |
| `cli-tool` | 13 | code 13 | CLI, script, backend |
| `education-k12` | 19 | education 14, docs 5 | Giáo án phổ thông, đề kiểm tra |
| `education-language` | 11 | education 9, docs 2 | Trung tâm ngoại ngữ, gia sư |
| `docs-writer` | 6 | docs 5, design 1 | Báo cáo, thuyết trình, bảng tính |

Thêm profile mới = thêm một file JSON. Không cần sửa code.

Tổng registry: **75 skill** (72 vendor + 3 rule hệ thống) + 46 subagent + 9 plugin. Toàn bộ đã nằm trong `packs/`,
pin commit, nên cài đặt không cần mạng.

## Ví dụ chạy

```bash
# cài phần global (rules + skill luôn có mặt)
python3 tools/install.py --core

# xem có profile gì
python3 tools/install.py --list

# cài vào project thật
python3 tools/install.py --profile web-admin -w ~/projects/shop-admin

# xem trước, không ghi gì
python3 tools/install.py --profile landing -w ~/p/landing --dry-run

# project lạ, chưa có profile → suy từ tags (router, không cài)
python3 tools/route.py --tags dashboard,design
```

Cài xong, `.agents/skill-os.json` được ghi vào workspace để lần sau biết project này
thuộc profile nào mà không cần đoán lại.

Installer **không bao giờ** xoá thư mục skill không do nó tạo (đánh dấu bằng
`.skill-os-owner`); muốn ghi đè phải `--force`. Gỡ bằng `--uninstall`, và lệnh đó
chỉ đụng phần global — skill trong workspace giữ nguyên.
