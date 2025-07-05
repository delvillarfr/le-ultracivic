# Code Quality Guidelines

## Overview

This project maintains high code quality standards using automated tools and pre-commit hooks. All code is formatted consistently and follows security best practices.

## Tools Used

### Formatting
- **Black**: Opinionated Python code formatter
- **Ruff Format**: Fast Python formatter (alternative to Black)

### Linting
- **Ruff**: Fast Python linter (replaces flake8, isort, pyupgrade, etc.)
  - Enforces code style (PEP 8)
  - Import sorting
  - Code complexity checks
  - Security patterns

### Security
- **Bandit**: Security vulnerability scanner for Python

### Pre-commit Hooks
- File formatting (trailing whitespace, end-of-file)
- YAML/TOML/JSON validation
- Merge conflict detection
- Python AST validation

## Quick Start

### Setup Development Environment
```bash
# Install dependencies
make install

# Install pre-commit hooks
make pre-commit-install

# Or manually:
poetry install
poetry run pre-commit install
```

### Manual Code Quality Checks
```bash
# Format code
make format
poetry run python scripts/format.py

# Run linting
make lint
poetry run python scripts/lint.py

# Comprehensive quality check
make check
poetry run python scripts/check.py

# Run all pre-commit hooks
make pre-commit-all
poetry run pre-commit run --all-files
```

## Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. They will:

1. **Format Code**: Apply Black and Ruff formatting
2. **Lint Code**: Check for style and security issues
3. **Validate Files**: Check YAML, TOML, JSON syntax
4. **Security Scan**: Run Bandit security checks

### Bypassing Hooks (Not Recommended)
```bash
# Skip pre-commit hooks (emergency only)
git commit --no-verify -m "Emergency commit"
```

## Code Style Standards

### Python Code Style
- **Line Length**: 88 characters (Black default)
- **String Quotes**: Double quotes preferred
- **Import Sorting**: Automatic with Ruff
- **Type Hints**: Encouraged but not required

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Methods**: `_leading_underscore`

### Code Organization
```python
# Standard library imports
import os
import sys

# Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from app.config import settings
from app.models import User
```

## Security Guidelines

### Bandit Checks
The following security patterns are automatically detected:

- **SQL Injection**: Raw SQL queries
- **Command Injection**: Shell command execution
- **Hard-coded Secrets**: Passwords, keys in code
- **Weak Cryptography**: Insecure hash functions
- **File Permissions**: Insecure file operations

### Security Best Practices
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Use parameterized queries for database operations
- Follow principle of least privilege

## CI/CD Integration

### GitHub Actions (Future)
```yaml
- name: Code Quality
  run: |
    poetry run python scripts/check.py
    poetry run pre-commit run --all-files
```

### Local Testing
```bash
# Test what CI will run
make check

# Quick quality assurance
make qa
```

## Troubleshooting

### Common Issues

#### 1. Pre-commit Hook Failures
```bash
# Update hooks
poetry run pre-commit autoupdate

# Clear cache and reinstall
poetry run pre-commit clean
poetry run pre-commit install
```

#### 2. Import Sorting Issues
```bash
# Fix import sorting
poetry run ruff check --select I --fix app/
```

#### 3. Formatting Conflicts
```bash
# Apply formatting
poetry run black app/
poetry run ruff format app/
```

#### 4. Security Scan False Positives
Add to `pyproject.toml`:
```toml
[tool.bandit]
skips = ["B101", "B601"]  # Skip specific tests
exclude_dirs = ["tests"]
```

### Getting Help

1. **Check Tool Documentation**:
   - [Ruff](https://docs.astral.sh/ruff/)
   - [Black](https://black.readthedocs.io/)
   - [Bandit](https://bandit.readthedocs.io/)

2. **Run Help Commands**:
   ```bash
   poetry run ruff --help
   poetry run black --help
   poetry run bandit --help
   ```

3. **Check Configuration**:
   - Ruff: `pyproject.toml` → `[tool.ruff]`
   - Black: `pyproject.toml` → `[tool.black]`
   - Pre-commit: `.pre-commit-config.yaml`

## Make Targets Reference

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install dependencies |
| `make format` | Format code with Black and Ruff |
| `make lint` | Run linting checks |
| `make check` | Run comprehensive quality checks |
| `make test` | Run test suite |
| `make clean` | Clean temporary files |
| `make pre-commit-install` | Install pre-commit hooks |
| `make pre-commit-run` | Run pre-commit manually |
| `make qa` | Quick quality assurance (format + lint + test) |
| `make setup` | Complete development setup |

## Configuration Files

- **`.pre-commit-config.yaml`**: Pre-commit hook configuration
- **`pyproject.toml`**: Python project and tool configuration
- **`scripts/`**: Manual code quality scripts
- **`Makefile`**: Development automation commands

## Best Practices

1. **Before Committing**:
   - Run `make check` to ensure quality
   - Review changes with `git diff`
   - Test functionality locally

2. **Regular Maintenance**:
   - Update dependencies with `poetry update`
   - Update pre-commit hooks with `poetry run pre-commit autoupdate`
   - Review and update linting rules as needed

3. **Team Collaboration**:
   - Ensure all team members run `make setup`
   - Share configuration changes via version control
   - Document any tool customizations