#!/usr/bin/env python3
"""外部ジャッジに接続せず、STANDALONE の検証をすべて実行する。"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', default=shutil.which('pypy3') or sys.executable)
    parser.add_argument('--timeout', type=float, default=60)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1')
    files = sorted(p for p in (root / 'python').rglob('*.py')
                   if '# competitive-verifier: STANDALONE' in p.read_text(encoding='utf-8-sig'))
    print(f'Python: {args.python}', flush=True)
    failures = []
    for path in files:
        try:
            result = subprocess.run([args.python, str(path)], cwd=root, env=env,
                                    capture_output=True, text=True, timeout=args.timeout)
            ok = result.returncode == 0
            if not ok:
                print(result.stdout + result.stderr, end='')
        except subprocess.TimeoutExpired:
            ok = False
            print(f'Timeout: {args.timeout}s')
        except OSError as exc:
            parser.error(str(exc))
        relative = path.relative_to(root)
        print(f'{"PASS" if ok else "FAIL"} {relative}', flush=True)
        if not ok:
            failures.append(relative)
    print(f'{len(files) - len(failures)}/{len(files)} passed')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
