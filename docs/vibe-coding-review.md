# Khảo sát nguồn vibe coding — đợt 1

Mục tiêu là bổ sung **phần có ích**, không cài toàn bộ catalog vào global. Đã tải
năm repo vào thư mục tạm, kiểm kê file `SKILL.md`, đọc chọn lọc nội dung và phụ thuộc;
với agentic-awesome-skills đã lấy cây GitHub đầy đủ và tải bốn ứng viên để đọc, **chưa
đọc toàn bộ catalog**. Các bản nguồn được pin commit khi đưa vào registry.

## Đã đưa vào

| Skill | Nguồn / commit | Review và phân tầng |
|---|---|---|
| `vitest-skill` | LambdaTest/agent-skills @ `992638bccbc311f42c0bd8b2b3387a0d1ce6288d` | Vitest, bổ sung patterns testing JS/TS đã có; stack `typescript`. |
| `mocha-skill` | Như trên | Mocha/Chai/Sinon; stack `typescript`. |
| `nunit-skill` | Như trên | NUnit, bổ sung ví dụ framework cho C#; stack `csharp`. |
| `xunit-skill` | Như trên | xUnit, bổ sung ví dụ framework cho C#; stack `csharp`. |
| `rspec-skill` | Như trên | RSpec, ví dụ test Ruby; stack `ruby`. |
| `phpunit-skill` | Như trên | PHPUnit, ví dụ test PHP; stack `php`. |
| `test-fixing` | sickn33/agentic-awesome-skills @ `753c5f7bb64650b7d3ac0ab84d9b24892d7aed8b` | Gom lỗi theo nguyên nhân và xác minh, không làm yếu test. Các ví dụ `uv run` được đổi thành `pytest` để không tự đồng bộ môi trường. |

Tất cả là domain `code`, project-only (`global: false`), dùng offline sau khi clone repo.
Đã giữ các file tham khảo đi kèm. Sáu skill framework có hướng dẫn setup upstream: Skill OS
thêm lưu ý ưu tiên dependency sẵn có, không tự cài hoặc chạy setup cần mạng khi chưa kiểm tra
môi trường và quyền. Mẫu code là ví dụ, phải điều chỉnh theo phiên bản framework của project;
chưa chạy từng snippet trên mọi framework/version.

## Chưa lấy / cần điều tra tiếp

| Nguồn | Trạng thái |
|---|---|
| LambdaTest JUnit 5 | Nguồn trỏ tới file không tồn tại; đã sửa tham chiếu trong đợt 2, xem bên dưới. |
| LambdaTest accessibility, Appium và các skill cloud | Một số phụ thuộc hoặc quảng bá TestMu cloud; chưa đạt yêu cầu offline. Phần còn lại của 74 file chưa được review từng skill. |
| agentic-awesome-skills | API cây có 2.877 skill canonical; đã đọc chọn lọc 4 ứng viên, chưa review toàn bộ. `test-fixing` được lấy; các ứng viên khác chưa nhập vì trùng phạm vi hoặc cần review thêm scripts. |
| impeccable @ `02523aec3e4c4580102d996d1b6a71fbe062e03f` | Skill chính gọi launcher, có thể tải binary, và dùng biến Claude; chưa đạt yêu cầu self-contained/port. |
| spec-kit @ `2a23a848f888de05f0107061d45232c485d6bae0` | Chủ yếu toolkit/workflow, không lấy nguyên runtime; cần nghiên cứu port logic và so với quy trình đã có. |
| Agent-Skills-for-Context-Engineering @ `9ff0c99108b36d3b886defd825d8ac1f47dba374` | Đã kiểm kê và đọc chọn lọc; nhiều skill dành cho xây agent hơn công việc code hàng ngày, chưa xác định phần bổ sung không trùng. |
| debug-skill @ `26ef325fe2188209d053f42a6ca0000942a94932` | Yêu cầu cài `dap` và debug adapter; chưa vendor runtime và kiểm chứng offline. |
| playwright-mcp, vibe-testing | Chưa tải hoặc tích hợp; là MCP/runtime riêng, không coi là skill offline. |

## Kiểm tra có thể chạy lại

`python3 tools/test_vibe_skills.py` kiểm tra từng skill trong đợt: frontmatter, tên,
kích thước, reference, symlink, một số dấu hiệu lệnh không an toàn / đường dẫn Claude,
commit/hash, phân tầng và cài thử cách ly project. Có test âm chứng minh reference
thiếu bị phát hiện. Đây là **kiểm tra tĩnh có giới hạn**, không chứng minh an toàn tuyệt
đối hoặc kiểm chứng chất lượng từng ví dụ trên runtime thật. Chạy thêm
`python3 tools/vendor.py --check`, `python3 tools/test_guess.py` và
`python3 tools/test_lsp_bridge.py` để hồi quy hệ thống hiện có.

## Đợt 2 — bổ sung và giới hạn

Đã kiểm kê tự động cả 74 `SKILL.md` của LambdaTest theo dấu hiệu cloud và reference
thiếu. Đây chỉ là sàng lọc máy, **không phải review toàn bộ nội dung**. Đã đọc chọn lọc
và bổ sung thêm:

| Skill | Phân loại | Kiểm tra / điều chỉnh |
|---|---|---|
| `pytest-skill`, `unittest-skill` | Python | Mẫu pytest/unittest cụ thể, bổ sung skill test Python tổng quát đã có. Kiểm tra cú pháp các block Python; chạy mẫu unittest đầu tiên với `Calculator` giả. |
| `junit-5-skill`, `testng-skill` | Java | Mẫu framework cụ thể. JUnit trỏ file Spring không tồn tại: đã thay bằng hướng dẫn dùng cấu hình và tài liệu project. |
| `mstest-skill` | C# | Bổ sung MSTest cho project đã dùng framework này. |
| `testunit-skill` | Ruby | Test::Unit, khác với RSpec. |
| `jest-skill`, `jasmine-skill` | JS/TS | Mẫu riêng cho hai framework, bổ sung skill testing JS tổng quát. |
| `lint-and-validate` | Code chung | Chỉ lấy hướng dẫn lint/typecheck và báo kiểm tra chưa chạy; bỏ hai script upstream để tránh bổ sung runtime/hành vi chạy lệnh chưa cần thiết. |

