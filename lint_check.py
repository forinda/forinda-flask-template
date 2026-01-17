#!/usr/bin/env python3
"""
Quick linting script for development.
Run: python lint_check.py
"""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f'\n{"=" * 60}')
    print(f'{description}')
    print(f'{"=" * 60}\n')

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f'\n✓ {description} passed')
        return True
    except subprocess.CalledProcessError:
        print(f'\n✗ {description} failed')
        return False


def main():
    """Run all linting checks."""
    print('Starting code quality checks...\n')

    checks = [
        (['pipenv', 'run', 'ruff', 'check', '.'], 'Ruff Linter'),
        (['pipenv', 'run', 'ruff', 'format', '--check', '.'], 'Ruff Formatter Check'),
    ]

    results = []
    for cmd, desc in checks:
        results.append(run_command(cmd, desc))

    # Summary
    print(f'\n{"=" * 60}')
    print('SUMMARY')
    print(f'{"=" * 60}')

    for (_, desc), passed in zip(checks, results):
        status = '✓ PASSED' if passed else '✗ FAILED'
        print(f'{desc}: {status}')

    if all(results):
        print('\n✓ All checks passed!')
        return 0
    print('\n✗ Some checks failed. Run `./lint.sh` to fix issues.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
