#!/usr/bin/env python3
"""Integration tests for owned-only skill updates in an isolated HOME."""
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / 'tools/install.py'


class OwnedUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home'
        self.home.mkdir()
        self.ws = Path(self.temp.name) / 'workspace'
        self.ws.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                        SKILL_OS_HOME=str(self.home / '.gemini'),
                        SKILL_OS_CACHE=str(self.home / 'cache'))
        self.profile = ['--profile', 'cli-tool', '-w', str(self.ws),
                        '--stacks', 'typescript', '--no-lsp']

    def install(self, *args):
        proc = subprocess.run([sys.executable, str(INSTALL), *args], env=self.env,
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc.stdout

    def test_workspace_update_preserves_unmanaged(self):
        self.install(*self.profile)
        skills = self.ws / '.agents/skills'
        owned = skills / 'jest-skill/SKILL.md'
        unmanaged = skills / 'vitest-skill/SKILL.md'
        owned.write_text('modified owned', encoding='utf-8')
        (unmanaged.parent / '.skill-os-owner').unlink()
        unmanaged.write_text('user data', encoding='utf-8')
        dry = self.install(*self.profile, '--update-owned', '--dry-run')
        self.assertIn('~ sẽ ghi đè jest-skill', dry)
        self.assertIn('! đã tồn tại, không do Skill OS tạo', dry)
        self.assertEqual(owned.read_text(), 'modified owned')
        self.install(*self.profile, '--update-owned')
        self.assertEqual(owned.read_bytes(), (ROOT / 'packs/code/jest-skill/SKILL.md').read_bytes())
        self.assertEqual(unmanaged.read_text(), 'user data')
        self.assertFalse((unmanaged.parent / '.skill-os-owner').exists())

    @unittest.skipUnless(shutil.which('bash'), 'bash is required for bootstrap tests')
    def test_bootstrap_dry_run_never_writes(self):
        for args in (['--core'], ['--system'], ['cli-tool', str(self.ws / 'new')]):
            with self.subTest(args=args):
                result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), *args,
                                         '--dry-run', '--update-owned'], env=self.env,
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('Dry-run hoàn tất', result.stdout)
                self.assertFalse((self.home / '.gemini').exists())
                self.assertEqual(list(self.ws.iterdir()), [])

    @unittest.skipUnless(shutil.which('bash'), 'bash is required for bootstrap tests')
    def test_bootstrap_dry_run_without_repo_does_not_clone(self):
        script = self.home / 'bootstrap.sh'
        script.write_bytes((ROOT / 'bootstrap.sh').read_bytes())
        result = subprocess.run(['bash', str(script), '--core', '--dry-run'],
                                env=self.env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Dry-run cần repo đã có sẵn', result.stderr)
        self.assertFalse((self.home / 'cache').exists())
        self.assertFalse((self.home / '.gemini').exists())

    def test_system_update_preserves_unmanaged(self):
        self.install('--system')
        skills = self.home / '.gemini/config/skills'
        owned = skills / 'test-driven-development/SKILL.md'
        unmanaged = skills / 'systematic-debugging/SKILL.md'
        owned.write_text('old content', encoding='utf-8')
        (unmanaged.parent / '.skill-os-owner').unlink()
        unmanaged.write_text('user data', encoding='utf-8')
        self.install('--system', '--update-owned')
        self.assertEqual(owned.read_bytes(),
                         (ROOT / 'packs/code/test-driven-development/SKILL.md').read_bytes())
        self.assertEqual(unmanaged.read_text(), 'user data')

    @unittest.skipIf(os.name == 'nt' or not shutil.which('bash'),
                     'POSIX PATH isolation test requires bash')
    def test_bootstrap_falls_back_to_python(self):
        tools = self.home / 'bin'
        tools.mkdir()
        (tools / 'python').symlink_to(sys.executable)
        (tools / 'dirname').symlink_to(shutil.which('dirname'))
        env = dict(self.env, PATH=str(tools))
        result = subprocess.run([shutil.which('bash'), str(ROOT / 'bootstrap.sh'), '--core', '--dry-run'],
                                env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Dry-run hoàn tất', result.stdout)
        self.assertFalse((self.home / '.gemini').exists())

    @unittest.skipUnless(shutil.which('bash'), 'bash is required for bootstrap tests')
    def test_bootstrap_core_update_flag(self):
        self.install('--core')
        owned = self.home / '.gemini/config/skills/handoff/SKILL.md'
        owned.write_text('old content', encoding='utf-8')
        result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), '--core', '--update-owned'],
                                env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(owned.read_bytes(), (ROOT / 'packs/meta/handoff/SKILL.md').read_bytes())

    @unittest.skipUnless(shutil.which('bash'), 'bash is required for bootstrap tests')
    def test_bootstrap_workspace_update_flag(self):
        self.install(*self.profile)
        owned = self.ws / '.agents/skills/jest-skill/SKILL.md'
        owned.write_text('old content', encoding='utf-8')
        result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), 'cli-tool', str(self.ws),
                                 '--update-owned', '--no-lsp', '--no-hooks', '--no-plugins'],
                                env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(owned.read_bytes(), (ROOT / 'packs/code/jest-skill/SKILL.md').read_bytes())

    def test_core_update_does_not_override_unmanaged(self):
        self.install('--core')
        skills = self.home / '.gemini/config/skills'
        owned = skills / 'handoff/SKILL.md'
        unmanaged = skills / 'writing-skills/SKILL.md'
        owned.write_text('old content', encoding='utf-8')
        (unmanaged.parent / '.skill-os-owner').unlink()
        unmanaged.write_text('user data', encoding='utf-8')
        self.install('--core', '--update-owned')
        self.assertEqual(owned.read_bytes(), (ROOT / 'packs/meta/handoff/SKILL.md').read_bytes())
        self.assertEqual(unmanaged.read_text(), 'user data')


if __name__ == '__main__':
    unittest.main(verbosity=2)
