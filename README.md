# MCP Server for PyMDU

A Model Control Protocol server that allows Claude Desktop to communicate with PyMDU.

[![smithery badge](https://smithery.ai/badge/@rupeelab17/mcp_pymdu)](https://smithery.ai/server/@rupeelab17/mcp_pymdu)

## Setup

1. Clone the repository
2. Install environment `micromamba env create -f environment.yml`
3. Activate environment `micromamba activate mcp_pymdu`
4. Install poetry `pip install poetry`
5. Install dependencies: `poetry install`

### Using with [Claude Desktop](https://claude.ai/download)

![Démonstration en action](claude.gif)

Edit the `claude_desktop_config.json` file with the following content, change path-to-mcp-server to the path of this repo:

```json
{
  "mcpServers": {
    "pymdu": {
      "command": "path-to-python-bin/fastmcp",
      "args": [
        "run",
        "path-to-mcp-server/mcp_pymdu/server.py",
		"--transport",
		"stdio"
      ],
      "env": {
        "PYTHONPATH": "path-to-mcp-server",
        
      }
    }
  }
}
```

### Using with [Gemini Cli](https://github.com/google-gemini/gemini-cli)

![Démonstration en action](gemini.gif)

Edit the `~/.gemini/settings.json` file with the following content, change path-to-mcp-server to the path of this repo:

```json
{
  "theme": "Dracula",
  "selectedAuthType": "oauth-personal",
  "preferredEditor": "vim",
  "mcpServers": {
    "pymdu": {
      "command": "path-to-python-bin/fastmcp",
      "args": [
        "run",
        "path-to-mcp-server/mcp_pymdu/server.py",
		"--transport",
		"stdio"
      ],
      "env": {
        "PYTHONPATH": "path-to-mcp-server"
      }
    }
  }
}
```
# ⚡️ mcpo

Expose any MCP tool as an OpenAPI-compatible HTTP server—instantly.

mcpo is a dead-simple proxy that takes an MCP server command and makes it accessible via standard RESTful OpenAPI, so your tools "just work" with LLM agents and apps expecting OpenAPI servers.

No custom protocol. No glue code. No hassle.

## 🚀 Quick Usage

We recommend using uv for lightning-fast startup and zero config.

```bash
uvx mcpo --port 8000 --api-key "top-secret" -- fastmcp run mcp_pymdu/server.py
```

Or, if you’re using Python:

```bash
pip install mcpo
mcpo --port 8000 --api-key "top-secret" -- fastmcp run mcp_pymdu/server.py
```