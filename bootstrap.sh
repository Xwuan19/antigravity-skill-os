#!/usr/bin/env bash
# Cài Antigravity Skill OS.
#
#   bash bootstrap.sh --system                  # TOÀN BỘ máy — mọi project dùng được
#   bash bootstrap.sh --system --exclude-pack education,docs
#                                              # global gọn: bỏ hẳn pack giáo dục/docs
#   bash bootstrap.sh --core --prune            # global mỏng: rules + 4 skill
#   bash bootstrap.sh auto ~/p/btvn             # rót skill đúng project (tự dò)
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
CORE=0
PROFILE=""
WS=""
FLAGS=()
EXCLUDE=""
WANT_EXCLUDE=0

for a in "$@"; do
  if [ "$WANT_EXCLUDE" -eq 1 ]; then EXCLUDE="$a"; WANT_EXCLUDE=0; continue; fi
  case "$a" in
    --system)     SYSTEM=1 ;;
    --core)       CORE=1 ;;
    --exclude-pack) WANT_EXCLUDE=1 ;;
    --exclude-pack=*) EXCLUDE="${a#*=}" ;;
    --no-hooks|--no-plugins|--no-lsp|--include-manual|--dry-run|--no-rules|--prune|--update-owned) FLAGS+=("$a") ;;
    -*)           echo "  ! tham số lạ: $a" >&2 ;;
    *)            if [ -z "$PROFILE" ]; then PROFILE="$a"
                  elif [ -z "$WS" ]; then WS="$a"
                  else echo "  ! bỏ qua tham số thừa: $a" >&2; fi ;;
  esac
done

has() { local x; for x in "${FLAGS[@]:-}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

die() { printf '\n  ✗ %s\n\n' "$1" >&2; exit 1; }

# A preview should not create Python bytecode caches in the repo either.
if has --dry-run; then export PYTHONDONTWRITEBYTECODE=1; fi

if [ "$SYSTEM" -eq 0 ] && [ "$CORE" -eq 0 ] && [ -z "$PROFILE" ]; then
  die "Chưa chọn kiểu cài.

  Tầng global mỏng + rót skill theo từng project (đỡ trần ngữ cảnh):
    bash bootstrap.sh --core --prune            # global chỉ còn 4 skill + rules
    bash bootstrap.sh auto ~/p/btvn             # mỗi project: tự dò rồi rót

  Cài toàn bộ máy (mọi project thấy hết):
    bash bootstrap.sh --system

  Hoặc cài riêng cho một project:
    bash bootstrap.sh web-admin ~/p/admin
    (profile: web-admin landing static-site cli-tool mobile-app desktop-app design-system docs-writer education-k12 education-language meta)"
fi

command -v python3 >/dev/null || die "Cần python3 (>= 3.10)."

# ---- 1. tìm repo ----------------------------------------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$HERE/tools/install.py" ] && [ -d "$HERE/packs" ]; then
  ROOT="$HERE"
  echo "  Repo: $ROOT (bản đang đứng)"
else
  if has --dry-run; then
    if [ -f "$CACHE/tools/install.py" ] && [ -d "$CACHE/packs" ]; then
      ROOT="$CACHE"
      echo "  Repo: $CACHE (dry-run: không pull)"
    else
      die "Dry-run cần repo đã có sẵn; clone trước rồi chạy bootstrap.sh từ repo."
    fi
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
fi

# ===========================================================================
# Chế độ global mỏng: rules + 4 skill core
# ===========================================================================
if [ "$CORE" -eq 1 ]; then
  echo "  Chế độ: GLOBAL MỎNG  (${SKILL_OS_HOME:-~/.gemini})"
  echo
  CORE_ARGS=(--core)
  has --prune && CORE_ARGS+=(--prune)
  has --dry-run && CORE_ARGS+=(--dry-run)
  has --update-owned && CORE_ARGS+=(--update-owned)
  python3 "$ROOT/tools/install.py" "${CORE_ARGS[@]}"
  if has --dry-run; then echo "  Dry-run hoàn tất — chưa cài hay ghi gì."; exit 0; fi
  echo
  echo "──────────────────────────────────────────────"
  echo "  Global giờ chỉ có rules + 4 skill. Mỗi project rót riêng:"
  echo
  echo "       bash bootstrap.sh auto ~/p/<ten-project>"
  echo
  echo "  (tự dò profile theo nội dung thư mục; muốn chỉ định tay thì"
  echo "   bash bootstrap.sh web-admin ~/p/admin)"
  echo "──────────────────────────────────────────────"
  exit 0
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
  [ -n "$EXCLUDE" ] && SYS+=(--exclude-pack "$EXCLUDE")
  has --prune && SYS+=(--prune)
  has --update-owned && SYS+=(--update-owned)
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
  if has --dry-run; then echo "  Dry-run hoàn tất — chưa cài hay ghi gì."; exit 0; fi
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
if has --dry-run; then
  WS="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$WS")"
else
  WS="$(cd "$WS" 2>/dev/null && pwd || { mkdir -p "$WS" && cd "$WS" && pwd; })"
fi
echo "  Workspace: $WS"
echo "  Profile:   $PROFILE"

echo
echo "── Tầng global (mọi project) ──"
CORE_ARGS=(--core)
has --prune && CORE_ARGS+=(--prune)
has --dry-run && CORE_ARGS+=(--dry-run)
has --update-owned && CORE_ARGS+=(--update-owned)
python3 "$ROOT/tools/install.py" "${CORE_ARGS[@]}"

echo
echo "── Tầng workspace ──"
ARGS=(--profile "$PROFILE" -w "$WS" --no-lsp)
has --no-hooks   || ARGS+=(--hooks)
has --no-plugins || ARGS+=(--plugins)
has --include-manual && ARGS+=(--include-manual)
has --dry-run && ARGS+=(--dry-run)
has --no-rules   && ARGS+=(--no-rules)
has --prune      && ARGS+=(--prune)
has --update-owned && ARGS+=(--update-owned)
[ -n "$EXCLUDE" ] && ARGS+=(--exclude-pack "$EXCLUDE")
python3 "$ROOT/tools/install.py" "${ARGS[@]}"

if ! has --no-lsp; then
  echo
  echo "── LSP ──"
  LSP_ARGS=(-w "$WS")
  has --dry-run && LSP_ARGS+=(--dry-run)
  python3 "$ROOT/tools/lsp.py" "${LSP_ARGS[@]}" || true
fi

echo
echo "──────────────────────────────────────────────"
if has --dry-run; then echo "  Dry-run hoàn tất — chưa cài hay ghi gì."; exit 0; fi
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
