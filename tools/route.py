#!/usr/bin/env python3
"""Skill router — chọn đúng skill cho đúng loại project.

Nguyên tắc: skill không liên quan thì không được cài vào workspace.
Cách cô lập chắc chắn nhất là *không tồn tại*, không phải ra lệnh "đừng dùng".

Chỉ dùng stdlib.

Ví dụ:
    python3 tools/route.py --list-profiles
    python3 tools/route.py --profile web-admin
    python3 tools/route.py --tags dashboard,design --install ../my-project
    python3 tools/route.py --profile education-k12 --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry" / "skills.json"
PROFILES = ROOT / "profiles"


# ---------------------------------------------------------------- load

def load() -> tuple[list[dict], dict[str, dict]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    profiles = {}
    for f in sorted(PROFILES.glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        profiles[p["id"]] = p
    return data["skills"], profiles


def resolve_profile(skills: list[dict], profiles: dict[str, dict],
                    name: str | None, tags: list[str]) -> dict:
    """Tìm profile khớp. tags thắng nếu chỉ định --tags."""
    if name:
        if name not in profiles:
            die(f"Không có profile '{name}'. Có: {', '.join(sorted(profiles))}")
        return profiles[name]

    if not tags:
        die("Cần --profile hoặc --tags. Xem --list-profiles.")

    # profile có nhiều tag khớp nhất
    scored = sorted(
        profiles.values(),
        key=lambda p: len(set(t.lower() for t in p["tags"]) & set(tags)),
        reverse=True,
    )
    best = scored[0]
    if len(set(best["tags"]) & set(tags)) == 0:
        # không profile nào khớp tag → suy facet trực tiếp
        return {
            "id": "custom",
            "label": "tuỳ chỉnh từ tags: " + ", ".join(tags),
            "select": {"domain": tags, "artifact": tags},
            "forbid_domains": [],
            "rationale": "Suy trực tiếp từ tag, không qua profile.",
            "max_skills": 30,
        }
    return best


# ------------------------------------------------------------- select

def select(skills: list[dict], prof: dict) -> tuple[list[dict], list[dict]]:
    want_dom = set(prof["select"].get("domain", []))
    want_art = set(prof["select"].get("artifact", []))
    forbid = set(prof.get("forbid_domains", []))
    want_fam = set(prof.get("families", []))

    chosen, skipped = [], []
    for s in skills:
        if s["mode"] == "system":
            skipped.append(s)  # báo riêng, không cài
            continue

        dom = set(s["domain"])
        art = set(s["artifact"]) or {"*"}

        # skill có khai `families` thì chỉ khớp đúng họ; không khai = khớp mọi họ
        fam = set(s.get("families", []))
        hit_fam = not fam or not want_fam or bool(fam & want_fam)

        hit_dom = "*" in dom or bool(dom & want_dom)
        hit_art = "*" in art or bool(art & want_art)
        if hit_dom and hit_art and hit_fam and not dom & forbid:
            chosen.append(s)
        else:
            skipped.append(s)

    chosen.sort(key=lambda s: (s["pack"], s["phase"][0] if s["phase"] else "", s["id"]))
    return chosen, skipped


# -------------------------------------------------------------- output

def report(prof: dict, chosen: list[dict], skipped: list[dict]) -> None:
    systems = [s for s in skipped if s["mode"] == "system"]
    print(f"\n  Profile : {prof['id']} — {prof['label']}")
    print(f"  Domain  : {', '.join(prof['select'].get('domain', []))}   "
          f"| Artifact: {', '.join(prof['select'].get('artifact', []))}")
    if prof.get("forbid_domains"):
        print(f"  Cấm     : {', '.join(prof['forbid_domains'])}  (loại cứng)")
    if prof.get("rationale"):
        print(f"  Lý do   : {prof['rationale']}")

    print(f"\n  LUÔN BẬT — rules always_on, không cài vào .agents/skills/ ({len(systems)}):")
    for s in systems:
        print(f"    · {s['id']:<28} {s['note'] or ''}")

    print(f"\n  CHỌN {len(chosen)} skill:")
    print(f"    {'pack':<10} {'id':<28} {'phase':<18} artifact")
    print(f"    {'-'*10} {'-'*28} {'-'*18} {'-'*20}")
    for s in chosen:
        ph = ",".join(s["phase"]) or "*"
        art = ",".join(s["artifact"]) or "*"
        print(f"    {s['pack']:<10} {s['id']:<28} {ph:<18} {art}")

    by_pack: dict[str, int] = {}
    for s in skipped:
        if s["mode"] != "system":
            by_pack[s["pack"]] = by_pack.get(s["pack"], 0) + 1
    if by_pack:
        total = sum(by_pack.values())
        print(f"\n  KHÔNG cài {total} skill: "
              + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))

    cap = prof.get("max_skills")
    if cap and len(chosen) > cap:
        print(f"\n  ⚠  {len(chosen)} skill > trần {cap} của profile — danh sách description "
              f"sẽ dài, agent dễ chọn sai. Cân nhắc --profile hẹp hơn.")
    print(f"\n  Chi phí khi idle: {len(chosen)} dòng description "
          f"(~{len(chosen) * 18}–{len(chosen) * 30} token mỗi phiên).")
    bad = [s["id"] for s in chosen if s.get("license") == "UNKNOWN"]
    if bad:
        print(f"  ⚠  License chưa rõ, tự kiểm tra trước khi dùng: {', '.join(bad)}")
    print()


# ------------------------------------------------------------- install

def vendor_dir(skill_id: str) -> Path | None:
    for p in (ROOT / "packs").rglob(skill_id):
        if p.is_dir():
            return p
    return None


def fetch(skill: dict, dest: Path) -> bool:
    """Sparse-clone đúng commit rồi copy đúng thư mục skill."""
    repo, ref, path = skill["repo"], skill.get("ref"), skill["path"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp) / "repo"
        cmds = [
            ["git", "clone", "--filter=blob:none", "--no-checkout", "--quiet",
             f"https://github.com/{repo}.git", str(tmp_p)],
            ["git", "-C", str(tmp_p), "sparse-checkout", "init", "--no-cone"],
            ["git", "-C", str(tmp_p), "sparse-checkout", "set", path],
        ]
        if ref:
            cmds.append(["git", "-C", str(tmp_p), "fetch", "--depth", "1", "--quiet",
                         "origin", ref])
            cmds.append(["git", "-C", str(tmp_p), "checkout", "--quiet", ref])
        else:
            cmds.append(["git", "-C", str(tmp_p), "checkout", "--quiet"])
        for c in cmds:
            r = subprocess.run(c, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"    ✗ {skill['id']}: {r.stderr.strip()[:120]}")
                return False
        src = tmp_p / path
        if not src.is_dir():
            print(f"    ✗ {skill['id']}: không thấy {path} trong {repo}@{ref or 'HEAD'}")
            return False
        shutil.copytree(src, dest)
    return True


def install(chosen: list[dict], workspace: Path) -> None:
    target = workspace / ".agents" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    print(f"\n  Cài vào {target}")
    for s in chosen:
        dest = target / s["id"]
        if dest.exists():
            print(f"    = {s['id']:<28} đã có, bỏ qua")
            continue
        local = vendor_dir(s["id"])
        if local:
            shutil.copytree(local, dest)
            print(f"    ✓ {s['id']:<28} từ packs/ (vendored)")
        elif s["repo"] == "local":
            continue
        elif fetch(s, dest):
            print(f"    ✓ {s['id']:<28} từ {s['repo']}@{s.get('ref', 'HEAD')[:10]}")
    manifest = {
        "generated_by": "tools/route.py",
        "always_on_rules": [s["id"] for s in chosen if s["mode"] == "system"],
        "installed": [s["id"] for s in chosen],
        "note": "ponytail FULL là rule global, không nằm trong .agents/skills/.",
    }
    (workspace / ".agents" / "skill-os.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"    manifest: {workspace / '.agents' / 'skill-os.json'}")


def die(msg: str) -> None:
    print(f"Lỗi: {msg}", file=sys.stderr)
    raise SystemExit(2)


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description="Chọn skill theo loại project.")
    ap.add_argument("--profile", "-p")
    ap.add_argument("--tags", "-t", default="")
    ap.add_argument("--install", metavar="DIR")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-profiles", action="store_true")
    a = ap.parse_args()

    skills, profiles = load()

    if a.list_profiles:
        print(f"\n  {len(profiles)} profile:\n")
        for p in profiles.values():
            print(f"    {p['id']:<20} {p['label']}")
            print(f"    {'':<20} tags: {', '.join(p['tags'])}")
        print()
        return

    tags = [t.strip().lower() for t in a.tags.split(",") if t.strip()]
    prof = resolve_profile(skills, profiles, a.profile, tags)
    chosen, skipped = select(skills, prof)

    if a.json:
        print(json.dumps({"profile": prof["id"], "skills": chosen,
                          "always_on": [s["id"] for s in skipped if s["mode"] == "system"]},
                         indent=2, ensure_ascii=False))
        return

    report(prof, chosen, skipped)
    if a.install:
        install(chosen, Path(a.install).expanduser().resolve())
        print()


if __name__ == "__main__":
    main()
