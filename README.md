# Claude MCP server gateway

A Python MCP server gateway for Claude Desktop, Claude Code, and Cline. Instead of loading all MCP tools at startup, it loads them on demand.

**Works with:** Claude Desktop (app), Claude Code (terminal), Cline (VSCode extension)

## Compatibility

| Platform | Config File | Supported |
|----------|------------|----------|
| Claude Desktop | `claude_desktop_config.json` | Yes |
| Claude Code | `.claude.json` or `.mcp.json` | Yes |
| Cline (VSCode) | `cline_mcp_settings.json` | Yes |

## The MCP server problem

When you connect multiple MCP servers to Claude:
- GitHub MCP server: 51 tools
- Slack MCP server: 20 tools  
- Google Drive MCP: 15 tools
- Filesystem MCP: 12 tools

That's 100+ MCP tool definitions loaded before you even start. Each tool's JSON schema eats up tokens.

## What this Claude MCP server gateway does

The gateway acts as a single MCP server with 3 tools:
1. `list_available_mcps` - shows configured MCP servers
2. `load_mcp_tools` - loads tools from a specific MCP server
3. `call_mcp_tool` - executes the tool

Model Context Protocol servers only start when Claude actually needs them.

## Setup

### Requirements
- Python 3.11+ (for MCP Python SDK)
- Claude Desktop, Claude Code, or Cline
- MCP servers you want to use

### Install

```bash
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install mcp python-dotenv
```

### Configure API keys

```bash
cp .env.example .env
# Edit .env with your tokens
```

## Claude Desktop MCP server configuration

Add to your Claude Desktop config:

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

## How to add MCP server to Claude Code

Claude Code MCP server setup uses a similar config with one additional field.

### User-level configuration (all projects)

Edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "gateway": {
      "type": "stdio",
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/claude-mcp-server-gateway/dcl_wrapper.py"]
    }
  }
}
```

### Project-level configuration

For project-specific MCP servers, create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "gateway": {
      "type": "stdio",
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/claude-mcp-server-gateway/dcl_wrapper.py"]
    }
  }
}
```

Claude Code will prompt for approval when using project-scoped servers.

### Alternative: Claude Code CLI

```bash
# Add the gateway using CLI
claude mcp add gateway --scope user \
  --command /path/to/.venv/bin/python \
  -- /path/to/claude-mcp-server-gateway/dcl_wrapper.py

# Verify it's added
claude mcp list
```

## Cline MCP server configuration

For Cline (VSCode extension), the MCP server gateway configuration goes in:

**Mac**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`  
**Windows**: `%APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`  
**Linux**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "gateway": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/claude-mcp-server-gateway/dcl_wrapper.py"],
      "disabled": false
    }
  }
}
```

Restart VSCode after updating.

## How it works

1. Claude starts - sees gateway (3 tools)
2. You ask about GitHub - Claude calls `list_available_mcps`
3. Claude sees GitHub available - calls `load_mcp_tools("github")`  
4. Gateway returns GitHub's tool list
5. Claude picks the right tool - calls `call_mcp_tool("github", "search_repositories", {...})`
6. Gateway spins up GitHub MCP, runs the tool, returns results

## Adding MCP servers to the gateway

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

- Small delay on first tool use (server startup)
- Each MCP server connection is temporary
- No persistence between calls

## Troubleshooting

### Gateway not appearing
- Check Python path in config points to virtual environment
- Verify `dcl_wrapper.py` path is correct
- Restart Claude Desktop/Code/VSCode completely

### MCP server connection errors
- Check API keys in `.env` file
- Verify MCP server package is installed
- Check gateway logs for errors

### Claude Code specific issues
- Make sure to include `"type": "stdio"` in config
- For project configs, approve when prompted
- Use `claude mcp list` to verify installation

## Files

- `dcl_wrapper.py` - The gateway server
- `.env` - Your API keys
- `requirements.txt` - Python dependencies

## License

MIT
