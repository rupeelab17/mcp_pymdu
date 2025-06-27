# MCP Server for PyMDU

A Model Control Protocol server that allows Claude Desktop to communicate with PyMDU.

![Démonstration en action](gemini.gif)

## Setup

1. Clone the repository
2. Install environment `micromamba env create -f environment.yml`
3. Activate environment `micromamba activate mcp_pymdu`
4. Install poetry `pip install poetry`
5. Install dependencies: `poetry install`

### Using with Claude Desktop

Edit the `claude_desktop_config.json` file with the following content, change path-to-mcp-server to the path of this repo:

```json
{
  "mcpServers": {
    "pymdu": {
      "command": "path-to-python-bin",
      "args": [
        "-m",
        "mcp_pymdu.server"
      ],
      "env": {
        "PYTHONPATH": "path-to-mcp-server"
      }
    }
  }
}
```

### Using with Gemini Cli

Edit the `~/.gemini/settings.json` file with the following content, change path-to-mcp-server to the path of this repo:

```json
{
  "theme": "Dracula",
  "selectedAuthType": "oauth-personal",
  "preferredEditor": "vim",
  "mcpServers": {
    "pymdu": {
      "command": "path-to-python-bin",
      "args": [
        "-m",
        "mcp_pymdu.server"
      ],
      "env": {
        "PYTHONPATH": "path-to-mcp-server"
      }
    }
  }
}
```

