---
name: commit
description: Create a git commit
---

> Bản gốc giới hạn tool (`allowed-tools`). Antigravity không có pattern scope theo lệnh nên giới hạn đó bị bỏ — chỉ dẫn bên dưới thay thế.

## Dữ liệu cần thu thập

Trước khi làm, chạy các lệnh sau và đọc output thật của chúng:

- `git status`
- `git diff HEAD`
- `git branch --show-current`
- `git log --oneline -10`

## Context

- Current git status: (output của `git status`)
- Current git diff (staged and unstaged changes): (output của `git diff HEAD`)
- Current branch: (output của `git branch --show-current`)
- Recent commits: (output của `git log --oneline -10`)

## Your task

Based on the above changes, create a single git commit.

You have the capability to call multiple tools in a single response. Stage and create the commit using a single message. Do not use any other tools or do anything else. Do not send any other text or messages besides these tool calls.
