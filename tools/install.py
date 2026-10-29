#!/usr/bin/env python3
"""Cài Skill OS vào Antigravity App — từ repo đã clone, không cần mạng.

Phạm vi (Google Antigravity App):
    ~/.gemini/AGENTS.md                  rules always_on (ponytail FULL + …)
    ~/.gemini/config/skills/<id>/        skill global, mọi workspace
    <workspace>/.agents/skills/<id>/     skill riêng workspace (cô lập cứng)

    python3 tools/install.py --core                     # cài phần global
    python3 tools/install.py --core --dry-run           # xem trước
    python3 tools/install.py --profile web-admin -w ~/p/admin
    python3 tools/install.py --list                     # xem đã cài gì
    python3 tools/install.py --core --uninstall

An toàn: không bao giờ xoá thư mục skill không do file này tạo (xem .skill-os-owner).
File rules cũ được backup thành AGENTS.md.bak.<timestamp>.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
REGISTRY = ROOT / "registry" / "skills.json"
AGENTS_REG = ROOT / "registry" / "agents.json"
AGENTS_SRC = ROOT / "agents"
HOOKS_SRC = ROOT / "hooks"
PLUGINS_SRC = ROOT / "plugins"
PLUGINS_REG = ROOT / "registry" / "plugins.json"
PROFILES = ROOT / "profiles"
OWNER = ".skill-os-owner"

GLOBAL_DIR = Path(os.environ.get("SKILL_OS_HOME", "~/.gemini")).expanduser()
GLOBAL_SKILLS = GLOBAL_DIR / "config" / "skills"
GLOBAL_RULES = GLOBAL_DIR / "AGENTS.md"


def load() -> tuple[list[dict], dict[str, dict]]:
    skills = json.loads(REGISTRY.read_text(encoding="utf-8"))["skills"]
    profiles = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                for p in sorted(PROFILES.glob("*.json"))}
    return skills, profiles


def pack_dir(skill: dict) -> Path:
    return PACKS / skill["pack"] / skill["id"]


def select(skills: list[dict], prof: dict, include_manual: bool = False) -> list[dict]:
    want_dom = set(prof["select"].get("domain", []))
    want_art = set(prof["select"].get("artifact", []))
    forbid = set(prof.get("forbid_domains", []))
    want_fam = set(prof.get("families", []))
    out = []
    for s in skills:
        if s["mode"] == "system":
            continue
        if s["mode"] == "manual" and not include_manual:
            continue
        dom, art = set(s["domain"]), set(s["artifact"]) or {"*"}
        fam = set(s.get("families", []))
        if fam and want_fam and not (fam & want_fam):
            continue
        if dom & forbid:
            continue
        if "*" in dom or dom & want_dom:
            if "*" in art or art & want_art:
                out.append(s)
    return sorted(out, key=lambda s: (s["pack"], s["id"]))


def copy_skill(skill: dict, dest_root: Path, dry: bool, force: bool) -> str:
    src, dest = pack_dir(skill), dest_root / skill["id"]
    if not src.is_dir():
        return "✗ thiếu nguồn trong packs/"
    if dest.exists():
        owned = (dest / OWNER).is_file()
        if owned and not force:
            return "= đã cài"
        if not owned and not force:
            return "! đã tồn tại, không do Skill OS tạo — bỏ qua (--force để ghi đè)"
        if dry:
            return "~ sẽ ghi đè"
        shutil.rmtree(dest)
    if dry:
        return "· sẽ cài"
    shutil.copytree(src, dest)
    (dest / OWNER).write_text("antigravity-skill-os\n", encoding="utf-8")
    return "✓"


def install_rules(dry: bool) -> str:
    src = ROOT / "core" / "AGENTS.md"
    if dry:
        return f"· sẽ ghi {GLOBAL_RULES}"
    GLOBAL_RULES.parent.mkdir(parents=True, exist_ok=True)
    msg = ""
    if GLOBAL_RULES.exists():
        bak = GLOBAL_RULES.with_suffix(f".md.bak.{datetime.now():%Y%m%d%H%M%S}")
        shutil.copy2(GLOBAL_RULES, bak)
        msg = f" (backup: {bak.name})"
    shutil.copy2(src, GLOBAL_RULES)
    return f"✓ {GLOBAL_RULES}{msg}"


def do_core(skills: list[dict], dry: bool, force: bool) -> None:
    print(f"\n  Rules → {GLOBAL_RULES}")
    print(f"    {install_rules(dry)}")
    core = [s for s in skills if s["mode"] == "core"]
    print(f"\n  Skill global → {GLOBAL_SKILLS}  ({len(core)})")
    for s in core:
        print(f"    {copy_skill(s, GLOBAL_SKILLS, dry, force)} {s['id']}")


def install_agents(groups: list[str], ws: Path, dry: bool, force: bool) -> int:
    """Copy subagent .md vào <ws>/.agents/agents/."""
    if not groups:
        return 0
    reg = json.loads(AGENTS_REG.read_text(encoding="utf-8"))["agents"]
    picked = [a for a in reg if a["group"] in groups]
    dest_root = ws / ".agents" / "agents"
    print(f"\n  Subagent → {dest_root}  ({len(picked)})")
    n = 0
    for a in picked:
        src = AGENTS_SRC / a["group"] / f"{a['id']}.md"
        dest = dest_root / f"{a['id']}.md"
        if not src.is_file():
            print(f"    ✗ {a['id']}: thiếu trong agents/ — chạy tools/port_agents.py --all")
            continue
        if dest.exists() and not force:
            print(f"    = {a['id']}")
            continue
        if dry:
            print(f"    · {a['id']}")
            continue
        dest_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"    ✓ {a['id']}")
        n += 1
    return len(picked)


def install_plugins(names: list[str], ws: Path, dry: bool, force: bool) -> int:
    """Copy plugin đã port vào <ws>/.agents/plugins/."""
    if not names:
        return 0
    reg = {p["id"]: p for p in json.loads(PLUGINS_REG.read_text(encoding="utf-8"))["plugins"]}
    dest_root = ws / ".agents" / "plugins"
    print(f"\n  Plugin → {dest_root}  ({len(names)})")
    for n in names:
        src = PLUGINS_SRC / n
        if not src.is_dir():
            print(f"    ✗ {n}: thiếu trong plugins/ — chạy tools/port_plugins.py --all")
            continue
        dest = dest_root / n
        if dest.exists() and not force:
            print(f"    = {n}")
            continue
        if dry:
            print(f"    · {n}")
            continue
        dest_root.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        rec = reg.get(n, {})
        nsk = len(list((dest / "skills").glob("*"))) if (dest / "skills").is_dir() else 0
        print(f"    ✓ {n:<24} {nsk} skill · {rec.get('license', '?')}")
    return len(names)


def install_hooks(ws: Path, dry: bool, force: bool) -> None:
    """Copy hooks.json + script vào <ws>/.agents/."""
    if not HOOKS_SRC.is_dir():
        print("\n  ✗ không thấy thư mục hooks/")
        return
    dest_json = ws / ".agents" / "hooks.json"
    dest_dir = ws / ".agents" / "skill-os"
    print(f"\n  Hooks → {dest_json}")
    if dest_json.exists() and not force:
        print("    ! hooks.json đã có — bỏ qua (--force để ghi đè)")
    elif dry:
        print("    · sẽ ghi hooks.json + scripts")
    else:
        ws.joinpath(".agents").mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOOKS_SRC / "hooks.json", dest_json)
        dest_dir.mkdir(parents=True, exist_ok=True)
        for f in HOOKS_SRC.glob("*.py"):
            shutil.copy2(f, dest_dir / f.name)
            (dest_dir / f.name).chmod(0o755)
        print("    ✓ hooks.json + 3 script (chỉ session-start bật mặc định)")


def do_manifest(dest_root: Path, skills: list[dict], prof: str, dry: bool) -> None:
    if dry:
        return
    dest_root.mkdir(parents=True, exist_ok=True)
    (dest_root.parent / "skill-os.json").write_text(json.dumps({
        "installed_by": "antigravity-skill-os",
        "profile": prof,
        "when": datetime.now().isoformat(timespec="seconds"),
        "skills": [s["id"] for s in skills],
        "always_on": "ponytail FULL + skill-first + verify (rules global, không nằm ở đây)",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def do_workspace(skills: list[dict], profiles: dict[str, dict],
                 profile: str, ws: Path, dry: bool, force: bool,
                 include_manual: bool = False, hooks: bool = False,
                 plugins: bool = False) -> None:
    if profile not in profiles:
        sys.exit(f"  Không có profile '{profile}'. Có: {', '.join(profiles)}")
    prof = profiles[profile]
    chosen = select(skills, prof, include_manual)
    target = ws / ".agents" / "skills"
    print(f"\n  Profile : {profile} — {prof['label']}")
    print(f"  Cài vào : {target}  ({len(chosen)} skill)")
    by_pack: dict[str, int] = {}
    for s in chosen:
        r = copy_skill(s, target, dry, force)
        print(f"    {r} {s['id']}")
        if r.startswith("✓") or r.startswith("~"):
            by_pack[s["pack"]] = by_pack.get(s["pack"], 0) + 1
    install_agents(prof.get("agent_groups", []), ws, dry, force)
    install_plugins(prof.get("plugins", []) if plugins else [], ws, dry, force)
    if hooks:
        install_hooks(ws, dry, force)
    do_manifest(target, chosen, profile, dry)
    skipped = len([s for s in skills if s["mode"] != "system"]) - len(chosen)
    print(f"\n  {sum(by_pack.values())} skill đã cài — "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))
    print(f"  {skipped} skill bị loại khỏi workspace này (cô lập cứng).")


def do_list(skills: list[dict]) -> None:
    print(f"\n  Rules: {GLOBAL_RULES} "
          f"({'có' if GLOBAL_RULES.exists() else 'CHƯA cài'})")
    print(f"\n  Skill global ({GLOBAL_SKILLS}):")
    if GLOBAL_SKILLS.is_dir():
        for d in sorted(GLOBAL_SKILLS.iterdir()):
            if d.is_dir():
                mark = " " if (d / OWNER).is_file() else "*"
                print(f"    {mark} {d.name}")
        print("    (* = không do Skill OS tạo)")
    else:
        print("    (chưa cài)")
    ws = Path.cwd()
    m = ws / ".agents" / "skill-os.json"
    if m.is_file():
        d = json.loads(m.read_text(encoding="utf-8"))
        print(f"\n  Workspace hiện tại: profile {d.get('profile')} — "
              f"{len(d.get('skills', []))} skill")
    print()


def do_uninstall(skills: list[dict], dry: bool) -> None:
    n = 0
    if GLOBAL_SKILLS.is_dir():
        for d in list(GLOBAL_SKILLS.iterdir()):
            if d.is_dir() and (d / OWNER).is_file():
                print(f"    - {d.name}")
                if not dry:
                    shutil.rmtree(d)
                n += 1
    if GLOBAL_RULES.exists():
        print(f"    - {GLOBAL_RULES}")
        if not dry:
            GLOBAL_RULES.unlink()
        n += 1
    print(f"\n  {'Sẽ gỡ' if dry else 'Đã gỡ'} {n} mục. Skill không do Skill OS tạo được giữ nguyên.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cài/ gỡ Skill OS cho Antigravity App")
    ap.add_argument("--core", action="store_true", help="cài rules + skill global")
    ap.add_argument("--profile")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="ghi đè skill không do Skill OS tạo")
    ap.add_argument("--include-manual", action="store_true",
                    help="cài cả skill mode=manual (mặc định bỏ để workspace gọn)")
    ap.add_argument("--plugins", action="store_true",
                    help="cài cả plugin đã port (mặc định tắt để workspace gọn)")
    ap.add_argument("--hooks", action="store_true",
                    help="cài hooks.json (session-start nhắc luật hệ thống)")
    a = ap.parse_args()

    skills, profiles = load()
    dry = a.dry_run
    if dry:
        print("  [DRY RUN] không ghi gì cả")

    if a.list:
        do_list(skills)
    if a.core:
        do_core(skills, dry, a.force)
    if a.profile:
        do_workspace(skills, profiles, a.profile, Path(a.workspace).expanduser().resolve(),
                     dry, a.force, a.include_manual, a.hooks, a.plugins)
    if a.uninstall:
        do_uninstall(skills, dry)
    if not any([a.list, a.core, a.profile, a.uninstall]):
        ap.print_help()
    print()


if __name__ == "__main__":
    main()
