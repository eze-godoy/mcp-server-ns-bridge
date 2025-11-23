# Developer Tools Guide

This document explains the developer tools used in this project, what they do, and why we chose them.

## Overview

We use a modern Python development stack focused on:
- **Speed**: Fast tools that don't slow down development
- **Quality**: Catch bugs and issues early
- **Consistency**: Maintain uniform code style across the project
- **Type Safety**: Leverage Python's type hints for better code reliability

## Package Manager: uv

**What it is**: A fast, modern Python package and project manager written in Rust.

**Why we use it**:
- **Speed**: 10-100x faster than pip for package installation
- **Reliability**: Better dependency resolution than pip
- **Modern**: Built-in support for virtual environments and project management
- **Compatible**: Works with existing `pyproject.toml` and `requirements.txt`
- **Virtual Environment**: Automatically creates and manages `.venv` directory

**Common commands**:
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras

# Add a new package
uv add httpx

# Add a dev dependency
uv add --dev pytest

# Run commands in the virtual environment
uv run python script.py
uv run pytest
```

**Resources**:
- Website: https://astral.sh/uv
- Docs: https://docs.astral.sh/uv/

---

## Code Formatter: Black

**What it is**: An opinionated Python code formatter.

**Why we use it**:
- **Zero Configuration**: No debates about style, it just formats
- **Consistent**: Produces the same output every time
- **Fast**: Reformats large codebases in seconds
- **Community Standard**: Widely adopted in the Python ecosystem

**Configuration**: Set in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

**Usage**:
```bash
# Format all code
uv run black src/ tests/

# Check without modifying
uv run black --check src/ tests/

# Show what would change
uv run black --diff src/ tests/
```

**What it does**:
- Enforces consistent indentation and spacing
- Normalizes string quotes
- Formats imports and function signatures
- Wraps long lines intelligently

**Resources**:
- Website: https://black.readthedocs.io/
- Why Black?: https://black.readthedocs.io/en/stable/the_black_code_style/index.html

---

## Linter: Ruff

**What it is**: An extremely fast Python linter and code quality checker, written in Rust.

**Why we use it**:
- **Speed**: 10-100x faster than Flake8, pylint, etc.
- **Comprehensive**: Replaces multiple tools (Flake8, isort, pydocstyle, etc.)
- **Auto-fix**: Can automatically fix many issues
- **Modern**: Actively developed with frequent updates
- **Extensive Rules**: Covers 700+ rules from various linting tools

**Configuration**: Set in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "N",   # pep8-naming
    "UP",  # pyupgrade (modern Python idioms)
    "B",   # flake8-bugbear (bug detection)
    "SIM", # flake8-simplify (simplification suggestions)
    # ... and many more
]
```

**Usage**:
```bash
# Check all files
uv run ruff check src/ tests/

# Check and auto-fix
uv run ruff check --fix src/ tests/

# Watch mode (re-check on file changes)
uv run ruff check --watch src/ tests/
```

**What it catches**:
- Syntax errors and undefined names
- Unused imports and variables
- Incorrect import order
- Potential bugs (e.g., mutable default arguments)
- Code complexity issues
- Security vulnerabilities
- Non-Pythonic code patterns
- And much more!

**Resources**:
- Website: https://docs.astral.sh/ruff/
- Rules: https://docs.astral.sh/ruff/rules/

---

## Type Checker: MyPy

**What it is**: A static type checker for Python.

**Why we use it**:
- **Catch Bugs Early**: Find type-related bugs before runtime
- **Better IDE Support**: Enables better autocomplete and refactoring
- **Documentation**: Type hints serve as inline documentation
- **Gradual Typing**: Works with partially-typed codebases

**Configuration**: Set in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
# ... strict typing enabled
```

**Usage**:
```bash
# Check all files
uv run mypy src/

# Check specific file
uv run mypy src/ns_trains_mcp/server.py

# Show error codes
uv run mypy --show-error-codes src/
```

**What it does**:
```python
# MyPy catches issues like:

def get_price(price: int) -> str:
    return price  # Error: incompatible return type

def search(query: str | None) -> list[str]:
    results = query.split()  # Error: query might be None
    return results
