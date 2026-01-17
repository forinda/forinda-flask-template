# Ruff Linting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

## Quick Start

### Run linter
```bash
pipenv run ruff check .
```

### Auto-fix issues
```bash
pipenv run ruff check --fix .
```

### Format code
```bash
pipenv run ruff format .
```

### Check and format
```bash
pipenv run ruff check --fix . && pipenv run ruff format .
```

## Configuration

Ruff is configured in [pyproject.toml](pyproject.toml) with:
- **Line length**: 120 characters
- **Target**: Python 3.12
- **Enabled rules**: pycodestyle, pyflakes, isort, pyupgrade, flake8-bugbear, pylint, and more
- **Import sorting**: Automatic with isort
- **Code formatting**: Single quotes, 4-space indentation

## Rules

### Enabled Rule Sets
- `E`, `W` - pycodestyle (PEP 8 style)
- `F` - pyflakes (logical errors)
- `I` - isort (import sorting)
- `N` - pep8-naming (naming conventions)
- `UP` - pyupgrade (Python version upgrades)
- `B` - flake8-bugbear (bug detection)
- `C4` - flake8-comprehensions (comprehension optimization)
- `PT` - flake8-pytest-style (pytest best practices)
- `PL` - pylint (code quality)
- `TRY` - tryceratops (exception handling)
- `RUF` - ruff-specific rules

### Ignored Rules
- Line length enforcement (handled by formatter)
- Some overly strict pylint rules (too many arguments, branches)
- Test-specific rules in `tests/` directory

## VS Code Integration

Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": true,
      "source.organizeImports.ruff": true
    }
  }
}
```

Install the [Ruff VS Code extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

## Pre-commit Hook

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Lint with ruff
  run: |
    pipenv install --dev
    pipenv run ruff check .
    pipenv run ruff format --check .
```

## Common Commands

| Command | Description |
|---------|-------------|
| `ruff check .` | Check all files for linting errors |
| `ruff check --fix .` | Auto-fix linting errors |
| `ruff format .` | Format all files |
| `ruff format --check .` | Check if files are formatted |
| `ruff check --watch .` | Watch mode for development |
| `ruff check --diff .` | Show diffs for fixes |
| `ruff check --statistics .` | Show statistics about violations |

## File-Specific Ignores

- `__init__.py` - Allows unused imports (F401, F403)
- `tests/**` - Relaxed rules for test files

## Tips

1. **Run before committing**: Always run `ruff check --fix . && ruff format .`
2. **Fix imports**: Ruff automatically sorts and organizes imports
3. **Incremental adoption**: Use `# noqa: <rule>` to ignore specific violations temporarily
4. **Performance**: Ruff is 10-100x faster than traditional linters
