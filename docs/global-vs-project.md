# Global hay theo-project: đo rồi mới chọn

Antigravity có **đúng hai phạm vi skill** — `~/.gemini/config/skills/` (mọi project đều thấy)
và `<project>/.agents/skills/` (chỉ project đó). Skill global **không thể bị project con ẩn
đi**: hai tầng chỉ cộng vào nhau. Đó là ràng buộc của nền tảng, không phải lựa chọn thiết kế.

Vì vậy "kho tổng" và "tầng global" là hai thứ khác nhau, và repo này tách sẵn:

```
Kho tổng   = repo đã clone (packs/ 234 skill + VENDOR.json)
             bootstrap.sh cache ở ~/.cache/antigravity-skill-os/
                  │
                  ├─► install.py --system   → ~/.gemini/config/skills/   (bản đã triển khai)
                  ├─► install.py --core     → 4 skill + AGENTS.md
                  └─► install.py --profile  → <project>/.agents/skills/
```

`~/.gemini/config/skills/` **không phải** kho tổng — nó là bản sao đã triển khai. Muốn đổi
bộ skill thì sửa registry rồi chạy lại, không sửa trực tiếp trong đó.

## Ba mô hình, đo bằng `install.py` trên máy

Token = description của skill đang bật + `AGENTS.md`, trần Antigravity 20.000.

**Đồng hồ của Antigravity đếm cao hơn ước lượng của `install.py` khoảng 1/4.** Hồi quy từ hai
lần đo trong Settings → Skills (195 skill = 21.430 token, 204 skill = 22.350): UI ≈
`1.497 + 102,2 × số skill`. Con số của `install.py` là **sàn**; `install.py` giờ in cả hai dòng.

| Mô hình | Lệnh | Global | Token mỗi phiên | Project thấy |
|---|---|---|---|---|
| **A. Toàn máy** | `bootstrap.sh --system` | 186 skill | 16.500 ≈ 82% → **UI 103%** | 186 + skill riêng |
| **A′. Toàn máy gọn** ← khuyên dùng | `bootstrap.sh --system --exclude-pack education,docs` | 156 skill | 13.554 ≈ 68% → **UI 87%** | 156 + skill riêng |
| **B. Global mỏng** | `--core` rồi `bootstrap.sh <profile> <dir>` | 4 skill | 1.296 (global) + của project | 4 + skill của profile |

Token thật của từng workspace ở mô hình B (4 skill global + profile rót vào):

| Workspace | Skill | Token | So với A |
|---|---|---|---|
| `education-k12` | 28 | **4.056** | −75% |
| `docs-writer` | 20 | **3.255** | −80% |
| `landing` | 56 | **5.818** | −65% |
| `cli-tool` | 138 | 11.123 | −33% |
| `desktop-app` | 161 | 13.474 | −18% |
| `web-admin` | 171 | 14.044 | −15% |

Đọc bảng này ra một kết luận ít ai nói: **với project code, B gần như không tiết kiệm gì**
(14.0k so với 16.5k) — vì bản thân profile code đã 102–171 skill. B chỉ thắng đậm ở workspace
**giáo dục, tài liệu, landing** — nơi A đang nạp thừa 150 skill code không bao giờ dùng.

## Đánh đổi thật

| | A `--system` | B `--core` + profile |
|---|---|---|
| Cài lần đầu | 1 lệnh | 1 lệnh global + 1 lệnh mỗi project mới |
| Project mới | không làm gì | `bootstrap.sh <profile> <dir>` |
| Cập nhật skill | chạy lại 1 lệnh, mọi project theo | phải chạy lại từng project |
| Danh sách skill trong App | 186 dòng ở **mọi** workspace | chỉ skill đúng việc |
| Cô lập domain | **không có** — project giáo dục vẫn thấy `springboot-security` | có, đúng như thiết kế |
| Token | 103% (vượt trần → bị loại bớt) | 87% ở A′, 16–70% ở B |

## Khuyến nghị

1. **Đang làm việc đa dạng (giáo án, slide, tài liệu, web)** → A′: giữ toàn máy nhưng bỏ hẳn
   `education,docs` khỏi global, project nào cần thì rót. 68% ngân sách, project giáo dục sạch.
2. **Chỉ làm code** → A. Danh sách 186 dòng có ồn, nhưng skill nào cũng có thể dùng, và không
   phải nhớ lệnh cho từng folder.
3. **Cần cô lập thật** (yêu cầu gốc: "skill giáo dục phải vắng khỏi workspace web-admin") →
   B. Không có cách nào khác: global bật bao nhiêu skill thì mọi project thấy bấy nhiêu.

### B chạy bằng hai lệnh (đã có sẵn)

```bash
bash bootstrap.sh --core --prune     # global: rules + 4 skill ≈ 10% ngân sách
bash bootstrap.sh auto ~/p/btvn      # mỗi project: tự dò profile rồi rót
```

`--core --prune` gỡ luôn 182 skill global của bản `--system` trước đó. Đo thật:

| Workspace | Skill (global+riêng) | Ước lượng | Đồng hồ Antigravity |
|---|---|---|---|
| `btvn` (giáo án) | 4 + 24 = 28 | 4.104 ≈ 21% | ≈ 22% |
| `SlidePPT` | 4 + 16 = 20 | 3.303 ≈ 17% | ≈ 18% |
| `web-admin` (Next/TS) | 4 + 167 = 171 | 14.092 ≈ 70% | ≈ 95% |
| `cli-tool` | 4 + 134 = 138 | 11.170 ≈ 56% | ≈ 78% |
| `landing` (HTML tĩnh) | 4 + 52 = 56 | 5.866 ≈ 29% | ≈ 36% |

Chọn A mà vẫn muốn cô lập thì phải chọn lại: **hai thứ đó loại trừ nhau**.

## Hai lỗi đã sửa khi kiểm chuyện này

- **Skill trùng**: `--system` rồi rót profile vào project thì trước đây chép **lại** cả 24
  skill đã có ở global (đĩa ×2, description ×2). Giờ `install.py` bỏ qua và in
  `= 24 skill đã có ở global — không chép lại`.
- **Cảnh báo sai**: khi cả hai tầng cùng bật, lệnh cài project giờ in rõ
  `⚠ global đang bật 186 skill: project này vẫn thấy hết. Cô lập đúng chỉ khi global mỏng`.
- **Skill sót lại**: skill bị bỏ khỏi registry ở bản cũ vẫn nằm trong `config/skills/`, ăn
  ngân sách và hiện ở mọi project. Giờ `--system` liệt kê tên, `--prune` dọn (chỉ xoá thư mục
  do Skill OS tạo). Đây cũng là lý do hay thấy **190** thay vì 186: 4 skill `mode: manual`
  (`vercel-byoc`, `vercel-cli-with-tokens`, `brand-guidelines`, `skill-creator`) từ lần cài
  có `--include-manual`.

## Skill tự dò sai thì sao

`--profile auto` chỉ là **gợi ý**, nó luôn in lý do trước khi cài. Ba thứ từng làm nó sai, nay
đều có test ([`tools/test_guess.py`](../tools/test_guess.py), 20/20):

- Đọc luôn `.agents/skills` của lần cài trước → có script `.py` nên đoán thành `cli-tool`.
- Workspace nằm dưới `…/.gemini/…`, `…/build/…`, `…/target/…` → mọi file bị loại, báo "thư mục
  trống". Đây là lỗi thật trên máy Windows của user, nơi repo ở `…/.gemini/antigravity/scratch/`.
- Trang HTML tĩnh (chỉ `index.html`) không khớp profile nào → trả `None`.
