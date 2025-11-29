# MCP Server for Netherlands NS Trains

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://github.com/pytest-dev/pytest)

A Model Context Protocol (MCP) server that enables LLMs to interact with the Netherlands Railways (NS) API for route planning, pricing, and real-time departure information.

## Features

### MCP Tools

1. **search_stations** - Find train stations by name or country
   - Search by station name
   - Filter by country code
   - Returns station codes needed for trip planning

2. **search_trips** - Plan routes between stations
   - Get multiple trip options with connections
   - View detailed leg-by-leg journey information
   - See pricing with discount options
   - Choose travel class (1st or 2nd)
   - Search by departure or arrival time

3. **get_departures** - View real-time departure boards
   - See upcoming departures from any station
   - Track delays and cancellations
   - Monitor platform changes

### MCP Resources

- `station://{code}` - Get detailed information about a specific station

## Installation

### Prerequisites

- Python 3.11 or higher
- NS API key from [NS API Portal](https://apiportal.ns.nl/)
- `uv` package manager (recommended) or `pip`

### Setup with uv (Recommended)

```bash
# Clone the repository
cd mcp-server-ns-bridge

# Install dependencies
uv sync --all-extras

# Copy environment template
cp .env.example .env

# Edit .env and add your NS API key
# NS_API_KEY=your_actual_api_key_here
```

### Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env and add your NS API key
```

### Getting an NS API Key

1. Go to [NS API Portal](https://apiportal.ns.nl/)
2. Create an account
3. Subscribe to the following APIs:
   - Reisinformatie API (Travel Information)
   - NS-APP Stations API
4. Copy your subscription key
5. Add it to your `.env` file as `NS_API_KEY`

## Usage

### Running the MCP Server

#### Development Mode (with Inspector)

```bash
export PATH="$HOME/.local/bin:$PATH"
uv run mcp dev src/ns_bridge/server.py
```

This opens the MCP Inspector for interactive testing.

#### Installing in Claude Desktop

```bash
uv run mcp install src/ns_bridge/server.py
```

This will configure Claude Desktop to use your MCP server.

#### Manual Configuration

Add to your Claude Desktop config file (location varies by OS):

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ns-bridge": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-server-ns-bridge",
        "run",
        "src/ns_bridge/server.py"
      ],
      "env": {
        "NS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Example Queries for LLMs

Once configured, you can ask Claude (or other MCP-compatible LLMs):

- "What trains are departing from Utrecht Centraal in the next hour?"
- "Find me a train from Amsterdam to Rotterdam tomorrow at 9 AM"
- "What's the fastest route from Den Haag to Groningen?"
- "How much does a first-class ticket from Eindhoven to Maastricht cost?"
- "Show me stations near the German border"

## Development

### Project Structure

```
mcp-server-ns-bridge/
├── src/
│   └── ns_bridge/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server implementation
│       ├── ns_api_client.py     # NS API wrapper
│       ├── models.py            # Data models (Pydantic)
│       └── config.py            # Configuration management
├── tests/                       # Test suite
├── pyproject.toml               # Project configuration & dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

### Developer Tools

This project uses modern Python development tools for code quality:

#### Code Formatting & Linting

- **Black**: Code formatter for consistent style
- **Ruff**: Fast, modern linter and code checker
- **MyPy**: Static type checker

Run all checks:

```bash
# Format code
uv run black src/ tests/

# Lint and auto-fix
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/
```

See [DEVELOPER_TOOLS.md](DEVELOPER_TOOLS.md) for detailed documentation on each tool and why we use them.

#### Testing

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage
- **pytest-httpx**: HTTP mocking for API tests

Run tests:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v
```

### Virtual Environment Note

Yes, `uv` is compatible with virtual environments! `uv` automatically creates and manages a `.venv` directory in your project. You can activate it manually if needed:

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

However, `uv run` automatically uses the virtual environment, so activation is optional for most tasks.

## API Documentation

### NS API Endpoints Used

1. **Stations API** (`/nsapp-stations/v2`)
   - Search and list train stations
   - Filter by country

2. **Trips API** (`/reisinformatie-api/api/v3/trips`)
   - Route planning with connections
   - Pricing information
   - Support for via stations

3. **Departures API** (`/reisinformatie-api/api/v2/departures`)
   - Real-time departure information
   - Delay and cancellation tracking

### Station Codes

Common station codes:
- `ut` - Utrecht Centraal
- `asd` - Amsterdam Centraal
- `rtd` - Rotterdam Centraal
- `gvc` - Den Haag Centraal
- `ehv` - Eindhoven Centraal
- `nm` - Nijmegen
- `gn` - Groningen

Use the `search_stations` tool to find more station codes.

## Contributing

Suggestions and improvements are welcome!

### Development Workflow

1. Create a feature branch
2. Make your changes
3. Run the test suite: `uv run pytest`
4. Run linting: `uv run ruff check --fix src/ tests/`
5. Run type checking: `uv run mypy src/`
6. Format code: `uv run black src/ tests/`
7. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic's MCP specification
- [NS API](https://apiportal.ns.nl/) - Netherlands Railways API
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python MCP SDK

## Roadmap

Future enhancements planned:
- [ ] Add support for disruptions API
- [ ] Include station facilities information
- [ ] Add journey details (crowdedness predictions)
- [ ] Support for international routes
- [ ] Caching for frequently accessed data
- [ ] Rate limiting to respect API quotas
