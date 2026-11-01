#!/usr/bin/env python3
"""Offline regression checks for grounded verification rules and skills.

These test packaging, selection and installation, not agent behaviour in Antigravity.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import skillselect
import vendor

SKILLS = {
    'reference-existence-check': ('SpawnZilla/agent-skills', '60a035f526aae36a499e6a6ef3836bebdf44d917'),
    'integration-reality-checker': ('aradmanamnaoon/vibe-coding-skills', 'd532b2b52725cbd92b2815fbc98e1e516503137b'),
    'dependency-grounding-auditor': ('aradmanamnaoon/vibe-coding-skills', 'd532b2b52725cbd92b2815fbc98e1e516503137b'),
    'completion-claims-auditor': ('aradmanamnaoon/vibe-coding-skills', 'd532b2b52725cbd92b2815fbc98e1e516503137b'),
}


class GroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = json.loads((ROOT / 'registry/skills.json').read_text(encoding='utf-8'))['skills']
        cls.index = {s['id']: s for s in cls.skills}
        cls.manifest = json.loads((ROOT / 'packs/VENDOR.json').read_text(encoding='utf-8'))['skills']

    def test_candidates_and_adaptations(self):
        for name, (repo, commit) in SKILLS.items():
            with self.subTest(skill=name):
                s = self.index[name]
                self.assertEqual((s['repo'], s['ref']), (repo, commit))
                self.assertEqual((s['pack'], s['domain'], s['stack'], s['global']),
                                 ('code', ['code'], ['general'], False))
                p = ROOT / 'packs/code' / name / 'SKILL.md'
                text = p.read_text(encoding='utf-8')
                self.assertRegex(text, r'\A---\nname: ' + re.escape(name) + r'\ndescription: .+\n---')
                self.assertGreater(len(text), 500)
                self.assertEqual(vendor.sha(p), self.manifest[name]['sha256'])
                self.assertEqual(self.manifest[name]['source'], repo + '@' + commit)
                self.assertNotIn('research/vibe-coding-problems.md', text)
                self.assertNotIn('existence-verification-escalation tiers', text)
        self.assertIn('not proof that a real external service works',
                      (ROOT / 'packs/code/integration-reality-checker/SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('do not require a planned new output file to exist',
                      (ROOT / 'packs/code/reference-existence-check/SKILL.md').read_text(encoding='utf-8'))
        self.assertNotIn('maintenance, license,',
                         (ROOT / 'packs/code/dependency-grounding-auditor/SKILL.md').read_text(encoding='utf-8'))

    def test_vendor_trim_eof_is_opt_in_and_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            skill = d / 'SKILL.md'
            licence = d / 'LICENSE'
            skill.write_bytes(b'---\nname: sample\n---\n\nbody\n\n')
            licence.write_bytes(b'text\n\n')
            vendor.patch_skill(d, {'id': 'sample'})
            self.assertTrue(skill.read_bytes().endswith(b'\n\n'))
            vendor.patch_skill(d, {'id': 'sample', 'trim_eof': True})
            self.assertTrue(skill.read_bytes().endswith(b'body\n'))
            self.assertEqual(licence.read_bytes(), b'text\n')
            before = skill.read_bytes()
            vendor.patch_skill(d, {'id': 'sample', 'trim_eof': True})
            self.assertEqual(skill.read_bytes(), before)

    def test_domain_and_stack_selection(self):
        cli = json.loads((ROOT / 'profiles/cli-tool.json').read_text(encoding='utf-8'))
        edu = json.loads((ROOT / 'profiles/education-k12.json').read_text(encoding='utf-8'))
        for stack in ('python', 'typescript', 'java'):
            selected = {s['id'] for s in skillselect.select(self.skills, cli, stacks=[stack])}
            self.assertTrue(SKILLS.keys() <= selected)
        selected = {s['id'] for s in skillselect.select(self.skills, edu)}
        self.assertFalse(SKILLS.keys() & selected)

    def test_core_and_workspace_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / 'home'
            env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                       SKILL_OS_HOME=str(home / '.gemini'))
            workspaces = {profile: Path(tmp) / profile for profile in ('cli-tool', 'education-k12')}
            for ws in workspaces.values():
                ws.mkdir()
            for args in (['--core'], ['--profile', 'cli-tool', '-w', str(workspaces['cli-tool']),
                                      '--stacks', 'python', '--no-lsp'],
                         ['--profile', 'education-k12', '-w', str(workspaces['education-k12']), '--no-lsp']):
                result = subprocess.run([sys.executable, str(ROOT / 'tools/install.py'), *args],
                                        env=env, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            core = (home / '.gemini/AGENTS.md').read_text(encoding='utf-8')
            self.assertIn('An empty search is not proof of absence', core)
            self.assertIn('successful health check, mock, or exit code', core)
            glob = {p.name for p in (home / '.gemini/config/skills').iterdir() if p.is_dir()}
            code = {p.name for p in (workspaces['cli-tool'] / '.agents/skills').iterdir() if p.is_dir()}
            education = {p.name for p in (workspaces['education-k12'] / '.agents/skills').iterdir() if p.is_dir()}
            self.assertEqual(len(glob), 4)
            self.assertTrue(SKILLS.keys() <= code)
            self.assertFalse(SKILLS.keys() & (glob | education))
            self.assertEqual(len(education), 24)


if __name__ == '__main__':
    unittest.main(verbosity=2)
