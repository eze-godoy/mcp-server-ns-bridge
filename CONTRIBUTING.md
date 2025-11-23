# Contributing to MCP Server for Netherlands NS Trains

Thank you for your interest in contributing! This document provides guidelines and standards for contributing to this project.

## Code of Conduct

This project aims to be welcoming and inclusive. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/))
- NS API key from [NS API Portal](https://apiportal.ns.nl/)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-server-ns-trains
   ```

2. **Install dependencies**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   uv sync --all-extras
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Add your NS API key to .env
   ```

4. **Verify installation**
   ```bash
   uv run pytest
   ```

## Development Workflow

### 1. Create a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features (e.g., `feature/add-disruptions-api`)
- `fix/` - Bug fixes (e.g., `fix/station-search-crash`)
- `docs/` - Documentation updates (e.g., `docs/update-quickstart`)
- `test/` - Test additions/improvements (e.g., `test/api-client-coverage`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-error-handling`)

### 2. Make Your Changes

Follow the project's coding standards and best practices.

### 3. Write Tests

All new code should include tests:
- Unit tests for individual functions
- Integration tests for API interactions (with mocking)
- Maintain or improve overall test coverage

### 4. Run Quality Checks

Before committing, ensure all checks pass:

```bash
# Format code
uv run black src/ tests/

# Lint and auto-fix
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/

# Run tests with coverage
uv run pytest --cov
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add disruptions API support

- Implement get_disruptions MCP tool
- Add Pydantic models for disruption data
- Include tests with 100% coverage
- Update README with examples
```

Commit message format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (bullet points)
- Reference related issues

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub/GitLab using the PR template.

## Code Standards

### Python Style

This project follows modern Python best practices:

- **PEP 8** compliant (enforced by Ruff)
- **Black** formatting (line length: 100)
- **Type hints** required for all function signatures
- **Docstrings** for all public functions and classes

### Type Hints

```python
# Good
def search_stations(
    query: str,
    country_code: str | None = None
) -> list[Station]:
    """Search for train stations."""
    ...

# Bad - missing type hints
def search_stations(query, country_code=None):
    ...
```

### Error Handling

- Use specific exception types
- Provide clear error messages
- Log errors appropriately
- Never expose sensitive information in errors

```python
# Good
if not station_code:
    raise ValueError("station_code is required and cannot be empty")

# Bad
if not station_code:
    raise Exception("error")
```

### Async/Await

- Use `async`/`await` for I/O operations
- Properly handle async context managers
- Don't mix sync and async unnecessarily

### Pydantic Models

- Use Pydantic for all data structures
- Include field descriptions
- Set appropriate validators
- Use proper type annotations

```python
class Station(BaseModel):
    """Represents a train station."""

    code: str = Field(..., description="Station code (e.g., 'ut' for Utrecht)")
    name: str = Field(..., description="Full station name")
    country: str = Field(default="NL", description="ISO country code")
```

## Testing Guidelines

### Test Structure

```python
import pytest
from ns_trains_mcp.models import Station

def test_station_creation():
    """Test creating a station with required fields."""
    station = Station(code="ut", name="Utrecht Centraal")

    assert station.code == "ut"
    assert station.name == "Utrecht Centraal"
    assert station.country == "NL"  # Default value

@pytest.mark.asyncio
async def test_api_client_search(httpx_mock):
    """Test API client station search with mocked response."""
    httpx_mock.add_response(
        url="https://gateway.apiportal.ns.nl/nsapp-stations/v2",
        json={"payload": [{"code": "ut", "name": "Utrecht Centraal"}]}
    )

    result = await client.search_stations("Utrecht")
    assert len(result) == 1
```

### Coverage Requirements

- Aim for 80%+ overall coverage
- 100% coverage for models and utilities
- All error paths should be tested
- Edge cases must be covered

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov

# Specific test file
uv run pytest tests/test_models.py

# Specific test
uv run pytest tests/test_models.py::test_station_creation

# Verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x
```

## Documentation

### Code Documentation

- All public functions need docstrings
- Include parameter descriptions
- Specify return types
- Add usage examples for complex functions

```python
async def search_trips(
    origin: str,
    destination: str,
    date_time: datetime | None = None,
    search_for_arrival: bool = False
) -> TripSearchResponse:
    """
    Search for train trips between two stations.

    Args:
        origin: Origin station code (e.g., 'ut' for Utrecht)
        destination: Destination station code
        date_time: Departure or arrival time (defaults to now)
        search_for_arrival: If True, date_time is arrival time

    Returns:
        TripSearchResponse containing available trips with pricing

    Raises:
        ValueError: If origin or destination is invalid
        NSAPIError: If the NS API returns an error

    Example:
        >>> result = await search_trips("ut", "asd")
        >>> print(f"Found {len(result.trips)} trips")
    """
    ...
```

### README Updates

When adding new features, update:
- Feature list
- Example queries
- API documentation section

## Pull Request Process

1. **Fill out the PR template completely**
2. **Ensure all checks pass** (tests, linting, type checking)
3. **Request review** from maintainers
4. **Address review feedback** promptly
5. **Squash commits** if requested before merging

### PR Review Criteria

Your PR will be reviewed for:
- **Code quality**: Follows style guide, well-structured
- **Tests**: Adequate coverage, tests pass
- **Documentation**: Clear and complete
- **Functionality**: Works as intended, no regressions
- **Performance**: No unnecessary performance degradation
- **Security**: No vulnerabilities introduced

## Project Structure

Understanding the codebase structure:

```
src/ns_trains_mcp/
├── __init__.py          # Package metadata
├── config.py            # Settings management
├── models.py            # Pydantic data models
├── ns_api_client.py     # NS API wrapper
└── server.py            # MCP server (main entry)

tests/
├── __init__.py
├── test_config.py       # Configuration tests
└── test_models.py       # Model tests
```

## Common Tasks

### Adding a New MCP Tool

1. Add tool handler in `server.py`
2. Add API client method in `ns_api_client.py`
3. Create Pydantic models in `models.py`
4. Write comprehensive tests
5. Update README with examples

### Adding a New Dependency

```bash
# Runtime dependency
uv add package-name

# Development dependency
uv add --dev package-name
```

Always:
- Justify why the dependency is needed
- Check the package is maintained and secure
- Update documentation if needed

## Questions or Issues?

- **Bug reports**: Open an issue with detailed reproduction steps
- **Feature requests**: Open an issue describing the use case
- **Questions**: Check existing issues or documentation first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to this project!
