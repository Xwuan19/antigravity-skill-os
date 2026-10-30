#!/usr/bin/env python3
"""Run five vendored skill examples against preinstalled test frameworks.

No dependencies are fetched. Supply paths to an existing pytest target and an npm
prefix with jest, jasmine, mocha, chai and vitest installed; fixtures are synthetic.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def sample(skill, language):
    text = (ROOT / 'packs' / 'code' / skill / 'SKILL.md').read_text(encoding='utf-8')
    found = re.search(r'```' + re.escape(language) + r'\n(.*?)```', text, re.S)
    if not found:
        raise ValueError(f'{skill}: example missing')
    return found.group(1)


def run(label, cmd, cwd, env=None):
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
    print(f'\n{label}: exit {result.returncode}', flush=True)
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node-prefix', required=True, type=Path,
                        help='npm prefix containing node_modules')
    parser.add_argument('--python-path', required=True, type=Path,
                        help='directory containing preinstalled pytest')
    args = parser.parse_args()
    node_modules = args.node_prefix.resolve() / 'node_modules'
    if not node_modules.is_dir() or not (args.python_path / 'pytest').is_dir():
        parser.error('provided dependency paths do not contain node_modules / pytest')
    if not shutil.which('node'):
        parser.error('node is not available')
    ok = True
    with tempfile.TemporaryDirectory(prefix='skill-os-examples-') as tmp:
        project = Path(tmp)
        # POSIX symlink is not always available on Windows: put temp files under the
        # existing npm prefix instead, so Node can resolve its parent node_modules.
        with tempfile.TemporaryDirectory(prefix='skill-os-test-', dir=args.node_prefix) as js_tmp:
            js = Path(js_tmp)
            calc = ("class Calculator { add(a,b) {return a+b} divide(a,b) {"
                    "if (b===0) throw new Error('Division by zero'); return a/b} }\n")
            for framework in ('jest', 'jasmine', 'mocha'):
                (js / f'{framework}.test.js').write_text(
                    calc + sample(framework + '-skill', 'javascript'), encoding='utf-8')
            (js / 'vitest.test.ts').write_text(sample('vitest-skill', 'typescript'), encoding='utf-8')
            (js / 'calculator.ts').write_text(
                'export class Calculator { add(a:number,b:number){return a+b} '
                'divide(a:number,b:number){if(!b)throw new Error("Division by zero");return a/b} }\n',
                encoding='utf-8')
            # Direct JS entrypoints work on both Windows and POSIX without shell=True.
            commands = [
                ('jest', ['jest/bin/jest.js', '--runInBand', '--runTestsByPath',
                          'jest.test.js', '--no-cache', '--config', '{"rootDir":"."}']),
                ('jasmine', ['jasmine/bin/jasmine.js', 'jasmine.test.js']),
                ('mocha', ['mocha/bin/mocha.js', 'mocha.test.js']),
                ('vitest', ['vitest/vitest.mjs', 'run', 'vitest.test.ts']),
            ]
            for name, cmd in commands:
                ok = run(name, ['node', str(node_modules / cmd[0]), *cmd[1:]], js) and ok
        stub = ('class Calculator:\n    def add(self,a,b): return a+b\n'
                '    def divide(self,a,b): return a/b\n\n')
        (project / 'test_example.py').write_text(stub + sample('pytest-skill', 'python'), encoding='utf-8')
        env = dict(os.environ, PYTHONPATH=str(args.python_path.resolve()), PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        ok = run('pytest', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                            'test_example.py'], project, env) and ok
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
