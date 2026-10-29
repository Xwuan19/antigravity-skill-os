#!/usr/bin/env bash
# Cài Antigravity Skill OS.
#
#   bash bootstrap.sh --system                  # TOÀN BỘ máy — mọi project dùng được
#   bash bootstrap.sh web-admin ~/p/admin       # chỉ một project (cô lập)
#
# --system cài tất cả skill vào ~/.gemini/config/skills/ + rules global + LSP global.
# Không cần làm gì cho từng project nữa.
#
# Không cần mạng sau bước clone: toàn bộ skill đã nằm trong repo.

set -euo pipefail

REPO_URL="${SKILL_OS_REPO:-https://github.com/Xwuan19/antigravity-skill-os.git}"
CACHE="${SKILL_OS_CACHE:-$HOME/.cache/antigravity-skill-os}"

SYSTEM=0
PROFILE=""
WS=""
FLAGS=()

for a in "$@"; do
  case "$a" in
    --system)     SYSTEM=1 ;;
    --no-hooks|--no-plugins|--no-lsp|--include-manual|--dry-run) FLAGS+=("$a") ;;
    -*)           echo "  ! tham số lạ: $a" >&2 ;;
    *)            if [ -z "$PROFILE" ]; then PROFILE="$a"
                  elif [ -z "$WS" ]; then WS="$a"
                  else echo "  ! bỏ qua tham số thừa: $a" >&2; fi ;;
  esac
done

has() { local x; for x in "${FLAGS[@]:-}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

die() { printf '\n  ✗ %s\n\n' "$1" >&2; exit 1; }

if [ "$SYSTEM" -eq 0 ] && [ -z "$PROFILE" ]; then
  die "Chưa chọn kiểu cài.

  Cài toàn bộ máy (khuyên dùng lần đầu):
    bash bootstrap.sh --system

  Hoặc cài riêng cho một project:
    bash bootstrap.sh web-admin ~/p/admin
    (profile: web-admin landing cli-tool mobile-app design-system docs-writer education-k12 education-language meta)"
fi

command -v python3 >/dev/null || die "Cần python3 (>= 3.10)."

# ---- 1. tìm repo ----------------------------------------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$HERE/tools/install.py" ] && [ -d "$HERE/packs" ]; then
  ROOT="$HERE"
  echo "  Repo: $ROOT (bản đang đứng)"
else
  command -v git >/dev/null || die "Cần git để clone repo."
  if [ -d "$CACHE/.git" ]; then
    git -C "$CACHE" pull --ff-only --quiet && echo "  Repo: $CACHE (đã cập nhật)"
  else
    echo "  Đang clone…"
    git clone --quiet --depth 1 "$REPO_URL" "$CACHE"
    echo "  Repo: $CACHE"
  fi
  ROOT="$CACHE"
fi

# ===========================================================================
# Chế độ hệ thống
# ===========================================================================
if [ "$SYSTEM" -eq 1 ]; then
  echo "  Chế độ: TOÀN BỘ HỆ THỐNG  (${SKILL_OS_HOME:-~/.gemini})"

  echo
  echo "── Rules + toàn bộ skill ──"
  SYS=()
  has --include-manual && SYS+=(--include-manual)
  has --dry-run && SYS+=(--dry-run)
  python3 "$ROOT/tools/install.py" --system "${SYS[@]}"

  if ! has --no-lsp; then
    echo
    echo "── LSP toàn cục ──"
    GLO=()
    has --dry-run && GLO+=(--dry-run)
    python3 "$ROOT/tools/lsp.py" --global --langs all "${GLO[@]}" || true
  fi

  echo
  echo "──────────────────────────────────────────────"
  echo "  Xong. Mọi project giờ dùng được, không cần cài lại."
  echo
  echo "  1. Khởi động lại Antigravity một lần."
  echo "  2. Thử trong phiên mới: \"có skill gì đang bật?\""
  echo
  echo "  Cài thêm language server (nếu bước LSP báo thiếu):"
  echo "       python3 $ROOT/tools/lsp.py --check"
  echo "──────────────────────────────────────────────"
  exit 0
fi

# ===========================================================================
# Chế độ một project
# ===========================================================================
WS="${WS:-$PWD}"
WS="$(cd "$WS" 2>/dev/null && pwd || { mkdir -p "$WS" && cd "$WS" && pwd; })"
echo "  Workspace: $WS"
echo "  Profile:   $PROFILE"

echo
echo "── Tầng global (mọi project) ──"
python3 "$ROOT/tools/install.py" --core

echo
echo "── Tầng workspace ──"
ARGS=(--profile "$PROFILE" -w "$WS" --no-lsp)
has --no-hooks   || ARGS+=(--hooks)
has --no-plugins || ARGS+=(--plugins)
has --include-manual && ARGS+=(--include-manual)
has --dry-run && ARGS+=(--dry-run)
python3 "$ROOT/tools/install.py" "${ARGS[@]}"

if ! has --no-lsp; then
  echo
  echo "── LSP ──"
  python3 "$ROOT/tools/lsp.py" -w "$WS" || true
fi

echo
echo "──────────────────────────────────────────────"
echo "  Xong. Còn 2 việc:"
echo
echo "  1. Khởi động lại Antigravity để nó nạp skill + MCP server."
echo
if has --no-lsp; then
  echo "  2. LSP đang tắt (--no-lsp). Bật sau bằng:"
  echo "       python3 $ROOT/tools/lsp.py -w $WS"
else
  echo "  2. Nếu bước LSP báo thiếu language server, cài rồi chạy lại:"
  echo "       python3 $ROOT/tools/lsp.py --check"
fi
echo
echo "  Kiểm chứng trong phiên mới: hỏi \"có skill gì đang bật?\""
echo "──────────────────────────────────────────────"
