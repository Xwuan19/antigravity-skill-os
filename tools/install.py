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
RULES_SRC = ROOT / "rules"
sys.path.insert(0, str(ROOT / "tools"))
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


def select_all(skills: list[dict], prof: dict, include_manual: bool = False,
               stacks: list[str] | None = None) -> list[dict]:
    import skillselect
    return skillselect.select(skills, prof, include_manual, stacks)


def resolve_stacks(ws: Path, prof: dict, explicit: str | None) -> list[str] | None:
    """Explicit > profile > tự dò theo đuôi file."""
    if explicit:
        return [x.strip() for x in explicit.split(",") if x.strip()]
    if prof.get("stacks"):
        return list(prof["stacks"])
    import skillselect
    return skillselect.detect_stacks(ws) or None


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


def install_global_rules(dry: bool) -> str:
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


def parse_packs(skills: list[dict], spec: str | None) -> set[str]:
    """`--exclude-pack a,b` → set tên pack; tên sai thì dừng trước khi ghi gì."""
    out = {p.strip() for p in (spec or "").split(",") if p.strip()}
    if not out:
        return out
    bad = out - {s["pack"] for s in skills}
    if bad:
        sys.exit(f"  Không có pack {', '.join(sorted(bad))}. "
                 f"Có: {', '.join(sorted({s['pack'] for s in skills}))}")
    return out


def do_core(skills: list[dict], dry: bool, force: bool,
            prune: bool = False) -> None:
    print(f"\n  Rules → {GLOBAL_RULES}")
    print(f"    {install_global_rules(dry)}")
    core = [s for s in skills if s["mode"] == "core"]
    print(f"\n  Skill global → {GLOBAL_SKILLS}  ({len(core)})")
    for s in core:
        print(f"    {copy_skill(s, GLOBAL_SKILLS, dry, force)} {s['id']}")

    ids = {s["id"] for s in core}
    if prune and GLOBAL_SKILLS.is_dir():
        extra = [d for d in GLOBAL_SKILLS.iterdir()
                 if d.is_dir() and d.name not in ids and (d / OWNER).is_file()]
        if extra and not dry:
            for d in extra:
                shutil.rmtree(d)
            print(f"    - đã gỡ {len(extra)} skill global, chỉ giữ {len(core)} skill core")
        elif extra:
            print(f"    · sẽ gỡ {len(extra)} skill global, chỉ giữ {len(core)} skill core")


def _desc_chars(sk: Path) -> int:
    """Số ký tự phần `description:` của một SKILL.md đã cài."""
    f = sk / "SKILL.md"
    if not f.is_file():
        return 0
    t = f.read_text(encoding="utf-8", errors="replace")
    a = t.find("description:")
    b = t.find("---", a + 3)
    return len(t[a:b]) if a != -1 and b != -1 else 0


def _desc_pack(s: dict) -> int:
    """Số ký tự description của một skill còn nằm trong packs/ (chưa cài)."""
    f = pack_dir(s) / "SKILL.md"
    if not f.is_file():
        return 0
    t = f.read_text(encoding="utf-8", errors="replace")
    a = t.find("description:")
    b = t.find("---", a + 3)
    return len(t[a:b]) if a != -1 and b != -1 else 0


def budget_ws(target: Path, projected: list[dict] | None = None) -> None:
    """Ngân sách của một workspace: skill global + skill riêng của project.

    `projected` = danh sách skill SẼ cài (dùng cho --dry-run, khi đĩa chưa đổi).
    Không truyền thì đo thật trên đĩa.
    """
    glob = ([d for d in GLOBAL_SKILLS.iterdir() if d.is_dir()]
            if GLOBAL_SKILLS.is_dir() else [])
    if projected is not None:
        own_n = len(projected)
        chars = sum(_desc_chars(d) for d in glob) + sum(_desc_pack(s) for s in projected)
        head = "Ngân sách dự kiến"
        tail = " (chưa ghi gì)"
    else:
        own = ([d for d in target.iterdir() if d.is_dir()] if target.is_dir() else [])
        own_n = len(own)
        chars = sum(_desc_chars(d) for d in glob + own)
        head = "Ngân sách workspace"
        tail = ""
    rules = ROOT / "core" / "AGENTS.md"
    r_chars = len(rules.read_text(encoding="utf-8")) if rules.is_file() else 0
    n = len(glob) + own_n
    tok = (chars + r_chars) // 4
    ui = 1497 + 102.2 * n
    mark = ("  ⚠ VƯỢT TRẦN — sẽ bị loại bớt" if ui > 20000
            else "  ⚠ sát trần (còn ~{:.0f} skill)".format((20000 - ui) / 102.2)
            if ui > 18000 else "")
    print(f"\n  {head}: {len(glob)} global + {own_n} riêng = {n} skill{tail}")
    print(f"    ước lượng {tok:,} token ≈ {tok/20000:.0%} · "
          f"đồng hồ Antigravity ≈ {ui:,.0f} ≈ {ui/20000:.0%}{mark}")


