# claude-mcp-server-gateway

A gateway that sits between Claude Desktop and your MCP servers. Instead of loading all MCP tools at startup (which eats up most of your context window), it loads them on demand.

## The problem

When you connect multiple MCP servers to Claude Desktop, they all load immediately:
- GitHub MCP: 51 tools
- Slack MCP: 20 tools  
- Google Drive MCP: 15 tools
- Filesystem MCP: 12 tools

That's 100+ tool definitions loaded before you even start talking. Each tool definition includes JSON schemas that consume tokens.

## What this does

This gateway presents itself as a single MCP server with 3 tools:
1. `list_available_mcps` - shows what MCP servers are configured
2. `load_mcp_tools` - loads tools from a specific MCP server
3. `call_mcp_tool` - actually runs the tool

MCP servers only spin up when Claude needs them.

## Setup

### Requirements
- Python 3.11+
- Claude Desktop
- The MCP servers you want to use

### Install

```bash
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install mcp python-dotenv
```

### Configure

1. Set up your API keys:
```bash
cp .env.example .env
# Edit .env with your tokens
```

2. Add to Claude Desktop config:

**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gateway": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/claude-mcp-server-gateway/dcl_wrapper.py"]
    }
  }
}
```

Restart Claude Desktop.

## How it works

1. Claude starts → sees only the gateway (3 tools)
2. You ask about GitHub → Claude calls `list_available_mcps`
3. Claude sees GitHub is available → calls `load_mcp_tools("github")`  
4. Gateway returns GitHub's tool list
5. Claude picks the right tool → calls `call_mcp_tool("github", "search_repositories", {...})`
6. Gateway spins up GitHub MCP, runs the tool, returns results

## Adding MCP servers

Edit `dcl_wrapper.py` and add to the `MCP_SERVERS` dict:

```python
MCP_SERVERS = {
    "your-server": {
        "command": "npx",
        "args": ["-y", "your-mcp-package"],
        "env": {
            "API_KEY": os.getenv("YOUR_API_KEY", "")
        },
        "description": "What it does"
    }
}
```

## Currently configured servers

- github
- slack  
- google-drive
- filesystem
- postgres
- memory
- brave-search

(Check `dcl_wrapper.py` for the full list)

## Limitations

- Adds a small delay on first tool use (server startup)
- Each MCP server connection is temporary (closes after use)
- No persistence between calls

## Files

- `dcl_wrapper.py` - The gateway server
- `.env` - Your API keys
- `requirements.txt` - Python dependencies

## License

MIT
