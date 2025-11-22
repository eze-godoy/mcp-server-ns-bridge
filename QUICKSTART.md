# Quick Start Guide

Get your NS Trains MCP server up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- NS API key ([Get one here](https://apiportal.ns.nl/))
- Terminal/Command line

## Installation (5 steps)

### 1. Install `uv` (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use Homebrew on macOS
brew install uv
```

### 2. Clone and navigate to the project

```bash
cd mcp-server-ns-trains
```

### 3. Install dependencies

```bash
# Add uv to PATH (if just installed)
export PATH="$HOME/.local/bin:$PATH"

# Install all dependencies
uv sync --all-extras
```

### 4. Set up your API key

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file and add your NS API key
# NS_API_KEY=your_actual_api_key_here
```

On macOS/Linux, you can use:
```bash
echo "NS_API_KEY=your_actual_api_key_here" > .env
```

### 5. Test the installation

```bash
uv run pytest
```

You should see: `11 passed`

## Usage

### Option A: Test with MCP Inspector (Recommended for first-time)

```bash
uv run mcp dev src/ns_trains_mcp/server.py
```

This opens an interactive inspector where you can test the MCP tools.

### Option B: Install in Claude Desktop

```bash
uv run mcp install src/ns_trains_mcp/server.py
```

This automatically configures Claude Desktop to use your server.

### Option C: Manual Claude Desktop Configuration

1. Open Claude Desktop config:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add this configuration (replace the path with your actual project path):

```json
{
  "mcpServers": {
    "ns-trains": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-server-ns-trains",
        "run",
        "src/ns_trains_mcp/server.py"
      ],
      "env": {
        "NS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Example Queries

Once configured with Claude Desktop, try these queries:

### Find Stations
```
Find train stations in Amsterdam
```

### Plan a Trip
```
I need to travel from Utrecht to Amsterdam tomorrow at 9 AM.
Show me the train options with prices.
```

### Check Departures
```
What trains are departing from Rotterdam Centraal in the next hour?
```

### Compare Routes
```
What's the fastest way to get from Den Haag to Groningen?
How much would a first-class ticket cost?
```

## Common Station Codes

Here are some frequently used station codes:

- `ut` - Utrecht Centraal
- `asd` - Amsterdam Centraal
- `rtd` - Rotterdam Centraal
- `gvc` - Den Haag Centraal
- `ehv` - Eindhoven Centraal
- `nm` - Nijmegen
- `gn` - Groningen
- `ams` - Amsterdam Sloterdijk
- `ledn` - Leiden Centraal
- `zl` - Zwolle

Use `search_stations` to find codes for other stations!

## Troubleshooting

### "Module not found" error
Make sure you're using `uv run` before commands:
```bash
uv run pytest  # ✓ Correct
pytest         # ✗ Wrong
```

### API key not working
1. Verify you registered at [NS API Portal](https://apiportal.ns.nl/)
2. Check you subscribed to the required APIs:
   - Reisinformatie API
   - NS-APP Stations API
3. Ensure your `.env` file exists and contains the key
4. Restart your terminal/Claude Desktop after adding the key

### Claude Desktop doesn't see the server
1. Check the path in `claude_desktop_config.json` is absolute
2. Verify `uv` is installed and accessible
3. Check Claude Desktop logs for errors
4. Restart Claude Desktop completely

### Permission denied
```bash
chmod +x src/ns_trains_mcp/server.py
```

## Development Workflow

If you want to modify or extend the server:

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check --fix src/ tests/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Type check
uv run mypy src/
```

See [DEVELOPER_TOOLS.md](DEVELOPER_TOOLS.md) for detailed information about development tools.

## Next Steps

1. Read the [README.md](README.md) for complete documentation
2. Check [DEVELOPER_TOOLS.md](DEVELOPER_TOOLS.md) to understand the development stack
3. Explore the NS API specs in `.ns-apis/` directory
4. Consider adding new features (disruptions, facilities, etc.)

## Getting Help

- Check the [README](README.md) for detailed documentation
- Review error messages - they usually include helpful hints
- NS API Documentation: https://apiportal.ns.nl/
- MCP Documentation: https://modelcontextprotocol.io/

## What's Next?

This is a basic implementation with:
- ✓ Station search
- ✓ Trip planning
- ✓ Pricing information
- ✓ Real-time departures

**Future ideas**:
- Add disruptions and maintenance notifications
- Include station facilities (parking, bike storage, etc.)
- Support for international routes
- Journey crowdedness predictions
- Historical delay statistics

Happy travels! 🚂
