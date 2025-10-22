# DCL Wrapper - Dynamic Context Loading for MCP Servers

**Reduce Claude's token usage by 95% with intelligent MCP server management**

A master MCP (Model Context Protocol) server that dynamically loads other MCP servers on-demand, dramatically reducing context window consumption and improving Claude's performance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/bzsasson/dcl-wrapper.git
cd dcl-wrapper

# Install dependencies
pip install mcp python-dotenv

# Configure your environment variables
cp .env.example .env
# Edit .env with your API keys

# Add to Claude Desktop config (see Installation section)
```

## Why DCL Wrapper?

### The Problem
Loading multiple MCP servers in Claude typically means exposing 100+ tools simultaneously, consuming massive amounts of your context window before you even start your conversation.

### The Solution
DCL Wrapper exposes only **3 tools** initially:
- `list_available_mcps` - Browse available MCP servers
- `load_mcp_tools` - Load specific MCP tools on-demand  
- `call_mcp_tool` - Execute tools from any loaded MCP

This reduces initial token usage by approximately **95%**, leaving more context for your actual work.

## Features

- **Token Optimization**: Start conversations with 3 tools instead of 100+
- **On-Demand Loading**: Load MCP servers only when needed
- **Automatic Connection Management**: Handles MCP lifecycle automatically
- **Environment Variable Support**: Secure API key management with `.env`
- **Error Handling**: Comprehensive error messages and timeout management
- **Multiple MCP Support**: Works with any MCP server (Python, Node.js, etc.)
- **Zero Configuration**: Works with existing MCP server setups

## Installation

### 1. Install the DCL Wrapper

```bash
# Clone or download this repository
git clone https://github.com/bzsasson/dcl-wrapper.git
cd dcl-wrapper

# Create a virtual environment (recommended)
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install mcp python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in the dcl-wrapper directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Memory Extension Pro
GEMINI_API_KEY=your_gemini_api_key_here

# Google Search Console
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Apify Actors
APIFY_TOKEN=your_apify_token_here

# DataForSEO
DATAFORSEO_USERNAME=your_dataforseo_username_here
DATAFORSEO_PASSWORD=your_dataforseo_password_here

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
```

### 3. Add to Claude Desktop Configuration

Edit your Claude Desktop config file:
- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Replace your entire `mcpServers` section with:

```json
{
  "mcpServers": {
    "dcl-wrapper": {
      "command": "/path/to/your/.venv/bin/python",
      "args": ["/path/to/your/dcl-wrapper/dcl_wrapper.py"],
      "env": {}
    }
  }
}
```

**Important**: Update the paths to match your actual installation location.

### 4. Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

## Usage

### List Available MCPs

In Claude, simply ask:
```
"What MCP servers are available?"
```

Or:
```
"List available MCPs"
```

Claude will show you all configured MCP servers with descriptions.

### Load Tools from a Specific MCP

```
"Load tools from github"
```

Or:
```
"Show me what dataforseo can do"
```

### Use an MCP Tool

Once tools are loaded, use them naturally:
```
"Search for repositories about MCP servers"
```

Or:
```
"Get search volume data for 'python tutorial'"
```

Claude will automatically call the appropriate MCP tools.

## Configuration

### Adding New MCP Servers

Edit `dcl_wrapper.py` and add to the `MCP_SERVERS` dictionary:

```python
MCP_SERVERS = {
    # ... existing MCPs ...
    
    "your-new-mcp": {
        "command": "npx",  # or python path
        "args": ["-y", "your-package-name"],
        "env": {
            "API_KEY": os.getenv("YOUR_API_KEY", "")
        },
        "description": "What this MCP does"
    }
}
```

### Timeout Configuration

You can customize timeouts via environment variables:

```env
# Operation timeout (default: 300 seconds)
DCL_OPERATION_TIMEOUT=300

# Initialization timeout (default: 30 seconds)
DCL_INIT_TIMEOUT=30
```

## Supported MCP Servers

DCL Wrapper comes pre-configured with popular MCP servers:

- **Context7** - Current code documentation and best practices
- **Memory Extension Pro** - Advanced memory storage with semantic search
- **Google Analytics** - Analytics reporting and metrics
- **Google Search Console** - Search analytics, URL inspection, sitemaps
- **Apify Actors** - Web scraping, automation, data extraction
- **Google Workspace** - Gmail, Drive, Calendar, Docs, Sheets, Tasks
- **GitHub** - Repositories, issues, PRs, code search, workflows
- **DataForSEO** - SERP data, keywords, backlinks, domain analytics

You can easily add any MCP server by following the configuration instructions above.

## Troubleshooting

### "Missing environment variables" warning

**Solution**: Check your `.env` file contains the required API keys for the MCP servers you want to use.

### "Error connecting to [MCP]" message

**Possible causes**:
1. The MCP package is not installed
2. The path in `MCP_SERVERS` is incorrect
3. The MCP server requires authentication you haven't provided

**Solution**: Verify the MCP is installed and paths are correct in `dcl_wrapper.py`

### Still seeing 100+ tools in Claude?

**Solution**: 
1. Completely quit Claude Desktop (not just close the window)
2. Restart Claude Desktop
3. Start a **new conversation** (the wrapper only loads in new conversations)

### Tools timing out

**Solution**: Increase timeout values in your `.env` file:
```env
DCL_OPERATION_TIMEOUT=600
DCL_INIT_TIMEOUT=60
```

## How It Works

### Architecture

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │
         │ Uses only 3 tools
         ▼
┌─────────────────┐
│  DCL Wrapper    │ ← Master MCP Server
│  (3 tools)      │
└────────┬────────┘
         │
         │ Dynamically connects on-demand
         ▼
┌─────────────────────────────────────┐
│  Individual MCP Servers             │
│  ┌────────┐ ┌────────┐ ┌─────────┐ │
│  │ GitHub │ │Context7│ │DataForSEO│ │
│  └────────┘ └────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

### Token Savings Example

**Without DCL Wrapper**:
- Context7: 15 tools
- GitHub: 25 tools
- DataForSEO: 30 tools
- Google Workspace: 35 tools
- **Total: 105 tools loaded** → ~5,000-10,000 tokens used

**With DCL Wrapper**:
- DCL Wrapper: 3 tools
- **Total: 3 tools loaded** → ~200-300 tokens used
- **Savings: ~95% reduction** in initial token usage

## Technical Details

### Requirements

- Python 3.11 or higher
- `mcp` Python package
- `python-dotenv` package

### MCP Specification Compliance

DCL Wrapper follows the official Model Context Protocol specification (2025-06-18) and uses the MCP Python SDK patterns from Context7 documentation.

### Connection Management

Each MCP server connection:
1. Opens when a tool is loaded or called
2. Initializes with a 30-second timeout
3. Executes the operation with a 5-minute timeout
4. Automatically closes after operation completes

This ensures minimal resource usage and no connection leaks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/bzsasson/dcl-wrapper.git
cd dcl-wrapper

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install mcp python-dotenv

# Run tests (if available)
python -m pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io) specification
- Uses patterns from the official MCP Python SDK
- Inspired by Context7 documentation and best practices

## Keywords

MCP server, Model Context Protocol, Claude Desktop, Claude AI, token optimization, context window management, dynamic loading, MCP wrapper, AI assistant tools, Claude tools, MCP integration, Python MCP server, Claude Desktop configuration, AI productivity, token savings, context management, Claude optimization, MCP manager, master MCP, lazy loading MCP

---

**Need help?** Open an issue on GitHub or check the [Troubleshooting](#troubleshooting) section above.