Các skill dùng cùng commit pin và quy tắc project-only của đợt 1. Cả 16 skill mới
được kiểm tra metadata, hash, reference và dấu hiệu rủi ro, chọn stack, loại khỏi
giáo dục/global; test cài thật dùng HOME tạm. Kiểm tra cú pháp không chứng minh mẫu
chạy đúng: pytest và các framework khác chưa được cài/chạy trong sandbox.

AAS có 2.877 đường dẫn `SKILL.md` dưới `skills/`, tương ứng 2.775 tên thư mục
cấp đầu; so khớp với registry hiện tại có 74 tên trùng chính xác. Đây không phải
số skill đã đánh giá: trùng tên chưa chắc trùng nội dung, không trùng tên cũng có
thể trùng chức năng. Cần tiếp tục đánh giá trước khi nhập.

**Ngân sách:** dry-run `cli-tool` với HOME trống, `--stacks python --no-lsp` chọn
86 skill riêng, vượt `max_skills: 75` của profile; hiện installer cảnh báo chứ không
cắt. Ước lượng đồng hồ ≈ 51% chưa bao gồm global/builtin. Thêm skill có thể làm
tăng nhiễu; cần đối chiếu runtime thực trước khi kết luận khả năng nạp.

## Đợt 3 — chạy mẫu thật và kiểm tra toàn vẹn

- Chạy block ví dụ **đầu tiên**, với `Calculator` giả, của pytest 8.4.2 (4 test),
  Jest 30.2.0, Jasmine 5.12.0, Mocha 11.7.5 + Chai 6.2.2 và Vitest 3.2.4
  (mỗi framework 2 test): tất cả pass trên Python 3.11 và Node 22. Không suy rộng
  cho các block khác, phiên bản khác hoặc framework chưa có runtime ở sandbox.
  Dependency chỉ cài ở `/tmp` để thử, không thêm vào repo hay installer.
- `tools/test_vibe_examples.py` chạy lại các ví dụ này với dependency đã cài sẵn;
  script không tự tải package. Ví dụ:
  `python3 tools/test_vibe_examples.py --node-prefix /path/to/npm-prefix --python-path /path/to/pytest-target`.
- Thêm `registry/vibe-review-hashes.json` để kiểm toàn bộ file của 16 skill trong
  đợt, kể cả tài liệu reference, bằng `test_vibe_skills.py`. Hash phát hiện thay đổi,
  không chứng minh nội dung an toàn; khi cập nhật nguồn phải review lại rồi cập nhật hash.
- Phát hiện `vendor.py --check` cũ in cảnh báo hash sai nhưng vẫn trả exit 0, và bỏ
  lọt `SKILL.md`/hash bị thiếu. Đã sửa để trả lỗi; bổ sung test âm. Ghi hash thực tế
  cho skill `handoff` local vốn có hash rỗng. `vendor.py --check` vẫn chỉ hash
  `SKILL.md`, không kiểm mọi file reference ngoài cohort nói trên.
- Đã đọc thêm sáu ứng viên AAS, chưa nhập: `phase-gated-debugging` trùng quy trình
  debug hiện có và mặc định đòi xác nhận, không hợp yêu cầu tự chủ; `agentic-test-audit`
  cần runner/dependency riêng; `code-review-checklist`, `code-review-excellence` và
  `fixing-accessibility` cần đối chiếu sâu với skill review/a11y hiện có;
  `codebase-audit-pre-push` có phạm vi sửa dọn quá rộng so với task. Không coi việc
  không nhập là kết luận vĩnh viễn về chất lượng nguồn.

## Đợt 4 — kiểm tra hai nguồn MCP và luồng cập nhật

- Đã clone `microsoft/playwright-mcp` @ `0c4107acbecb75472b23c05c0e42471a0011874f`.
  Đây là MCP runtime cần Node, package Playwright và browser; không phải skill
  độc lập, chưa thử trong Antigravity App, không tự động cài hoặc cam kết offline.
- Đã clone `AishwaryShrivastav/vibe-testing` @ `a451c842940e80155b8b4306d9ed0c4ac00b8e71`.
  `release-qa` phụ thuộc các tool MCP của repo và khuyên lưu thông tin đăng nhập
  trong `VIBE.md`; không đưa vào bộ skill offline hoặc yêu cầu lưu mật khẩu vào file.
  Chưa chạy browser hay xác minh tương thích Antigravity.
- Thêm `--update-owned` cho installer và bootstrap: cập nhật nội dung skill có dấu
  sở hữu, không ghi đè thư mục skill không có dấu. Cờ này không tự cập nhật agent,
  plugin hay hook đã tồn tại; sửa tay trong skill có dấu vẫn bị ghi đè.
- Phát hiện bootstrap bỏ qua `--dry-run` ở nhánh `--core` và phần global khi cài
  workspace; còn tạo workspace và gọi LSP thật. Đã truyền dry-run vào cả ba chế độ,
  không tạo workspace mới và không clone/pull khi chạy dry-run ngoài repo. Test
  dùng HOME tạm để kiểm tra không ghi, và kiểm tra cập nhật owned/unowned.
  Nếu chưa có repo/cache, dry-run dừng và yêu cầu clone trước.
