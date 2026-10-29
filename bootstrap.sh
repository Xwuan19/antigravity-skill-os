#!/usr/bin/env bash
# Cài Antigravity Skill OS trong một lệnh.
#
#   bash bootstrap.sh web-admin ~/p/admin
#   bash bootstrap.sh cli-tool ~/p/bot --no-hooks
#   bash bootstrap.sh web-admin            # cài vào thư mục hiện tại
#
# Script làm đúng những gì cần, không hỏi gì thêm:
#   1. lấy repo (dùng bản đang đứng nếu chạy trong repo, không thì clone)
#   2. --core                → rules + skill global, mọi project
#   3. --profile <p> -w <ws> → skill + agent + plugin + hook + LSP cho project
#   4. in ra việc còn lại (khởi động lại Antigravity, cài language server thiếu)
#
# Không cần mạng sau bước clone: toàn bộ skill đã nằm trong repo.

set -euo pipefail

REPO_URL="${SKILL_OS_REPO:-https://github.com/Xwuan19/antigravity-skill-os.git}"
CACHE="${SKILL_OS_CACHE:-$HOME/.cache/antigravity-skill-os}"

PROFILE="${1:-}"
WS="${2:-$PWD}"
shift $(( $# < 2 ? $# : 2 )) 2>/dev/null || true

NO_HOOKS=0; NO_PLUGINS=0; NO_LSP=0; STACKS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --no-hooks)   NO_HOOKS=1 ;;
    --no-plugins) NO_PLUGINS=1 ;;
    --no-lsp)     NO_LSP=1 ;;
    --stacks)     STACKS="${2:-}"; shift ;;
    *)            echo "  ! bỏ qua tham số lạ: $1" >&2 ;;
  esac
  shift
done

die() { printf '\n  ✗ %s\n\n' "$1" >&2; exit 1; }

[ -n "$PROFILE" ] || die "Thiếu profile. Ví dụ: bash bootstrap.sh web-admin ~/p/admin
  Xem danh sách: python3 tools/install.py --list"

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

WS="$(cd "$WS" 2>/dev/null && pwd || { mkdir -p "$WS" && cd "$WS" && pwd; })"
echo "  Workspace: $WS"
echo "  Profile:   $PROFILE"

# ---- 2. global ------------------------------------------------------------
echo
echo "── Tầng global (mọi project) ──"
python3 "$ROOT/tools/install.py" --core

# ---- 3. workspace ---------------------------------------------------------
echo
echo "── Tầng workspace ──"
ARGS=(--profile "$PROFILE" -w "$WS" --no-lsp)
[ "$NO_HOOKS"   -eq 0 ] && ARGS+=(--hooks)
[ "$NO_PLUGINS" -eq 0 ] && ARGS+=(--plugins)
[ -n "$STACKS" ]        && ARGS+=(--stacks "$STACKS")
python3 "$ROOT/tools/install.py" "${ARGS[@]}"

# ---- 4. LSP ---------------------------------------------------------------
if [ "$NO_LSP" -eq 0 ]; then
  echo
  echo "── LSP ──"
  python3 "$ROOT/tools/lsp.py" -w "$WS" || true
fi

# ---- 5. việc còn lại ------------------------------------------------------
echo
echo "──────────────────────────────────────────────"
echo "  Xong. Còn 2 việc:"
echo
echo "  1. Khởi động lại Antigravity để nó nạp skill + MCP server."
echo
if [ "$NO_LSP" -eq 0 ]; then
  echo "  2. Nếu bước LSP báo thiếu language server, cài rồi chạy lại:"
  echo "       python3 $ROOT/tools/lsp.py --check"
else
  echo "  2. LSP đang tắt (--no-lsp). Bật sau bằng:"
  echo "       python3 $ROOT/tools/lsp.py -w $WS"
fi
echo
echo "  Kiểm chứng trong phiên mới: hỏi \"có skill gì đang bật?\""
echo "  hoặc thử \"sửa bug này\" — nếu có skill logic, nó sẽ hỏi/tái hiện trước."
echo "──────────────────────────────────────────────"
