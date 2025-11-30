# MCP Server for Netherlands NS Trains

[![Docker Pulls](https://img.shields.io/docker/pulls/ezegodoy26/mcp-server-ns-bridge)](https://hub.docker.com/r/ezegodoy26/mcp-server-ns-bridge)
[![Docker Image Size](https://img.shields.io/docker/image-size/ezegodoy26/mcp-server-ns-bridge/latest)](https://hub.docker.com/r/ezegodoy26/mcp-server-ns-bridge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Add Dutch Railways (NS) train information to your AI assistant via Docker.**

This [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server enables AI assistants to search train stations, plan routes with pricing, and get real-time departure information for Netherlands Railways (NS).

Works with **any MCP-compatible client** including Claude Desktop, custom implementations, and AI agent frameworks.

## Quick Start

### Prerequisites

- Docker Desktop or Docker Engine installed
- NS API key from [NS API Portal](https://apiportal.ns.nl/) (free to register)
- An MCP-compatible client (Claude Desktop, custom client, etc.)

### Installation

**1. Pull the Docker image:**

```bash
docker pull ezegodoy26/mcp-server-ns-bridge:latest
```

**2. Configure your MCP client:**

The examples below show Claude Desktop configuration. For other MCP clients, adapt the stdio server configuration to your client's format.

**Claude Desktop:**

Edit your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "ns-bridge": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "-e",
        "NS_API_KEY",
        "ezegodoy26/mcp-server-ns-bridge:latest"
      ],
      "env": {
        "NS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> **Important**: The `-e NS_API_KEY` in the `args` array passes the environment variable into the Docker container. The `env` section sets it on the host, but Docker needs the `-e` flag to receive it.

**3. Restart your MCP client**

That's it! You can now ask your AI assistant about Dutch trains.

## What This Server Provides

### Tools

1. **search_stations** - Find train stations by name or country code
2. **search_trips** - Plan routes with connections, pricing, and travel time
3. **get_departures** - View real-time departure boards with delays and platform info

### Resources

- **station://{code}** - Get detailed station information

## Example Usage

Once configured, ask your AI assistant:

- *"What trains are departing from Utrecht Centraal in the next hour?"*
- *"Find me a train from Amsterdam to Rotterdam tomorrow at 9 AM"*
- *"What's the fastest route from Den Haag to Groningen?"*
- *"How much does a first-class ticket from Eindhoven to Maastricht cost?"*
- *"Show me stations near the German border"*

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NS_API_KEY` | **Yes** | - | Your NS API subscription key |
| `NS_API_BASE_URL` | No | `https://gateway.apiportal.ns.nl` | NS API base URL (for testing) |
| `ENVIRONMENT` | No | `production` | Set to `development` for verbose logging |

### Getting an NS API Key

1. Visit [NS API Portal](https://apiportal.ns.nl/)
2. Create a free account
3. Subscribe to these APIs:
   - Reisinformatie API (Travel Information)
   - NS-APP Stations API
4. Copy your subscription key
5. Add it to your MCP client config as shown above

## Common Station Codes

- `ut` - Utrecht Centraal
- `asd` - Amsterdam Centraal
- `rtd` - Rotterdam Centraal
- `gvc` - Den Haag Centraal
- `ehv` - Eindhoven Centraal
- `nm` - Nijmegen
- `gn` - Groningen

Use the `search_stations` tool to find more station codes.

## Updating to Latest Version

```bash
docker pull ezegodoy26/mcp-server-ns-bridge:latest
```

Then restart your MCP client.

## Docker Image Details

- **Base Image**: Python 3.13 Alpine
- **Size**: ~126MB
- **Architecture**: Multi-platform (amd64, arm64)
- **Security**: Runs as non-root user
- **Optimization**: Multi-stage build with layer caching

## Other Installation Options

Docker is the easiest way to get started. For alternative installation methods including:
- Local development with `uv`
- Traditional Python `pip` installation
- Building from source

See the [full documentation on GitHub](https://github.com/YOUR_GITHUB_USERNAME/mcp-server-ns-bridge).

## Troubleshooting

### "Cannot connect to Docker daemon"
Make sure Docker Desktop is running.

### "No response from MCP server"
- Verify the `-i` flag is in your MCP client config args
- Check that your NS_API_KEY is valid
- Restart your MCP client after configuration changes

### "API authentication failed"
- Get a fresh API key from [NS API Portal](https://apiportal.ns.nl/)
- Ensure there are no extra spaces in your API key
- Verify you've subscribed to both required APIs

For more help, see the [troubleshooting guide](https://github.com/YOUR_GITHUB_USERNAME/mcp-server-ns-bridge/blob/main/DOCKER.md#troubleshooting).

## Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/YOUR_GITHUB_USERNAME/mcp-server-ns-bridge/issues)
- **Full Documentation**: [GitHub Repository](https://github.com/YOUR_GITHUB_USERNAME/mcp-server-ns-bridge)
- **License**: MIT

## About MCP

This server implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), an open standard for connecting AI assistants to external data sources and tools.

---

Made with ❤️ for the Dutch railway community | [NS API](https://apiportal.ns.nl/)