def budget(chosen: list[dict]) -> None:
    """Ước lượng ngân sách always-on.

    Antigravity cho 20.000 token cho rules always_on + description của skill.
    Cả `AGENTS.md` lẫn description đều ăn vào đó, nên đếm cả hai.
    """
    total = 0
    for s in chosen:
        p = pack_dir(s) / "SKILL.md"
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        a = t.find("description:")
        b = t.find("---", a + 3)
        if a != -1 and b != -1:
            total += len(t[a:b])
    rules = ROOT / "core" / "AGENTS.md"
    r_chars = len(rules.read_text(encoding="utf-8")) if rules.is_file() else 0
    tok = (total + r_chars) // 4
    pct = tok / 20000
    # Đồng hồ thật của Antigravity đếm cao hơn ước lượng ký-tự/4 của mình khoảng 1/4.
    # Hai điểm đo từ Settings → Skills: 195 skill = 21.430 token, 204 skill = 22.350.
    # Hồi quy ra: ui ≈ 1.497 + 102,2 × số skill. Con số trên là SÀN, không phải trần.
    ui = 1497 + 102.2 * len(chosen)
    ui_pct = ui / 20000
    flag = "  ⚠ đã gần trần" if pct > 0.85 else ""
    print(f"  Ngân sách: {tok:,} token ≈ {pct:.0%} trần 20k — "
          f"{len(chosen)} description + AGENTS.md{r_chars and f' ({r_chars:,} ký tự)'}{flag}")
    if ui_pct > 1.0:
        print(f"    đồng hồ Antigravity: ≈ {ui:,.0f} token ≈ {ui_pct:.0%}"
              "  ⚠ VƯỢT TRẦN — Antigravity sẽ tự loại bớt skill"
              "  → bớt pack: `--exclude-pack education,docs`")
    else:
        print(f"    đồng hồ Antigravity: ≈ {ui:,.0f} token ≈ {ui_pct:.0%}"
              + ("  ⚠ sát trần" if ui_pct > 0.95 else ""))


