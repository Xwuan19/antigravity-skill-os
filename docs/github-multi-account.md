# Làm việc với nhiều tài khoản GitHub

Quy tắc global trong `core/AGENTS.md` yêu cầu agent xác định tài khoản trước thao tác
GitHub, không đoán theo tên owner và không âm thầm đổi tài khoản khi đang có phiên khác.
Đây là **chỉ dẫn cho agent**, không phải bộ chặn kỹ thuật; Git, GCM và GitHub CLI vẫn
quản lý xác thực theo cấu hình thực tế trên máy.

## Ba thứ độc lập

| Thành phần | Quyết định | Cách kiểm tra an toàn |
|---|---|---|
| Git qua HTTPS + Git Credential Manager (GCM) | Credential dùng khi Git kết nối remote | Xem host, owner, tên repo và username trong URL **sau khi che userinfo/bí mật**; kiểm tra cấu hình credential helper. Username trong URL giúp GCM chọn tài khoản nếu GCM được cấu hình phù hợp, nhưng không tự chứng minh quyền. |
| GitHub CLI (`gh`) | Tài khoản dùng cho lệnh `gh` | `gh auth status` (không dùng `--show-token`); kiểm tra cả khả năng biến môi trường xác thực đang override, nhưng không in giá trị biến. |
| Git author | Tên và email ghi vào commit | `git config --show-origin --get user.name` và `git config --show-origin --get user.email`. Email phải liên kết tài khoản GitHub nếu muốn GitHub nhận diện commit; tên đăng nhập không tự đảm bảo điều đó. |

Không chạy `git credential fill`, `git credential-manager get`, hoặc lệnh nào in token ra
chat/log. Không đưa password/token vào URL, file, prompt hay lịch sử lệnh.

## Ánh xạ theo từng repo

Người dùng có thể chỉ định tài khoản dùng cho một repo. Agent cần kiểm tra remote và
cấu hình hiện có trước khi thay đổi; không sửa `--global`, không sửa repo khác và không
đổi thông tin tác giả nếu người dùng chưa yêu cầu. Chọn tài khoản Git/GCM không có nghĩa
là đổi author commit; nếu cấu hình đã đúng thì giữ nguyên, không ghi lại. Tên tài khoản
trong URL là tài khoản **đăng nhập**, không nhất thiết là `<owner>` của repo. Nếu chưa rõ
chọn tài khoản nào, hỏi trước khi push, tạo PR hay thao tác ghi khác. Nếu người dùng đã
chỉ định rõ tài khoản và cho phép thao tác ghi, tiến hành mà không hỏi xác nhận thừa;
dừng khi thông tin thiếu, mâu thuẫn hoặc thao tác phá hủy chưa được cho phép.

Ví dụ, sau khi đã xác nhận repo, URL cũ và tài khoản với người dùng:

```bash
# HTTPS, GCM: thay các giá trị bằng thông tin đã xác nhận; không chứa token.
git remote set-url origin https://<tai-khoan-dang-nhap>@github.com/<owner>/<repo>.git
# Chỉ khi người dùng đã cung cấp thông tin author cần dùng cho repo này:
git config --local user.name "<ten-author>"
git config --local user.email "<email-author>"
```

`git remote set-url` chỉ đổi một URL được chọn; repo có thể có fetch/push URL hoặc nhiều
URL riêng, vì vậy phải kiểm tra cấu hình trước, không thay thế bừa. Tránh in nguyên URL
nếu có khả năng chứa thông tin đăng nhập. Không lưu tên/email mặc định của người dùng
vào repo Skill OS công khai: cấu hình riêng nằm trong `.git/config` của project trên máy.

`git ls-remote` có thể kiểm tra truy cập đọc; repo công khai có thể đọc ẩn danh nên thành
công **không chứng minh** đúng tài khoản hoặc có quyền push. Chỉ báo thành công khi thao tác
thực tế thành công. Nếu credential thiếu hoặc bị từ chối, báo lỗi đã che thông tin nhạy cảm
và hướng dẫn người dùng kiểm tra kết nối GCM, không thử tài khoản khác âm thầm.

## Đồng thời dùng hai tài khoản

Các repo có thể có cấu hình Git local khác nhau; không cần liên tục đổi `user.name` hay
remote toàn máy. Tuy nhiên `gh auth switch` có thể đổi tài khoản active chung và gây xung
đột với phiên khác. Không tự động switch; kiểm tra tài khoản `gh` và các override hiện
hành trước mỗi thao tác `gh`. Nếu môi trường không cung cấp cơ chế cô lập tài khoản an
toàn, dừng thao tác ghi và báo người dùng. Không suy ra rằng URL Git có username cũng
đổi tài khoản `gh`.

## Prompt cho Antigravity trên máy đã cài

```text
Tôi dùng hai tài khoản GitHub. Hãy áp dụng quy tắc quản lý tài khoản của
Antigravity Skill OS cho repo hiện tại.

Dùng run_command để kiểm tra repo, host/owner của remote (che mọi thông tin nhạy cảm),
credential helper, author Git có hiệu lực và tài khoản gh đang active. Không in token,
không yêu cầu mật khẩu, không gọi lệnh lấy credential. Kiểm tra biến môi trường override
xác thực mà không in giá trị. Đối chiếu với tài khoản tôi chỉ định cho tác vụ; không suy
ra tài khoản chỉ từ owner repo.

Nếu đã đủ thông tin và tôi yêu cầu cấu hình repo này, chỉ cấu hình local cho repo này;
không đổi global hay repo khác. Nếu chưa rõ tài khoản hoặc email author, hỏi tôi trước
thao tác ghi. Không tự switch tài khoản gh dùng chung. Báo cách xác thực Git, tài khoản gh
và author là ba thứ riêng; kiểm tra đọc không chứng minh quyền push.
```

Sau khi repo Skill OS có bản rule mới, cài lại global bằng installer của repo hiện tại
(theo cấu hình `--core` hoặc `--system` đang dùng), rồi khởi động lại Antigravity để nạp
rules. Cài rules ghi đè `~/.gemini/AGENTS.md` và tạo bản sao lưu; kiểm tra/sao lưu sửa tay
trước. Không cần đưa toàn bộ skill lên global để dùng quy tắc này.
