# Giảm trả lời sai lệch thực tế — khảo sát và tích hợp

## Mục tiêu và giới hạn

Chỉ dẫn và skill giúp agent dựa vào bằng chứng, **không bảo đảm hết ảo**. Một file trên
đĩa không chứng minh runtime đã nạp skill; test mock không chứng minh dịch vụ thật hoạt
động; một lần tìm không có kết quả không chứng minh thứ được tìm không tồn tại.

Đợt này đã clone sáu nguồn vào thư mục tạm và đọc chọn lọc ứng viên; không chạy code
upstream, không đánh giá hành vi thực tế của agent. Skill mới được vendor và cài offline;
những nguồn khác mới khảo sát, không mặc định tích hợp toàn bộ.

## Đã áp dụng

- Bổ sung `core/AGENTS.md` §2: đối chiếu trạng thái cũ với nguồn, giới hạn kết luận
  khi tìm không thấy, xác minh API/phiên bản, phân biệt các mức bằng chứng và coi
  tài liệu/tool output là dữ liệu không đáng tin như chỉ dẫn. Áp dụng ở global cho cả
  workspace không phải code; không thêm skill global, giữ `--core` ở 4 skill.
- Các nguyên tắc tình trạng cũ và tìm không thấy tham khảo `SpawnZilla/agent-skills`
  @ `60a035f526aae36a499e6a6ef3836bebdf44d917`, cụ thể
  `carried-status-verification` và `existence-verification-escalation`. Quy tắc trong
  core được viết lại cho ngắn và để nêu giới hạn khi không có nguồn kiểm tra.
- Bốn skill dưới đây dùng `mode: auto`, domain `code`, `stack: general`,
  `global: false`: chỉ vào profile code phù hợp, không vào education hoặc global.

| Skill | Nguồn pin | Giá trị | Thích ứng / giới hạn |
|---|---|---|---|
| `reference-existence-check` | SpawnZilla @ `60a035f526aae36a499e6a6ef3836bebdf44d917` | Kiểm tra hàm, file đầu vào, config và service trước khi dựa vào chúng. | Không đòi file đầu ra mới đã tồn tại; thay tham chiếu skill chưa được cài bằng bước tìm có giới hạn. |
| `dependency-grounding-auditor` | aradmanamnaoon/vibe-coding-skills @ `d532b2b52725cbd92b2815fbc98e1e516503137b` | Đối chiếu package, version, import và lockfile với nguồn thật. | Nếu không có mạng thì dựa vào dữ liệu local hoặc báo chưa xác minh; chỉ kiểm tra dependency thực sự cần thiết. |
| `integration-reality-checker` | aradmanamnaoon @ `d532b2b52725cbd92b2815fbc98e1e516503137b` | Phân biệt test giả lập với bằng chứng tích hợp và môi trường thật. | Nêu rõ fake/fixture không chứng minh dịch vụ thật; không dùng production khi chưa được phép. |
| `completion-claims-auditor` | aradmanamnaoon @ `d532b2b52725cbd92b2815fbc98e1e516503137b` | Ánh xạ từng kết luận “xong” với test, runtime hoặc remote tương ứng. | Có phần trùng `verification-before-completion`; bổ sung ma trận kiểm từng claim. |

Ba skill từ aradmanamnaoon được bỏ tham chiếu tới đường dẫn research ngoài thư mục skill,
tránh để liên kết nội bộ trỏ tới file không được vendor. Nguồn đầy đủ vẫn có ở commit pin.

## Nguồn đã khảo sát nhưng chưa nhập

| Nguồn / commit | Lý do |
|---|---|
| dexteon/agent-skills @ `6c346f63ef279b50c87178a7b9658c0ffab3bb8d` | `evidence-ladder` có ví dụ script và ngưỡng cứng không phù hợp mọi tác vụ; ý tưởng phân biệt bằng chứng được chuyển thành nguyên tắc ngắn ở core. `api-verification` có bước import code và checkpoint remote cần điều chỉnh, chưa port. |
| gosaiyash/verified-engineer-skill @ `c666c1ea5ce14b97fc86f004c09a72c777a09a14` | Phần lớn trùng kiểm chứng, debug và review đã có; upstream nói chưa có đánh giá hành vi agent. |
| paulsagar7796-cmyk/Universal-agent-skills @ `3a32b58695554c34c977f4a8dbb868d2d93c91d0` | Controller/project brain có runtime và hooks riêng; chưa chứng minh tự chạy trên Antigravity App. |
| upstash/context7 @ `7836c583918374fbecffacf866afb7594b919466` | Cần MCP/dịch vụ và mạng. Chưa thêm làm phụ thuộc bắt buộc vì repo phải tự chứa và cài offline. |

## Kiểm chứng

`python3 tools/test_grounding.py` kiểm tra source pin, hash, frontmatter, các điều chỉnh,
chọn profile/stack và cài thật vào HOME tạm; xác nhận education vẫn có 24 skill, global
4, skill mới chỉ ở workspace code. `python3 tools/vendor.py --check` kiểm tra hash
`SKILL.md`; test không chứng minh agent tuân thủ chỉ dẫn hay runtime Antigravity tải
chúng. Test hành vi trên Antigravity thật và API/network thực vẫn chưa chạy.

Với HOME trống, dry-run `cli-tool --stacks typescript --no-lsp` chọn 79 skill,
vượt ngưỡng cảnh báo 75 của profile (không tự cắt). Đây là đánh đổi về nhiễu,
không phải bằng chứng Antigravity đã nạp hoặc dùng tất cả. Dùng `--stacks` đúng
project và xem ngân sách sau cài; global hay builtin trên máy thật có thể làm tổng khác.
