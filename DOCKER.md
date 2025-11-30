# Docker Usage Guide

This guide covers running the NS Bridge MCP server using Docker.

## Table of Contents

- [Quick Start](#quick-start)
- [Using Pre-built Images](#using-pre-built-images)
- [Building Locally](#building-locally)
- [Configuration](#configuration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Quick Start

### Prerequisites

- Docker Desktop or Docker Engine installed
- NS API subscription key (get one at [apiportal.ns.nl](https://apiportal.ns.nl))

### Using with MCP Clients

1. **Pull the Docker image:**
   ```bash
   docker pull <dockerhub-username>/mcp-server-ns-bridge:latest
   ```

2. **Configure your MCP client:**

   **Example: Claude Desktop**

   Edit your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

   Add the following configuration:
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
           "<dockerhub-username>/mcp-server-ns-bridge:latest"
         ],
         "env": {
           "NS_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

   > **Note**: The `-e NS_API_KEY` flag in the `args` array passes the environment variable into Docker. The `env` section sets it on the host.

   **Other MCP Clients:**

   For other MCP-compatible clients, configure a stdio server that runs:
   ```bash
   docker run -i --rm --init -e NS_API_KEY=your_key <dockerhub-username>/mcp-server-ns-bridge:latest
   ```

3. **Restart your MCP client** to load the server.

4. **Verify** by asking your AI assistant: "What train departures are there from Amsterdam Centraal?"

## Using Pre-built Images

### Available Tags

- `latest` - Latest stable release from the main branch
- `v1.0.0`, `v1.0`, `v1` - Semantic version tags
- `main-<sha>` - Specific commits from main branch

### Pull a Specific Version

```bash
# Latest stable
docker pull <dockerhub-username>/mcp-server-ns-bridge:latest

# Specific version
docker pull <dockerhub-username>/mcp-server-ns-bridge:v1.0.0

# Specific commit
docker pull <dockerhub-username>/mcp-server-ns-bridge:main-abc1234
```

### Manual Testing

Test the Docker image manually with stdio input:

```bash
# Interactive mode
docker run -i --rm \
  -e NS_API_KEY=your_api_key_here \
  <dockerhub-username>/mcp-server-ns-bridge:latest
```

Then send a JSON-RPC request via stdin:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}
```

## Building Locally

### Build for Your Platform

```bash
# Build for local testing
docker build -t mcp-server-ns-bridge:local .

# Run the local build
docker run -i --rm \
  -e NS_API_KEY=your_api_key_here \
  mcp-server-ns-bridge:local
```

### Multi-Platform Build

Build for both AMD64 and ARM64 (Apple Silicon):

```bash
# Create a new builder instance
docker buildx create --name multiplatform --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t mcp-server-ns-bridge:multiplatform \
  --load \
  .
```

### Build with Docker Compose

```bash
# Build using docker-compose
docker-compose build

# Run with docker-compose (requires .env file)
docker-compose run --rm ns-bridge
```

## Configuration

### Environment Variables

The Docker image supports the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NS_API_KEY` | Yes | - | NS API subscription key |
| `NS_API_BASE_URL` | No | `https://gateway.apiportal.ns.nl` | NS API base URL |
| `ENVIRONMENT` | No | `production` | Set to `development` for verbose logging |

### Passing Environment Variables

**Via MCP client config (example: Claude Desktop):**
```json
{
  "mcpServers": {
    "ns-bridge": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--init",
        "-e", "NS_API_KEY",
        "-e", "ENVIRONMENT",
        "image:tag"
      ],
      "env": {
        "NS_API_KEY": "your_key",
        "ENVIRONMENT": "development"
      }
    }
  }
}
```

> **Important**: Each environment variable needs its own `-e` flag in the `args` array to be passed into the Docker container.

**Via command line:**
```bash
docker run -i --rm \
  -e NS_API_KEY=your_key \
  -e ENVIRONMENT=development \
  mcp-server-ns-bridge:latest
```

**Via .env file:**
```bash
# Create .env file
cat > .env << EOF
NS_API_KEY=your_api_key_here
ENVIRONMENT=production
EOF

# Run with env file
docker run -i --rm --env-file .env mcp-server-ns-bridge:latest
```

## Development Workflow

### Iterative Development

For rapid development, use the native Python workflow instead of Docker:

```bash
# Faster for development
uv run mcp dev src/ns_bridge/server.py
```

### Testing Docker Changes

When modifying the Dockerfile:

```bash
# 1. Make changes to Dockerfile
# 2. Rebuild
docker build -t mcp-server-ns-bridge:dev .

# 3. Test the build
docker run -i --rm -e NS_API_KEY=test mcp-server-ns-bridge:dev

# 4. Check image size
docker images mcp-server-ns-bridge:dev
```

### Debugging

Run with verbose logging:

```bash
docker run -i --rm \
  -e NS_API_KEY=your_key \
  -e ENVIRONMENT=development \
  mcp-server-ns-bridge:local
```

Access the container shell:

```bash
docker run -it --rm \
  --entrypoint /bin/sh \
  mcp-server-ns-bridge:local
```

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to Docker daemon"

**Problem**: Docker is not running.

**Solution**:
- macOS/Windows: Start Docker Desktop
- Linux: `sudo systemctl start docker`

#### 2. "Failed to pull image"

**Problem**: Image not found or network issues.

**Solution**:
```bash
# Check if image exists
docker search <dockerhub-username>/mcp-server-ns-bridge

# Try pulling with full path
docker pull docker.io/<dockerhub-username>/mcp-server-ns-bridge:latest
```

#### 3. "No response from MCP server"

**Problem**: Missing `-i` flag or incorrect command.

**Solution**: Ensure your MCP client config includes `-i` flag:
```json
"args": ["run", "-i", "--rm", "--init", "image:tag"]
```

#### 4. "API authentication failed"

**Problem**: Invalid or missing `NS_API_KEY`.

**Solution**:
- Verify your API key at [apiportal.ns.nl](https://apiportal.ns.nl)
- Check the `env` section in your MCP client config
- Ensure no extra spaces or quotes in the key

#### 5. "Platform mismatch warnings"

**Problem**: Running amd64 image on arm64 (or vice versa).

**Solution**: Pull the multi-platform image, Docker will select the correct architecture automatically:
```bash
docker pull --platform linux/arm64 <dockerhub-username>/mcp-server-ns-bridge:latest
```

### Debugging Commands

```bash
# Check running containers
docker ps

# View container logs (if using docker-compose)
docker-compose logs

# Inspect image details
docker inspect <dockerhub-username>/mcp-server-ns-bridge:latest

# Check image layers and size
docker history <dockerhub-username>/mcp-server-ns-bridge:latest

# Clean up stopped containers
docker container prune

# Clean up unused images
docker image prune -a
```

## Advanced Usage

### Custom Network Configuration

If you need to connect to a custom NS API endpoint:

```bash
docker run -i --rm \
  -e NS_API_KEY=your_key \
  -e NS_API_BASE_URL=https://custom-api.example.com \
  mcp-server-ns-bridge:latest
```

### Resource Limits

Limit CPU and memory usage:

```bash
docker run -i --rm \
  --memory 512m \
  --cpus 1 \
  -e NS_API_KEY=your_key \
  mcp-server-ns-bridge:latest
```

For MCP clients that support Docker args (e.g., Claude Desktop):
```json
{
  "mcpServers": {
    "ns-bridge": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--init",
        "--memory", "512m",
        "--cpus", "1",
        "-e", "NS_API_KEY",
        "image:tag"
      ],
      "env": {
        "NS_API_KEY": "your_key"
      }
    }
  }
}
```

### Health Checks

The Docker image does not include HTTP health checks since MCP uses stdio transport. To verify the container is working:

```bash
# Send a test initialize request
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
  docker run -i --rm -e NS_API_KEY=test mcp-server-ns-bridge:latest
```

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use Docker secrets** for production deployments
3. **Run as non-root** (already configured in the image)
4. **Keep images updated** to get security patches
5. **Limit container resources** to prevent resource exhaustion

### CI/CD Integration

The repository includes automated Docker builds via GitHub Actions. On every push to `main` or version tag:

1. Tests run to ensure code quality
2. Multi-platform Docker image builds (amd64 + arm64)
3. Image pushes to Docker Hub with appropriate tags
4. README syncs to Docker Hub description

To trigger a release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/mcp-server-ns-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/mcp-server-ns-bridge/discussions)
- **Docker Hub**: [Docker Hub Repository](https://hub.docker.com/r/<dockerhub-username>/mcp-server-ns-bridge)
