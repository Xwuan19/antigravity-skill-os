---
trigger: always_on
description: "TypeScript: không any mới, narrow từ unknown, switch phải đủ nhánh, kiểm bằng tsc --noEmit."
---

# TypeScript

## Trước khi sửa
- Đổi type/interface: tìm mọi chỗ dùng bằng `rg "\b<TênType>\b"`, không chỉ chỗ import.
- `tsc` là lưới an toàn — chạy trước khi sửa để biết baseline có sạch không.

## Viết
- `unknown` rồi narrow; không `any` trong code mới.
- `strict` bật, không tắt bằng `// @ts-ignore` (cùng lắm `@ts-expect-error` kèm lý do).
- Union: `switch` phải phủ hết nhánh, hoặc có `default` gọi `never`.
- Dữ liệu từ ngoài (fetch, JSON, env): validate ở biên, đừng tin type.

## Không được
- `as` để ép type cho xong.
- `!` non-null assertion để né lỗi null.
- `any` rò vào type public.
- Bắt lỗi rồi `return undefined` im lặng.

## Kiểm chứng
```bash
npx tsc --noEmit
npm test        # hoặc pnpm test / bun test
```
