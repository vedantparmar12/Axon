# MCP Crawl4AI with Docker & Ollama Setup Guide

## Overview
This setup runs your MCP server with local Ollama models in Docker containers, solving embedding initialization issues and providing a scalable architecture.

## Architecture
- **Ollama Container**: Hosts local LLM (Mistral) and embedding models (nomic-embed-text)
- **MCP Server Container**: Runs the Crawl4AI server with hiRAG capabilities
- **Docker Network**: Secure communication between containers
- **MCP Gateway**: Integration with Claude Desktop

## Prerequisites
1. Docker and Docker Compose installed
2. At least 8GB RAM available for containers
3. Claude Desktop with MCP support

## Quick Start

### 1. Build and Start Services
```bash
cd C:\Users\vedan\Desktop\mcp-rag\mcp-crawl4ai-rag

# Build the MCP server image
docker build -t mcp-crawl4ai:latest .

# Start all services (Ollama + MCP server)
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Verify Models (Optional)
Your models are already downloaded and ready:
```bash
# Optional: Check that your models are available
docker exec ollama ollama list

# Should show:
# ai/embeddinggemma
# ai/smollm3
```

### 3. Configure Claude Desktop
Copy the Docker configuration from `claude_desktop_config_example.json` to your Claude Desktop config:

```json
{
  "mcpServers": {
    "crawl4ai-research-agent": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "mcp-crawl4ai-rag_mcp-network",
        "--add-host", "host.docker.internal:host-gateway",
        "mcp-crawl4ai:latest"
      ],
      "env": {
        "DOCKER_SOCKET": "/var/run/docker.sock"
      }
    }
  }
}
```

### 4. Restart Claude Desktop
After updating the config, restart Claude Desktop to load the new MCP server.

## Available Models (Your Existing Models)
- **Embedding**: `ai/embeddinggemma` (Already pulled)
- **LLM**: `ai/smollm3` (Already pulled)

## Container Services

### Ollama Service
- **URL**: http://localhost:11434
- **Models**: Auto-downloaded on first run
- **Persistent**: Model data stored in Docker volume

### MCP Server
- **Port**: 8080 (internal)
- **Network**: Connected to Ollama via Docker network
- **Features**: Full hiRAG + Research Agent capabilities

## Troubleshooting

### Check Service Health
```bash
# All services status
docker-compose ps

# Ollama health
curl http://localhost:11434/api/version

# MCP server logs
docker-compose logs mcp-crawl4ai
```

### Common Issues

1. **Models not downloading**: Check internet connection and Docker logs
2. **Memory issues**: Ensure at least 8GB RAM available
3. **Network errors**: Verify Docker network configuration

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (will re-download models)
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d
```

## Resource Usage
- **Ollama**: ~2GB RAM (with embeddinggemma + smollm3 loaded)
- **MCP Server**: ~1GB RAM
- **Disk**: Your existing models + ~1GB for containers and data

## Benefits of This Setup
1. **Instant Startup**: Models already downloaded, immediate availability
2. **Isolation**: Containers provide security and easy management
3. **Scalability**: Easy to add more models or scale services
4. **Reproducibility**: Consistent environment across machines
5. **Resource Management**: Proper limits and health checks
6. **Efficiency**: Uses your existing model downloads

## Next Steps
Once running, you can:
- Test web crawling with `crawl_url` tool
- Set up monitoring with `setup_monitoring`
- Use advanced search with `advanced_search`
- Access hiRAG capabilities for enhanced retrieval