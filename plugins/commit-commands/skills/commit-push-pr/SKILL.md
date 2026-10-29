---
name: commit-push-pr
description: Commit, push, and open a PR
---

> Bản gốc giới hạn tool (`allowed-tools`). Antigravity không có pattern scope theo lệnh nên giới hạn đó bị bỏ — chỉ dẫn bên dưới thay thế.

## Dữ liệu cần thu thập

Trước khi làm, chạy các lệnh sau và đọc output thật của chúng:

- `git status`
- `git diff HEAD`
- `git branch --show-current`

## Context

- Current git status: (output của `git status`)
- Current git diff (staged and unstaged changes): (output của `git diff HEAD`)
- Current branch: (output của `git branch --show-current`)

## Your task

Based on the above changes:

1. Create a new branch if on main
2. Create a single commit with an appropriate message
3. Push the branch to origin
4. Create a pull request using `gh pr create`
5. You have the capability to call multiple tools in a single response. You MUST do all of the above in a single message. Do not use any other tools or do anything else. Do not send any other text or messages besides these tool calls.
