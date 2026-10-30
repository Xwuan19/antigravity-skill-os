#!/usr/bin/env python3
"""Vendor toàn bộ skill vào packs/ — repo tự chứa, không cần mạng khi cài.

Với mỗi repo trong registry: clone đúng commit đã pin một lần, sparse-checkout
đúng các đường dẫn cần, rồi copy từng skill vào `packs/<pack>/<id>/`.

Ghi `packs/VENDOR.json` để lần sau biết bản đang có là commit nào và có bị sửa tay không.

    python3 tools/vendor.py                # vendor tất cả
    python3 tools/vendor.py --only design  # chỉ pack design
    python3 tools/vendor.py --check        # chỉ kiểm tra sha256, không tải
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
REGISTRY = ROOT / "registry" / "skills.json"
MANIFEST = PACKS / "VENDOR.json"

# file license ở gốc repo, thử lần lượt
LICENSE_NAMES = ["LICENSE", "LICENSE.txt", "LICENSE.md", "license", "COPYING"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str]) -> tuple[bool, str]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()


def repo_root_license(repo_dir: Path) -> Path | None:
    for n in LICENSE_NAMES:
        p = repo_dir / n
        if p.is_file():
            return p
    return None


def fetch_repo(repo: str, ref: str, paths: list[str], tmp: Path) -> Path | None:
    d = tmp / repo.replace("/", "__")
    ok, err = run(["git", "clone", "--filter=blob:none", "--no-checkout",
                   "--quiet", f"https://github.com/{repo}.git", str(d)])
    if not ok:
        print(f"  ✗ clone {repo}: {err[:140]}")
        return None
    run(["git", "-C", str(d), "sparse-checkout", "init", "--no-cone"])
    (d / ".git" / "info" / "sparse-checkout").write_text(
        "\n".join(paths + LICENSE_NAMES) + "\n", encoding="utf-8")
    if ref:
        ok, err = run(["git", "-C", str(d), "fetch", "--depth", "1", "--quiet",
                       "origin", ref])
        if not ok:
            print(f"  ✗ fetch {repo}@{ref[:10]}: {err[:140]}")
            return None
        ok, err = run(["git", "-C", str(d), "checkout", "--quiet", ref])
    else:
        ok, err = run(["git", "-C", str(d), "checkout", "--quiet"])
    if not ok:
        print(f"  ✗ checkout {repo}@{ref[:10] or 'HEAD'}: {err[:140]}")
        return None
    return d


def strip(dest: Path, patterns: list[str]) -> int:
    """Xoá file khớp glob — dùng để bỏ font/ảnh/test nặng không cần cho skill."""
    n = 0
    for pat in patterns:
        for f in sorted(dest.glob(pat)):
            if f.is_file():
                f.unlink()
                n += 1
            elif f.is_dir():
                shutil.rmtree(f)
                n += 1
    return n


def patch_skill(dest: Path, s: dict) -> None:
    """Sửa SKILL.md sau khi copy: đổi `name:`, thay chuỗi, chèn ghi chú.

    Làm trước khi ghi sha256 nên `--check` vẫn so trên bản đã vá.
    """
    sk = dest / "SKILL.md"
    if not sk.is_file():
        return
    txt = orig = sk.read_text(encoding="utf-8")

    # fm_desc: viết lại frontmatter chỉ còn name + description.
    # Dùng khi bản gốc mang hooks/allowed-tools/metadata của Claude Code
    # (`${CLAUDE_SKILL_DIR}`, `~/.claude/...`) hoặc description dài quá mức.
    fd = s.get("fm_desc")
    if fd:
        end = txt.find("\n---", 3) if txt.startswith("---") else -1
        body = txt[end + 4:].lstrip("\n") if end != -1 else txt
        txt = (f"---\nname: {s['id']}\n"
               f"description: {json.dumps(fd, ensure_ascii=False)}\n---\n\n{body}")
    for a, b in s.get("cut", []):
        i = txt.find(a)
        j = txt.find(b, i + len(a)) if i != -1 else -1
        if i == -1 or j == -1:
            print(f"      ! {s['id']}: cut không khớp — {a[:40]}")
        else:
            txt = txt[:i] + txt[j:]
    for old, new in s.get("patch", []):
        if old not in txt:
            print(f"      ! {s['id']}: patch không khớp — {old[:50]}")
        txt = txt.replace(old, new)
    if s.get("rename"):
        txt, n = re.subn(r"^name:.*$", f"name: {s['id']}", txt, count=1, flags=re.M)
        if n == 0:
            print(f"      ! {s['id']}: không thấy dòng `name:` để đổi")
    note = s.get("note_md")
    if note:
        if txt.startswith("---"):
            end = txt.find("\n---", 3)
            end = txt.find("\n", end + 1) if end != -1 else 0
            txt = txt[:end] + f"\n\n{note}\n" + txt[end:]
        else:
            txt = f"{note}\n\n{txt}"
    if txt != orig:
        sk.write_text(txt, encoding="utf-8")


def vendor(skills: list[dict], only: str | None, ids: list[str] | None = None) -> dict:
    todo = [s for s in skills
            if s["mode"] != "system" and s.get("repo") not in (None, "local")
            and (only is None or s["pack"] == only)
            and (not ids or s["id"] in ids)]

    by_repo: dict[tuple[str, str], list[dict]] = {}
    for s in todo:
        by_repo.setdefault((s["repo"], s.get("ref") or ""), []).append(s)

    out: dict = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skills": {},
    }
    total_bytes = 0

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for (repo, ref), group in by_repo.items():
            print(f"\n  {repo} @ {ref[:10] or 'HEAD'}  ({len(group)} skill)")
            paths = sorted({s["path"] for s in group}
                           | {e for s in group for e in s.get("extra", [])})
            if "." in paths or "./" in paths:
                paths = ["/**"]  # skill ở gốc repo: lấy cả cây
            src = fetch_repo(repo, ref, paths, tmp)
            if src is None:
                continue
            lic = repo_root_license(src)
            for s in group:
                sdir = src / s["path"]
                if s["path"] in (".", "./"):
                    # skill nằm ngay gốc repo: copy cả cây, bỏ .git và file ẩn
                    dest = PACKS / s["pack"] / s["id"]
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(sdir, dest, ignore=shutil.ignore_patterns(
                        ".git", ".github", ".gitignore", ".gitattributes"))
                    if s.get("exclude"):
                        strip(dest, s["exclude"])
                    patch_skill(dest, s)
                    size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
                    total_bytes += size
                    sk = dest / "SKILL.md"
                    out["skills"][s["id"]] = {
                        "pack": s["pack"],
                        "source": (f"{repo}@{ref}" if ref else f"{repo}@HEAD"),
                        "path": s["path"], "license": s["license"],
                        "bytes": size, "sha256": sha(sk) if sk.is_file() else None,
                    }
                    print(f"    ✓ {s['id']:<30} {size:>8,}B  {len(list(dest.iterdir()))} mục")
                    continue
                if not sdir.is_dir():
                    print(f"    ✗ {s['id']}: không thấy {s['path']}")
                    continue
                dest = PACKS / s["pack"] / s["id"]
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(sdir, dest)
                if lic and not any((dest / n).exists() for n in LICENSE_NAMES):
                    shutil.copy2(lic, dest / lic.name)
                if s.get("exclude"):
                    strip(dest, s["exclude"])
                for e in s.get("extra", []):
                    src_f = src / e
                    if not src_f.is_file():
                        print(f"      ! {s['id']}: thiếu {e}")
                        continue
                    ref_dir = dest / "references"
                    ref_dir.mkdir(exist_ok=True)
                    # giữ tên gốc, viết thường cho dễ đọc trong SKILL.md
                    shutil.copy2(src_f, ref_dir / src_f.name.lower())
                patch_skill(dest, s)
                size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
                total_bytes += size
                sk = dest / "SKILL.md"
                out["skills"][s["id"]] = {
                    "pack": s["pack"],
                    "source": (f"{repo}@{ref}" if ref else f"{repo}@HEAD"),
                    "path": s["path"],
                    "license": s["license"],
                    "bytes": size,
                    "sha256": sha(sk) if sk.is_file() else None,
                }
                print(f"    ✓ {s['id']:<30} {size:>8,}B  {len(list(dest.rglob('*')))} mục")

    out["total_bytes"] = total_bytes
    return out


def check(skills: list[dict], manifest: dict) -> int:
    bad = 0
    for s in skills:
        if s["mode"] == "system":
            continue
        rec = manifest.get("skills", {}).get(s["id"])
        if not rec:
            print(f"  ? {s['id']:<30} chưa có trong VENDOR.json")
            bad += 1
            continue
        d = PACKS / s["pack"] / s["id"]
        if not d.is_dir():
            print(f"  ✗ {s['id']:<30} thiếu thư mục")
            bad += 1
        elif rec.get("sha256") and (d / "SKILL.md").is_file() \
                and sha(d / "SKILL.md") != rec["sha256"]:
            print(f"  ~ {s['id']:<30} SKILL.md đã bị sửa tay")
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["code", "design", "motion", "education",
                                       "docs", "meta"])
    ap.add_argument("--id", action="append", metavar="ID",
                    help="chỉ vendor skill này (lặp lại được)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    skills = json.loads(REGISTRY.read_text(encoding="utf-8"))["skills"]

    if a.check:
        m = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
        n = check(skills, m)
        print(f"\n  {n} vấn đề." if n else "\n  Tất cả khớp VENDOR.json.")
        raise SystemExit(1 if n else 0)

    man = vendor(skills, a.only, a.id)
    if MANIFEST.exists():
        old = json.loads(MANIFEST.read_text(encoding="utf-8"))
        old["skills"].update(man["skills"])
        man["skills"] = old["skills"]
    man["total_bytes"] = sum(v["bytes"] for v in man["skills"].values())
    MANIFEST.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    n = len(man["skills"])
    print(f"\n  {n} skill · {man['total_bytes'] / 1_048_576:.1f} MB · {MANIFEST.name}")


if __name__ == "__main__":
    sys.exit(main())
