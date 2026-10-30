#!/usr/bin/env python3
"""Offline structural and isolation checks for the reviewed vibe-coding cohort.

These checks are not a security audit or proof that example code runs in every stack.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import skillselect
import vendor

COHORT = {
    'mocha-skill': 'typescript', 'vitest-skill': 'typescript',
    'nunit-skill': 'csharp', 'xunit-skill': 'csharp',
    'rspec-skill': 'ruby', 'phpunit-skill': 'php', 'test-fixing': 'general',
    'pytest-skill': 'python', 'unittest-skill': 'python',
    'junit-5-skill': 'java', 'testng-skill': 'java', 'mstest-skill': 'csharp',
    'testunit-skill': 'ruby', 'jest-skill': 'typescript', 'jasmine-skill': 'typescript',
    'lint-and-validate': 'general',
}


def inspect_skill(directory, skill_id):
    """Return deterministic review errors; does not execute third-party content."""
    errors = []
    sk = directory / 'SKILL.md'
    if not sk.is_file():
        return ['missing SKILL.md']
    text = sk.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not match:
        return ['invalid frontmatter']
    if not re.search(r'^name: ' + re.escape(skill_id) + r'\s*$', match[1], re.M):
        errors.append('name mismatch')
    if not re.search(r'^description: .{10,}', match[1], re.M):
        errors.append('missing description')
    if len(text) < 300 or len(text.encode()) > 24000:
        errors.append('unexpected SKILL.md size')
    for ref in set(re.findall(r'\breference/[\w.-]+\.md\b', text)):
        if not (directory / ref).is_file():
            errors.append('missing ' + ref)
    for file in directory.rglob('*'):
        if file.is_symlink():
            errors.append('symlink: ' + str(file.relative_to(directory)))
        if file.is_file() and file.suffix == '.md':
            data = file.read_text(encoding='utf-8')
            for pattern in (r'\$\{CLAUDE_SKILL_DIR\}', r'\.claude/',
                            r'(?i)ignore (?:all |previous )+(?:instructions|rules)',
                            r'(?i)curl[^\n]*\|\s*(?:ba)?sh\b'):
                if re.search(pattern, data):
                    errors.append('review required: ' + pattern)
    return errors


class ReviewChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / 'registry/skills.json').read_text())['skills']
        cls.by_id = {s['id']: s for s in cls.registry}
        cls.manifest = json.loads((ROOT / 'packs/VENDOR.json').read_text())['skills']
        cls.review_hashes = json.loads((ROOT / 'registry/vibe-review-hashes.json').read_text())

    def test_each_candidate(self):
        for name, stack in COHORT.items():
            with self.subTest(skill=name):
                s = self.by_id[name]
                self.assertEqual(s['stack'], [stack])
                self.assertFalse(s.get('global', True))
                self.assertEqual(s['domain'], ['code'])
                self.assertRegex(s['ref'], r'^[0-9a-f]{40}$')
                d = ROOT / 'packs' / s['pack'] / name
                self.assertEqual(inspect_skill(d, name), [])
                actual = {str(f.relative_to(d)).replace(os.sep, '/'): hashlib.sha256(f.read_bytes()).hexdigest()
                          for f in d.rglob('*') if f.is_file()}
                self.assertEqual(actual, self.review_hashes[name], 'reviewed files changed')
                self.assertEqual(hashlib.sha256((d / 'SKILL.md').read_bytes()).hexdigest(),
                                 self.manifest[name]['sha256'])
                self.assertEqual(self.manifest[name]['source'], s['repo'] + '@' + s['ref'])

    def test_vendor_check_rejects_modified_or_missing_skill(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(vendor, 'PACKS', Path(tmp)):
            d = Path(tmp) / 'code' / 'example'
            d.mkdir(parents=True)
            f = d / 'SKILL.md'
            f.write_text('original', encoding='utf-8')
            skills = [{'id': 'example', 'pack': 'code', 'mode': 'auto'}]
            manifest = {'skills': {'example': {'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}}}
            self.assertEqual(vendor.check(skills, manifest), 0)
            f.write_text('changed', encoding='utf-8')
            self.assertEqual(vendor.check(skills, manifest), 1)
            f.unlink()
            self.assertEqual(vendor.check(skills, manifest), 1)
            f.write_text('original', encoding='utf-8')
            manifest['skills']['example']['sha256'] = None
            self.assertEqual(vendor.check(skills, manifest), 1)

    def test_checker_rejects_missing_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / 'SKILL.md').write_text('---\nname: sample\ndescription: sample description\n---\n' +
                                        'x' * 300 + '\nreference/missing.md\n')
            self.assertIn('missing reference/missing.md', inspect_skill(d, 'sample'))

    def test_profile_and_stack_selection(self):
        code = json.loads((ROOT / 'profiles/cli-tool.json').read_text())
        education = json.loads((ROOT / 'profiles/education-k12.json').read_text())
        for stack in ('typescript', 'csharp', 'ruby', 'php', 'python', 'java'):
            chosen = {s['id'] for s in skillselect.select(self.registry, code, stacks=[stack])}
            for name, required in COHORT.items():
                self.assertEqual(name in chosen, required in (stack, 'general'), name)
        chosen = {s['id'] for s in skillselect.select(self.registry, education, stacks=['typescript'])}
        self.assertFalse(chosen & COHORT.keys())

    def test_python_example_syntax_and_unittest_execution(self):
        for name in ('pytest-skill', 'unittest-skill'):
            for file in (ROOT / 'packs/code' / name).rglob('*.md'):
                for block in re.findall(r'```python\n(.*?)```', file.read_text(), re.S):
                    with self.subTest(file=str(file), block=block[:40]):
                        ast.parse(block)
        text = (ROOT / 'packs/code/unittest-skill/SKILL.md').read_text()
        example = re.search(r'```python\n(.*?)```', text, re.S).group(1)
        stub = ('class Calculator:\n'
                '    def add(self, a, b): return a + b\n'
                '    def subtract(self, a, b): return a - b\n'
                '    def divide(self, a, b): return a / b\n\n')
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / 'example.py'
            script.write_text(stub + example)
            result = subprocess.run([sys.executable, str(script)], capture_output=True,
                                    text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Ran 3 tests', result.stderr)

    def test_system_does_not_install_cohort(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp, USERPROFILE=tmp)
            result = subprocess.run([sys.executable, str(ROOT / 'tools/install.py'),
                                     '--system', '--dry-run'], env=env,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in COHORT:
                self.assertNotRegex(result.stdout, r'(?m)^\s*·\s+' + re.escape(name) + r'\s*$')

    def test_actual_install_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = dict(os.environ, HOME=str(root / 'home'), USERPROFILE=str(root / 'home'))
            for profile, stacks in [('cli-tool', 'typescript'), ('education-k12', 'typescript')]:
                ws = root / profile
                ws.mkdir()
                result = subprocess.run([sys.executable, str(ROOT / 'tools/install.py'),
                    '--profile', profile, '-w', str(ws), '--stacks', stacks, '--no-lsp'],
                    env=env, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                installed = {p.name for p in (ws / '.agents/skills').iterdir() if p.is_dir()}
                if profile == 'education-k12':
                    self.assertFalse(installed & COHORT.keys())
                else:
                    self.assertTrue({'vitest-skill', 'mocha-skill', 'test-fixing'} <= installed)
                    self.assertFalse({'nunit-skill', 'rspec-skill', 'phpunit-skill'} & installed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
