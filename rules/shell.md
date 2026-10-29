---
trigger: always_on
description: "Shell: set -euo pipefail, quote biến, không parse ls, kiểm bằng shellcheck."
---

# Shell

## Trước khi sửa
- Script được gọi ở đâu: `rg "<tên_script>"` — kể cả trong CI, Makefile, Dockerfile.
- Biến môi trường script đọc: liệt kê ra trước khi đổi.

## Viết
- Dòng đầu: `#!/usr/bin/env bash` + `set -euo pipefail`.
- Luôn quote: `"$var"`, `"${arr[@]}"`.
- Kiểm đầu vào sớm: `[[ -f $file ]] || { echo "missing $file" >&2; exit 1; }`.
- Hàm có `local` cho biến tạm.

## Không được
- `for f in $(ls)` — dùng `for f in *.txt` hoặc `find -print0`.
- `cd` mà không kiểm lỗi.
- `rm -rf "$VAR/"` khi `VAR` có thể rỗng.
- Pipe vào `while read` làm mất biến (dùng `done < <(...)`).

## Kiểm chứng
```bash
bash -n script.sh        # cú pháp
shellcheck script.sh     # bắt lỗi thật
```
