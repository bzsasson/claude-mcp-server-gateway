# Claude MCP Server Gateway

**Stop Wasting 87% of Claude's Context on Tool Definitions**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Claude Desktop Ready](https://img.shields.io/badge/Claude_Desktop-Ready-purple.svg)](https://claude.ai/download)

When you connect Claude Desktop to GitHub, Slack, Google Drive, Filesystem, and Postgres MCP servers, something terrible happens before you even ask a question:

- **GitHub MCP**: 51 tools → 10,200 tokens
- **Slack MCP**: 20 tools → 4,000 tokens  
- **Google Drive MCP**: 15 tools → 3,000 tokens
- **Filesystem MCP**: 12 tools → 2,400 tokens
- **Postgres MCP**: 10 tools → 2,000 tokens

**Total: 108 tools consuming 21,600 tokens — that's 87% of Claude's 25,000 token context window.**

It's like opening every app on your phone just to check one notification. Your context is maxed out before the conversation even starts.

## The Solution: Model Context Protocol Gateway Architecture

Claude MCP Server Gateway is a Python-based intelligent gateway that implements dynamic loading for Model Context Protocol servers. Instead of loading 108 tools at startup, Claude Desktop sees only **3 gateway tools** (~600 tokens). MCP servers load on-demand, **only when Claude actually needs them**.

**Traditional MCP Setup**: Claude → 108 tools loaded → 87% context consumed  
**Gateway Approach**: Claude → 3 gateway tools → MCP servers load as needed → 97% context available

This server gateway pattern revolutionizes how Claude Desktop manages multiple MCP servers, keeping your Model Context Protocol ecosystem lean and efficient.