def do_system(skills: list[dict], dry: bool, force: bool,
              include_manual: bool = False,
              exclude_pack: str | None = None,
              prune: bool = False) -> None:
    """Cài TOÀN BỘ skill vào tầng global — mọi project đều thấy, không cần profile.

    Đánh đổi: workspace nào cũng nạp đủ danh sách skill, nên mất phần "cô lập cứng".
    Đổi lại: cài một lần, không phải làm gì cho từng project nữa.
    """
    skip_pack = parse_packs(skills, exclude_pack)

    print(f"\n  Rules → {GLOBAL_RULES}")
    print(f"    {install_global_rules(dry)}")
    chosen = [s for s in skills
              if s["mode"] != "system"
              and (s["mode"] != "manual" or include_manual)
              and s.get("global", True) is not False
              and s["pack"] not in skip_pack]
    project_only = [s for s in skills
                    if s["mode"] != "system" and s.get("global", True) is False]
    left_out = [s for s in skills
                if s["mode"] != "system" and s["pack"] in skip_pack]
    print(f"\n  Skill global → {GLOBAL_SKILLS}  ({len(chosen)})")

    by_pack: dict[str, int] = {}
    new = existing = 0
    for s in chosen:
        r = copy_skill(s, GLOBAL_SKILLS, dry, force)
        if r.startswith(("✓", "~", "=", "·")):
            by_pack[s["pack"]] = by_pack.get(s["pack"], 0) + 1
        if r.startswith(("✓", "~")):
            new += 1
        elif r.startswith("="):
            existing += 1
        if not r.startswith(("✓", "~", "=", "·")):
            print(f"    {r} — {s['id']}")

    if dry:
        print(f"\n  {sum(by_pack.values())} skill sẽ cài — "
              + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))
    elif new:
        print(f"\n  {new} skill mới, {existing} đã có — "
              + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))
    else:
        print(f"\n  {existing} skill đã có sẵn, không đổi gì.")

    # Thư mục có trên đĩa nhưng không thuộc bộ vừa cài: skill đã bị bỏ khỏi registry
    # ở bản trước vẫn nằm đó, ăn ngân sách và hiện trong danh sách của mọi project.
    expected = {s["id"] for s in chosen}
    have = {d.name for d in GLOBAL_SKILLS.iterdir() if d.is_dir()} if GLOBAL_SKILLS.is_dir() else set()
    extra = sorted(have - expected)
    if extra:
        mine = [x for x in extra if (GLOBAL_SKILLS / x / OWNER).is_file()]
        theirs = [x for x in extra if x not in mine]
        if prune and not dry and mine:
            for x in mine:
                shutil.rmtree(GLOBAL_SKILLS / x)
            print(f"  - đã xoá {len(mine)} thư mục của bản cũ: {', '.join(mine)}")
            extra, mine = theirs, []
        if mine:
            print(f"  {len(mine)} skill của bản cũ còn trên đĩa: {', '.join(mine)}")
            print("    — thêm `--prune` để xoá (chỉ xoá thư mục do Skill OS tạo).")
        if theirs:
            print(f"  {len(theirs)} thư mục KHÔNG phải của Skill OS: {', '.join(theirs)}")
            print("    — skill do Antigravity tự thêm hoặc bạn tự viết. Chúng cũng ăn ngân "
                  "sách always-on; giữ thì thôi, không muốn thì xoá tay:")
            for x in theirs:
                print(f"      rm -rf {GLOBAL_SKILLS / x}")
    if not include_manual:
        n_man = len([s for s in skills if s["mode"] == "manual"])
        if n_man:
            print(f"  {n_man} skill mode=manual không cài (thêm `--include-manual` nếu muốn).")

    if left_out:
        print(f"  {len(left_out)} skill bị loại theo --exclude-pack "
              f"({', '.join(sorted(skip_pack))}) — cài vào project cần bằng "
              "`bootstrap.sh <profile> <dir>`.")
    n_po = len(project_only)
    if n_po:
        print(f"  {n_po} skill theo ngôn ngữ/khung không cài vào global — "
              "dùng `bootstrap.sh <profile> <dir>` cho project cần.")
    budget(chosen)
    if not dry:
        GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
        (GLOBAL_DIR / "skill-os.json").write_text(json.dumps({
            "installed_by": "antigravity-skill-os",
            "mode": "system",
            "when": datetime.now().isoformat(timespec="seconds"),
            "skills": [s["id"] for s in chosen],
            "packs": dict(sorted(by_pack.items())),
            "always_on": "ponytail FULL + skill-first + verify (rules global)",
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def install_lsp(ws: Path, spec: str, dry: bool) -> None:
    """Đăng ký language server qua MCP. spec: '', 'auto', 'all', 'go,python'."""
    import lsp as lsp_mod

    print(f"\n  LSP → {ws / '.agents' / 'mcp_config.json'}")
    if spec.strip().lower() in ("", "auto"):
        langs = None
    elif spec.strip().lower() == "all":
        langs = list(lsp_mod.servers())
    else:
        langs = [x.strip() for x in spec.split(",") if x.strip()]
        bad = [x for x in langs if x not in lsp_mod.servers()]
        if bad:
            print(f"    ✗ không hỗ trợ: {', '.join(bad)}")
            return

    r = lsp_mod.install(ws, langs, dry=dry, copy_bridge=True)
    if r["written"]:
        n = len([s for s in r["servers"] if s.startswith("lsp-")])
        print(f"    → {n} language server đã nối. Khởi động lại Antigravity để nạp.")
    elif r["missing"]:
        print("    → chưa đăng ký gì: cài language server rồi chạy lại "
              "(`python3 tools/lsp.py --check`).")


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


def install_stack_rules(ws: Path, stacks: list[str] | None, dry: bool) -> tuple[list[str], int]:
    """Chép luật theo ngôn ngữ vào <ws>/.agents/rules/.

    Luôn cài `common.md`; mỗi ngôn ngữ dò được thì thêm `<ngôn ngữ>.md`.
    Không đè file lạ: file đã có mà không do Skill OS tạo thì bỏ qua và cảnh báo.
    """
    if not RULES_SRC.is_dir():
        return [], 0
    dest = ws / ".agents" / "rules"
    names = ["common"] + [s for s in (stacks or []) if (RULES_SRC / f"{s}.md").is_file()]
    manifest = dest / ".skill-os-rules.json"
    owned = set()
    if manifest.is_file():
        try:
            owned = set(json.loads(manifest.read_text(encoding="utf-8")).get("files", []))
        except ValueError:
            owned = set()

    written: list[str] = []
    changed = 0
    for n in names:
        src = RULES_SRC / f"{n}.md"
        if not src.is_file():
            continue
        out = dest / f"{n}.md"
        if out.exists() and n not in owned and out.read_bytes() != src.read_bytes():
            print(f"    ! {out.name} đã có và không do Skill OS tạo — giữ nguyên")
            continue
        if dry or (out.is_file() and out.read_bytes() == src.read_bytes()):
            written.append(n)
            continue
        dest.mkdir(parents=True, exist_ok=True)
        out.write_bytes(src.read_bytes())
        written.append(n)
        owned.add(n)
        changed += 1

    if not dry and written:
        manifest.write_text(json.dumps(
            {"files": sorted(owned), "stacks": sorted(stacks or [])},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return written, changed


EDU_WORDS = ("btvn", "bai-tap", "bai_giang", "giao-an", "lesson", "edu", "hoc",
             "truong", "lop", "de-thi", "de-kiem-tra", "curriculum")


def guess_profile(ws: Path) -> tuple[str | None, str]:
    """Đoán profile từ thứ có trong thư mục. Trả (id, lý do) hoặc (None, lý do)."""
    if not ws.is_dir():
        return None, "thư mục chưa tồn tại"
    skip = {"node_modules", "dist", "build", "target", "vendor", "packs"}
    files = []
    for f in ws.rglob("*"):
        if len(files) > 3000:
            break
        # Chỉ xét đường dẫn TƯƠNG ĐỐI. Dùng đường dẫn tuyệt đối thì workspace nằm
        # dưới …/.gemini/…, …/build/… hay …/target/… sẽ bị loại sạch và báo nhầm
        # "thư mục trống". Thư mục ẩn (.agents, .git, .venv) cũng bỏ qua.
        rel = f.relative_to(ws).parts
        if any(part.startswith(".") or part in skip for part in rel[:-1]):
            continue
        if f.is_file():
            files.append(f)
    if not files:
        return None, "thư mục trống"

    exts = {f.suffix.lower() for f in files}
    code = exts & {".py", ".go", ".rs", ".ts", ".tsx", ".js", ".jsx", ".java",
                   ".kt", ".cs", ".cpp", ".rb", ".php", ".dart", ".swift"}
    names = {f.name.lower() for f in files}
    blob = ""
    for n in ("package.json", "Cargo.toml"):
        f = ws / n
        if f.is_file():
            blob += f.read_text(encoding="utf-8", errors="replace")[:4000].lower()

    if {"pubspec.yaml", "app.json"} & names or "react-native" in blob or "expo" in blob:
        return "mobile-app", "có pubspec.yaml / react-native / expo"
    if ({"tauri.conf.json", "tauri.conf.json5", "electron-builder.yml"} & names
            or "src-tauri" in {p.name for p in ws.iterdir() if p.is_dir()}
            or "tauri" in blob or "electron" in blob or ".xaml" in exts):
        return "desktop-app", "có Tauri / Electron / WPF"
    lowered = str(ws).lower() + " " + " ".join(sorted(names)[:200])
    if any(w in lowered for w in EDU_WORDS) and not code:
        return "education-k12", "thư mục/tên file mang từ khóa giáo dục, không có code"
    if not code:
        if exts & {".docx", ".pptx", ".xlsx", ".pdf"}:
            return "docs-writer", "chỉ có tài liệu văn phòng"
        if exts <= {".md", ".txt", ""}:
            return "docs-writer", "chỉ có file văn bản"
        if exts & {".html", ".htm", ".css"}:
            return "static-site", "chỉ có HTML/CSS tĩnh, không có build tool"
    if ({"components.json", "tailwind.config.js", "tailwind.config.ts"} & names
            or (ws / "src" / "components" / "ui").is_dir()):
        return "design-system", "có cấu hình shadcn/Tailwind, thư viện component"
    if "package.json" in names or exts & {".tsx", ".jsx", ".vue", ".svelte"}:
        if (ws / "index.html").is_file() and "package.json" not in names:
            return "static-site", "có index.html nhưng không có package.json"
        return "web-admin", "có package.json / JSX / Vue"
    if code:
        return "cli-tool", "có code nhưng không có frontend"
    return None, "không nhận ra loại project"


def do_workspace(skills: list[dict], profiles: dict[str, dict],
                 profile: str, ws: Path, dry: bool, force: bool,
                 include_manual: bool = False, hooks: bool = False,
                 plugins: bool = False, lsp: str | None = None,
                 stacks: str | None = None, rules: bool = True,
                 prune: bool = False, exclude_pack: str | None = None) -> None:
    if profile not in profiles:
        sys.exit(f"  Không có profile '{profile}'. Có: {', '.join(profiles)}")
    prof = profiles[profile]
    stk = resolve_stacks(ws, prof, stacks)
    chosen = select_all(skills, prof, include_manual, stk)
    skip_pack = parse_packs(skills, exclude_pack)
    if skip_pack:
        dropped = [s for s in chosen if s["pack"] in skip_pack]
        chosen = [s for s in chosen if s["pack"] not in skip_pack]
        if dropped:
            print(f"  Bỏ {len(dropped)} skill theo --exclude-pack "
                  f"({', '.join(sorted(skip_pack))})")
    target = ws / ".agents" / "skills"
    print(f"\n  Profile : {profile} — {prof['label']}")
    print(f"  Stack   : {', '.join(stk) if stk else 'không lọc theo ngôn ngữ'}")
    # Skill đã cài ở tầng global thì mọi project đều đã thấy — chép lại chỉ tốn đĩa
    # và làm danh sách description dài gấp đôi.
    in_global = [s for s in chosen if (GLOBAL_SKILLS / s["id"] / OWNER).is_file()]
    if in_global:
        chosen = [s for s in chosen if s not in in_global]
    print(f"  Cài vào : {target}  ({len(chosen)} skill)")
    if in_global:
        print(f"    = {len(in_global)} skill đã có ở global — không chép lại "
              f"({GLOBAL_SKILLS})")
    by_pack: dict[str, int] = {}
    new = existing = 0
    for s in chosen:
        r = copy_skill(s, target, dry, force)
        print(f"    {r} {s['id']}")
        if r.startswith("✓") or r.startswith("~"):
            new += 1
        elif r.startswith("="):
            existing += 1
        if r.startswith(("✓", "~", "=", "·")):
            by_pack[s["pack"]] = by_pack.get(s["pack"], 0) + 1
    if rules:
        got, changed = install_stack_rules(ws, stk, dry)
        if got:
            mark = "·" if dry else ("+" if changed else "=")
            note = "" if changed or dry else "  (không đổi)"
            print(f"    {mark} rules: {', '.join(got)}{note}  →  {ws / '.agents' / 'rules'}")
    install_agents(prof.get("agent_groups", []), ws, dry, force)
    install_plugins(prof.get("plugins", []) if plugins else [], ws, dry, force)
    if hooks:
        install_hooks(ws, dry, force)
    if lsp is not None:
        install_lsp(ws, lsp, dry)
    do_manifest(target, chosen, profile, dry)
    skipped = len([s for s in skills if s["mode"] != "system"]) - len(chosen)
    if dry:
        print(f"\n  {sum(by_pack.values())} skill sẽ cài — "
              + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))
    elif new:
        print(f"\n  {new} skill mới, {existing} đã có sẵn — "
              + ", ".join(f"{k} {v}" for k, v in sorted(by_pack.items())))
    elif in_global and not target.exists():
        print(f"\n  không có gì để chép — toàn bộ {len(in_global)} skill của profile "
              "đã có ở tầng global.")
    else:
        print(f"\n  {existing} skill đã có sẵn, không đổi gì — workspace đã cài rồi.")
    print(f"  {skipped} skill bị loại khỏi workspace này (cô lập cứng).")
    if target.is_dir():
        ids = {s["id"] for s in chosen}
        stale = [d for d in target.iterdir()
                 if d.is_dir() and d.name not in ids and (d / OWNER).is_file()]
        if stale and prune:
            for d in stale:
                shutil.rmtree(d)
            print(f"  - đã gỡ {len(stale)} skill của profile cũ trong workspace")
        elif stale:
            print(f"  {len(stale)} skill của profile cũ còn trong workspace "
                  f"(đổi profile mà không dọn) — thêm `--prune` để gỡ.")
    budget_ws(target, projected=chosen if dry else None)
    if in_global:
        n_glob = len([d for d in GLOBAL_SKILLS.iterdir() if (d / OWNER).is_file()])
        print(f"  ⚠  global đang bật {n_glob} skill: project này vẫn thấy hết. "
              "Cô lập đúng chỉ khi global mỏng — dùng `--core` thay `--system`.")
    cap = prof.get("max_skills")
    if cap and len(chosen) > cap:
        print(f"  ⚠  {len(chosen)} skill > trần {cap} của profile — "
              "danh sách description dài, agent dễ chọn sai.")


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
    ap.add_argument("--core", action="store_true",
                    help="cài rules + 4 skill global tối thiểu")
    ap.add_argument("--system", action="store_true",
                    help="cài TOÀN BỘ skill vào global — mọi project đều có, "
                         "không cần --profile cho từng project")
    ap.add_argument("--profile",
                    help="id profile, hoặc 'auto' để tự dò theo nội dung thư mục")
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
    ap.add_argument("--lsp", nargs="?", const="auto", default=None, metavar="LANGS",
                    help="nối language server qua MCP: bỏ trống = tự dò theo "
                         "workspace, hoặc 'all', hoặc 'go,python,rust' "
                         "(mặc định theo profile)")
    ap.add_argument("--no-lsp", action="store_true", help="tắt LSP dù profile có bật")
    ap.add_argument("--no-rules", action="store_true",
                    help="không cài luật theo ngôn ngữ vào .agents/rules/")
    ap.add_argument("--prune", action="store_true",
                    help="với --system: xoá thư mục skill còn sót từ bản cũ "
                         "(chỉ xoá cái do Skill OS tạo)")
    ap.add_argument("--exclude-pack", metavar="PACKS",
                    help="với --system: bỏ hẳn pack khỏi tầng global "
                         "(vd 'education,docs') để danh sách skill gọn hơn")
    ap.add_argument("--stacks", metavar="LIST",
                    help="lọc skill theo ngôn ngữ: 'python,go'. Bỏ trống = tự dò "
                         "theo đuôi file trong workspace")
    a = ap.parse_args()

    skills, profiles = load()
    dry = a.dry_run
    if dry:
        print("  [DRY RUN] không ghi gì cả")

    if a.list:
        do_list(skills)
    if a.core:
        do_core(skills, dry, a.force, a.prune)
    if a.system:
        do_system(skills, dry, a.force, a.include_manual, a.exclude_pack, a.prune)
    if a.profile:
        if a.profile == "auto":
            guess, why = guess_profile(Path(a.workspace).expanduser().resolve())
            if not guess:
                sys.exit(f"  Không tự đoán được profile ({why}). "
                         f"Chỉ định tay: {', '.join(sorted(profiles))}")
            print(f"\n  Tự dò profile: {guess}  ({why})")
            a.profile = guess
        lsp_spec = a.lsp
        if a.no_lsp:
            lsp_spec = None
        elif lsp_spec is None and profiles.get(a.profile, {}).get("lsp"):
            lsp_spec = "auto"
        do_workspace(skills, profiles, a.profile, Path(a.workspace).expanduser().resolve(),
                     dry, a.force, a.include_manual, a.hooks, a.plugins, lsp_spec,
                     a.stacks, not a.no_rules, a.prune, a.exclude_pack)
    if a.uninstall:
        do_uninstall(skills, dry)
    if not any([a.list, a.core, a.system, a.profile, a.uninstall]):
        ap.print_help()
    print()


if __name__ == "__main__":
    main()
