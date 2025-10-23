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