```

**Resources**:
- Website: https://mypy-lang.org/
- Docs: https://mypy.readthedocs.io/
- Cheat Sheet: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html

---

## Testing: pytest

**What it is**: A mature, full-featured Python testing framework.

**Why we use it**:
- **Simple**: Easy to write and understand tests
- **Powerful**: Advanced features like fixtures and parametrization
- **Extensible**: Rich plugin ecosystem
- **Async Support**: Works well with async/await code

**Plugins we use**:
- **pytest-asyncio**: Test async functions
- **pytest-cov**: Code coverage reporting
- **pytest-httpx**: Mock HTTP requests for API testing

**Configuration**: Set in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"
```

**Usage**:
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_models.py

# Run tests matching a pattern
uv run pytest -k "test_station"

# Verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x
```

**Example test**:
```python
import pytest
from ns_trains_mcp.models import Station

def test_station_creation():
    station = Station(name="Utrecht Centraal", code="ut")
    assert station.name == "Utrecht Centraal"
    assert station.code == "ut"

@pytest.mark.asyncio
async def test_api_client():
    # Test async code
    result = await some_async_function()
    assert result is not None
```

**Resources**:
- Website: https://pytest.org/
- Docs: https://docs.pytest.org/

---

## Coverage: pytest-cov

**What it is**: Code coverage measurement for pytest.

**Why we use it**:
- **Visibility**: See which code is tested
- **Quality**: Identify untested code paths
- **Reports**: Generate HTML coverage reports

**Configuration**: Set in `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
```

**Usage**:
```bash
# Run tests with coverage
uv run pytest --cov

# Generate HTML report
uv run pytest --cov --cov-report=html

# View report (opens in browser)
open htmlcov/index.html
```

**What it shows**:
```
---------- coverage: platform darwin, python 3.11.0 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/ns_trains_mcp/__init__.py         2      0   100%
src/ns_trains_mcp/config.py          15      2    87%
src/ns_trains_mcp/models.py          45      0   100%
src/ns_trains_mcp/ns_api_client.py   89     12    87%
src/ns_trains_mcp/server.py         124     28    77%
-----------------------------------------------------
TOTAL                               275     42    85%
```

---

## Recommended Workflow

### Before Committing

Run this checklist before committing code:

```bash
# 1. Format code
uv run black src/ tests/

# 2. Lint and auto-fix
uv run ruff check --fix src/ tests/

# 3. Type check
uv run mypy src/

# 4. Run tests
uv run pytest --cov
```

### IDE Integration

Most IDEs support these tools:

**VS Code**:
- Install Python extension
- Install Black Formatter extension
- Install Ruff extension
- Install MyPy extension

**PyCharm**:
- Built-in support for Black, MyPy, pytest
- Configure in Settings → Tools → Python Integrated Tools

### Pre-commit Hooks (Optional)

You can automate these checks with pre-commit hooks:

```bash
# Install pre-commit
uv add --dev pre-commit

# Set up hooks
uv run pre-commit install

# Now checks run automatically on git commit
```

---

## Why This Stack?

### Performance
All our tools are either written in Rust (uv, Ruff) or highly optimized (Black, MyPy, pytest). This means:
- Linting takes seconds, not minutes
- Formatting is nearly instant
- Type checking is fast enough to run on every save

### Modern Python
These tools encourage modern Python practices:
- Type hints everywhere
- Async/await patterns
- Latest Python features (3.11+)
- Pydantic for data validation

### Industry Standard
These tools are used by major Python projects:
- FastAPI uses Ruff and MyPy
- Django uses Black
- Many companies use this exact stack

### Developer Experience
- **Fast feedback**: See issues immediately
- **Auto-fix**: Many issues fixed automatically
- **Clear errors**: Helpful error messages with suggestions
- **IDE integration**: Works seamlessly with editors

---

## Troubleshooting

### "Module not found" errors

Make sure you're running commands with `uv run`:
```bash
# Wrong
pytest

# Correct
uv run pytest
```

### Type checking errors

If MyPy complains about missing type stubs:
```bash
uv add --dev types-httpx
```

### Import errors in tests

Ensure `pythonpath = ["src"]` is set in `pyproject.toml` under `[tool.pytest.ini_options]`.

---

## Learn More

- **uv**: https://docs.astral.sh/uv/
- **Black**: https://black.readthedocs.io/
- **Ruff**: https://docs.astral.sh/ruff/
- **MyPy**: https://mypy.readthedocs.io/
- **pytest**: https://docs.pytest.org/

## Questions?

These tools have excellent documentation. If you're unsure about an error or warning, the error messages usually include links to detailed explanations.