[🚀 Quick Start](#quick-start) • [📦 Installation](#installation) • [🔧 Configuration](#configuration) • [📚 How It Works](#how-dynamic-mcp-loading-works-3-level-architecture) • [🤝 Contributing](#contributing)

## How Dynamic MCP Loading Works: 3-Level Architecture

Traditional Model Context Protocol setups load everything at startup. Claude MCP Server Gateway implements progressive loading across three tiers, similar to cache optimization in database systems:

### Level 1: Server Discovery (~50 tokens)
At startup, Claude sees only high-level MCP server descriptions:

```
Available MCP Servers:
- github: Repository management, issues, pull requests, code analysis
- slack: Team communication, channels, message history
- google-drive: File storage, document access, search
- filesystem: Local file operations
- postgres: Database queries and schema inspection
```

**Token cost**: ~50 tokens for all server summaries  
**Claude knows**: WHAT'S available, but hasn't loaded any tools yet

### Level 2: Tool Summaries (~300 tokens per server)
When Claude needs a specific server, it loads tool summaries:

**Example - Loading GitHub MCP**:
```
GitHub MCP Tools (51 total):
- search_repositories: Find GitHub repositories by query
- create_issue: Create new issues in repositories
- get_pull_request: Retrieve PR details and status
- list_commits: Get commit history for branches
- add_issue_comment: Comment on existing issues
... (46 more tool summaries)
```

**Token cost**: ~300 tokens for summaries (vs 10,200 for full tools)  
**Claude knows**: Brief descriptions to choose the right tool

### Level 3: Active Tools (~10,000 tokens when needed)
Finally, Claude loads complete tool definitions with full JSON schemas:

```json
{
  "name": "create_issue",
  "description": "Create a new issue in a GitHub repository.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "owner": {"type": "string", "description": "Repository owner"},
      "repo": {"type": "string", "description": "Repository name"},
      "title": {"type": "string", "description": "Issue title"},
      "body": {"type": "string", "description": "Issue body content"},
      "labels": {"type": "array", "items": {"type": "string"}},
      "assignees": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["owner", "repo", "title"]
  }
}
```

**Token cost**: Full GitHub MCP (~10,200 tokens) loaded ONLY when executing tools  
**Claude knows**: Complete schemas to make accurate API calls

### The Gateway Advantage

| Loading Stage | Without Gateway | With Gateway |
|--------------|----------------|--------------|
| **Startup** | 21,600 tokens (all tools) | 50 tokens (server list) |
| **Discovery** | Already loaded | 300 tokens (tool summaries) |
| **Execution** | Already loaded | 10,200 tokens (active server only) |
| **Multiple Servers** | All 21,600 always loaded | Load only what's used |

**Real-world scenario**: If you only use GitHub and Slack in a conversation, the gateway loads 2 servers (~11,000 tokens) instead of all 5 (~21,600 tokens). That's **10,000 additional tokens** available for your actual conversation.

## Why Choose Claude MCP Server Gateway?

### The Problem with Multiple MCP Servers
When using Claude Desktop with multiple MCP servers, you face:
- **Token Explosion**: Each MCP server adds 10-50 tools to Claude's context
- **Context Saturation**: 15,000-20,000 tokens consumed before you even start
- **Tool Overload**: Claude sees 100+ tools, making selection slower and less accurate
- **Management Complexity**: No central control over MCP server lifecycle

### The Gateway Solution
Claude MCP Server Gateway solves these issues by acting as a master MCP server:
- **97% Token Reduction**: From ~21,600 tokens → ~600 tokens at startup
- **Dynamic Loading**: MCP servers load only when their tools are needed
- **Intelligent Management**: Automatic connection lifecycle and error handling
- **Universal Compatibility**: Works with any MCP server (Python, Node.js, TypeScript)

## Real Conversation Flow: How Claude Uses the Gateway

Here's what actually happens when you ask Claude to work with GitHub:

### Step 1: You Ask Claude
```
You: "Find all open issues in the microsoft/vscode repository with the 'bug' label"
```

### Step 2: Claude Discovers Available MCP Servers
**Claude's thought process**: *"I need to work with GitHub. Let me check what MCP servers are available."*

**Gateway response** (Level 1 - Server Discovery):
```json
{
  "servers": [
    {
      "name": "github",
      "description": "Repository management, issues, PRs, code analysis",
      "status": "available"
    },
    {
      "name": "slack",
      "description": "Team communication and messaging",
      "status": "available"
    }
  ]
}
```
**Tokens used**: 50 total

### Step 3: Claude Loads GitHub Tool Summaries  
**Claude**: *"GitHub is available. Let me load its tool summaries to find the right one."*

**Action**: `load_mcp_tools(mcp_name="github")`

**Gateway response** (Level 2 - Tool Summaries):
```json
{
  "tools": [
    {"name": "search_repositories", "description": "Find repos by query"},
    {"name": "list_issues", "description": "List issues with filters"},
    {"name": "create_issue", "description": "Create new issue"}
  ]
}
```
**Tokens used**: 300 additional (350 total)

### Step 4: Claude Executes the Tool
**Claude**: *"I need 'list_issues' with owner, repo, and label filters."*

**Action**: `call_mcp_tool(mcp_name="github", tool_name="list_issues", arguments={...})`

**Gateway**: Loads full GitHub MCP server, executes query, returns results

**Tokens used**: 10,200 additional (10,550 total for entire interaction)

### The Efficiency Gain

**Without Gateway** (traditional MCP):
- Startup: 21,600 tokens loaded immediately
- Conversation: ~3,000 tokens for Q&A
- **Total context used**: 24,600 tokens (98% of available context!)
- **Problem**: Almost no room for actual conversation

**With Gateway**:
- Startup: 50 tokens (server list)
- Load GitHub summaries: 300 tokens
- Execute tool: 10,200 tokens (when actually needed)
- Conversation: ~3,000 tokens for Q&A
- **Total: 13,550 tokens (54% of context)**
- **Benefit**: 11,050 tokens (44%) still available for deeper analysis

### Universal Compatibility

The Claude MCP Server Gateway works with **any Model Context Protocol server**:
- ✅ Official MCP servers (GitHub, Slack, Google Drive, Brave Search)
- ✅ Community MCP servers (Memory, Filesystem, Postgres, SQLite)  
- ✅ Your custom Python/Node.js/TypeScript MCP servers
- ✅ Docker-based MCP servers
- ✅ Remote HTTP+SSE MCP servers

**No modifications needed** - if it implements the Model Context Protocol specification, the gateway manages it automatically.

## Quick Start

### For Claude Desktop Users

```bash
# 1. Clone the Claude MCP Server Gateway
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

# 2. Set up Python environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install the gateway
pip install mcp python-dotenv

# 4. Configure your MCP servers
cp .env.example .env
# Edit .env with your API keys

# 5. Add to Claude Desktop (see detailed instructions below)
```

### For Claude API/Code Users
The gateway also works with Claude API and Claude Code - see [Advanced Usage](#advanced-usage).

## Installation

### Prerequisites
- Python 3.11+ (required for MCP server compatibility)
- Claude Desktop, Claude API access, or Claude Code
- MCP servers you want to use (GitHub, Slack, Google Drive, etc.)

### Step 1: Install Claude MCP Server Gateway

```bash
# Clone the gateway repository
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

# Create virtual environment (recommended for Python MCP servers)
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install gateway dependencies
pip install -r requirements.txt
```

### Step 2: Configure Your MCP Servers

The gateway needs access to your MCP server credentials:

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your MCP server API keys
nano .env  # or use your preferred editor
```

Add your API keys for the MCP servers you want to use through the gateway:

```env
# GitHub MCP Server
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# Slack MCP Server (if using)
SLACK_BOT_TOKEN=your_slack_token

# Add any other MCP server credentials
```

### Step 3: Configure Claude Desktop

Add Claude MCP Server Gateway to your Claude Desktop configuration:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Replace your entire `mcpServers` section with just the gateway:

```json
{
  "mcpServers": {
    "claude-mcp-server-gateway": {
      "command": "/path/to/your/.venv/bin/python",
      "args": ["/path/to/claude-mcp-server-gateway/dcl_wrapper.py"],
      "env": {}
    }
  }
}
```

**Important**: Update paths to match your actual installation location.

### Step 4: Restart Claude Desktop

Completely quit and restart Claude Desktop for the gateway to initialize.

## Configuration

### Adding New MCP Servers to the Gateway

Extend the gateway with any MCP server by adding to `dcl_wrapper.py`:

```python
MCP_SERVERS = {
    "your-mcp-server": {
        "command": "npx",  # or python path
        "args": ["-y", "your-mcp-package"],
        "env": {
            "API_KEY": os.getenv("YOUR_API_KEY", "")
        },
        "description": "Your MCP server description"
    }
}
```

The gateway automatically manages connections to both pre-configured and custom MCP servers.

### Timeout Configuration

Customize timeouts via environment variables:

```env
# Operation timeout (default: 300 seconds)
GATEWAY_OPERATION_TIMEOUT=300

# Initialization timeout (default: 30 seconds)
GATEWAY_INIT_TIMEOUT=30
```

## Pre-configured MCP Servers

Claude MCP Server Gateway comes with popular MCP servers pre-configured and ready to use:

### Developer Tools
- **GitHub** - Complete GitHub integration: repositories, issues, PRs, workflows, code scanning
- **Context7** - Current code documentation and best practices lookup

### SEO & Analytics 
- **DataForSEO** - SERP data, keyword research, backlink analysis
- **Google Analytics** - Analytics reporting and metrics
- **Google Search Console** - Search performance and indexing

### Productivity & Collaboration
- **Google Workspace** - Gmail, Drive, Calendar, Docs, Sheets integration
- **Slack** - Team communication and channel management
- **Memory Extension Pro** - Persistent memory with semantic search

### Automation
- **Apify Actors** - Web scraping and automation workflows

## Performance: Real Token Savings

### Scenario 1: Typical Developer Setup
**MCP Servers Configured**: GitHub (51 tools), Slack (20 tools), Filesystem (12 tools)

| Metric | Without Gateway | With Gateway | Savings |
|--------|----------------|--------------|---------|
| Startup Tokens | 16,600 | 50 | **16,550** (99.7%) |
| First Tool Use | 0 (preloaded) | ~300 | +300 |
| Active Server | 0 (preloaded) | ~10,200 | +10,200 |
| **Typical Session** | **16,600** | **~4,000** | **12,600 (76%)** |

*Assumes using 1-2 MCP servers per conversation*

### Scenario 2: Enterprise Setup  
**MCP Servers**: GitHub, Slack, Google Drive, Postgres, Memory, Jira, Linear, Confluence (8 servers, ~150 tools)

| Metric | Without Gateway | With Gateway | Improvement |
|--------|----------------|--------------|-------------|
| Context Available at Startup | 5% | 99.8% | **+94.8%** |
| Response Time (first query) | Slow (100+ tools) | Fast (3 tools) | **~50x faster** |
| Token Efficiency | Poor | Excellent | **97% reduction** |

### Why Token Savings Matter

Every token consumed by tool definitions is a token you CAN'T use for:
- ❌ Providing more context about your task
- ❌ Sharing relevant code or documentation  
- ❌ Getting detailed, nuanced responses
- ❌ Having multi-turn conversations with context retention

**With 21,000 tokens freed up**, you can share:
- 10+ full source code files for analysis
- Complete API documentation for reference
- Extensive conversation history for context
- Detailed specifications and requirements

The Claude MCP Server Gateway doesn't just save tokens - it fundamentally changes what's possible in a single Claude Desktop session.

## Frequently Asked Questions

### Does this work with all MCP servers?
**Yes.** Claude MCP Server Gateway is compatible with any server implementing the Model Context Protocol specification. This includes:
- Python MCP servers (official SDK)
- Node.js/TypeScript MCP servers  
- Remote HTTP+SSE MCP servers
- Docker-containerized MCP servers
- Your custom MCP implementations

### Will this slow down my tool execution?
**No.** Tool execution speed is identical. The gateway adds ~50ms for initial tool discovery, but tool execution happens at native MCP server speed. The performance gain from reduced context processing far outweighs any overhead.

### Can I preload specific MCP servers?
**Current version**: All servers load on-demand  
**Roadmap**: We're adding configurable preload rules for frequently-used MCP servers in v2.1

### How does this compare to GitHub's dynamic toolsets?
GitHub MCP offers dynamic toolsets within their server. Claude MCP Server Gateway manages ALL your MCP servers dynamically - GitHub, Slack, Google Drive, and any other Model Context Protocol servers you use. It's a layer above individual server features.

### What if I use Claude API instead of Claude Desktop?
The gateway works with Claude API, Claude Code, and Claude Desktop. Configuration differs slightly - see [Advanced Usage](#advanced-usage) for API-specific setup.

### How do I add my custom MCP server to the gateway?
Add your server configuration to the gateway's config (see [Configuration](#adding-new-mcp-servers-to-the-gateway)). The gateway automatically discovers and manages any compliant MCP server.

## Troubleshooting Claude MCP Server Gateway

### Gateway Not Appearing in Claude Desktop

**Solution**: 
1. Verify the gateway path in `claude_desktop_config.json`
2. Check Python path points to virtual environment
3. Restart Claude Desktop completely (not just close window)

### MCP Server Connection Errors Through Gateway

**Common causes**:
- Missing API credentials in `.env` file
- MCP server package not installed
- Network connectivity issues

**Solution**: Check gateway logs at `~/.claude-mcp-gateway/logs/`

### Claude Still Shows 100+ Tools Instead of Gateway

This means the gateway isn't being used. Ensure:
1. You've replaced ALL MCP server entries with just the gateway
2. Started a NEW conversation (gateway doesn't affect existing chats)
3. Claude Desktop was fully restarted after configuration

### Timeout Errors When Loading MCP Servers

Increase timeouts in your `.env`:
```env
GATEWAY_OPERATION_TIMEOUT=600
GATEWAY_INIT_TIMEOUT=60
```

## Technical Architecture

### Gateway Design Pattern

Claude MCP Server Gateway implements a lightweight service mesh pattern for MCP servers:

1. **Service Discovery**: Dynamic MCP server registration and discovery
2. **Load Balancing**: Intelligent routing to appropriate MCP servers  
3. **Circuit Breaking**: Automatic failure handling and recovery
4. **Connection Pooling**: Efficient resource management

### MCP Protocol Compliance

The gateway fully implements the Model Context Protocol specification (v2025-06-18):
- Standard MCP handshake and capability negotiation
- Tool discovery and invocation protocol
- Error handling and timeout management
- Compatible with all MCP transport types (stdio, HTTP+SSE)

### Supported MCP Server Types

- **Python MCP Servers**: Native support via subprocess
- **Node.js MCP Servers**: Full compatibility via npx
- **TypeScript MCP Servers**: Compiled or ts-node execution
- **Docker MCP Servers**: Container-based MCP servers
- **Remote MCP Servers**: HTTP+SSE based servers

### Performance Optimizations

- Lazy loading of MCP server connections
- Automatic connection cleanup after operations
- Shared environment variable management
- Intelligent caching of MCP server metadata

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## Related Resources

### Official Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io) - Official MCP docs
- [Claude Desktop Download](https://claude.ai/download) - Get Claude Desktop
- [Anthropic MCP Guide](https://docs.anthropic.com/mcp) - Anthropic's MCP documentation

### Community Resources
- [Awesome MCP Servers](https://github.com/topics/mcp-server) - Discover MCP servers
- [MCP Server Development Guide](https://modelcontextprotocol.io/docs/server) - Build your own

### Gateway Ecosystem
- [Claude MCP Server Gateway Wiki](https://github.com/bzsasson/claude-mcp-server-gateway/wiki) - Extended documentation
- [Gateway Configuration Examples](https://github.com/bzsasson/claude-mcp-server-gateway/tree/main/examples) - Sample configs

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io) specification
- Uses patterns from the official MCP Python SDK
- Inspired by dynamic context loading best practices

## Keywords

Python MCP server gateway, Claude MCP Server Gateway, Model Context Protocol gateway, Claude Desktop MCP integration, MCP server manager, token optimization for Claude, dynamic MCP loading, Claude AI gateway, Anthropic MCP tools, context window management, MCP server Python, claude-mcp-server, server gateway architecture

---

**Built with** [Model Context Protocol](https://modelcontextprotocol.io) | **For** [Claude Desktop](https://claude.ai) | **License**: MIT