# -*- coding: utf-8 -*-
"""
DCL (Dynamic Context Loading) Wrapper for MCP Servers
A master MCP server that manages all your other MCP servers dynamically.

Instead of loading all tools from all MCPs upfront, this wrapper:
1. Exposes brief summaries of available MCP servers  
2. Provides a single "load_mcp_tools" tool to load specific MCP tools on-demand
3. Dynamically connects to and disconnects from MCP servers as needed

This dramatically reduces token consumption by only loading tools when needed.

Based on official MCP Python SDK patterns from Context7 documentation (2025).
"""

import asyncio
import json
import os
import sys
import traceback
from typing import Any, Optional, Dict

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP

# Add dotenv import and load
from dotenv import load_dotenv
load_dotenv()

# Create the master MCP server
mcp = FastMCP("DCL Master MCP")

# Check for required environment variables at startup
REQUIRED_ENV_VARS = {
    "memory-extension-pro": ["GEMINI_API_KEY"],
    "google-search-console": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
    "actors-mcp-server": ["APIFY_TOKEN"],
    "dataforseo": ["DATAFORSEO_USERNAME", "DATAFORSEO_PASSWORD"]
}

# Warning message for missing env vars (non-fatal)
def check_env_vars():
    """Check for required environment variables and warn if missing."""
    missing_vars = {}
    for server_name, required_vars in REQUIRED_ENV_VARS.items():
        for var in required_vars:
            if not os.getenv(var):
                if server_name not in missing_vars:
                    missing_vars[server_name] = []
                missing_vars[server_name].append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables for some MCPs:", file=sys.stderr)
        for server, vars in missing_vars.items():
            print(f"   {server}: {', '.join(vars)}", file=sys.stderr)
        print("   These MCPs may not work without the required environment variables.", file=sys.stderr)
        print("", file=sys.stderr)

# Check env vars on startup
check_env_vars()

# Configuration: Your existing MCP servers
# 
# IMPORTANT: Customize the paths below to match your installation!
# 
# NPX-based servers (like "context7", "actors-mcp-server") work universally
# Local path servers (like "memory-extension-pro", "google-workspace") need your paths
# 
# To customize:
# 1. Update command paths to match your system
# 2. Update args to point to your script locations  
# 3. Add/remove servers as needed
# 4. Set required environment variables in .env file
#
MCP_SERVERS = {
    # Universal NPX-based server (works for everyone)
    "context7": {
        "command": "npx",
        "args": [
            "-y",
            "@upstash/context7-mcp"
        ],
        "env": {},
        "description": "Context7 for checking current code documentation"
    },
    # LOCAL PATH EXAMPLE - Customize these paths to your installation!
    # Replace /Users/boazsasson/Roo/... with your actual paths
    "memory-extension-pro": {
        "command": "/Users/boazsasson/Roo/claude-memory-extension-mcp/venv/bin/python",
        "args": [
            "/Users/boazsasson/Roo/claude-memory-extension-mcp/mcp_memory_server_hybrid.py"
        ],
        "env": {
            # No default - must be set as environment variable
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "")
        },
        "description": "Advanced memory storage with permanent files, temporary content, semantic search"
    },
    "google-analytics": {
        "command": "npx",
        "args": [
            "-y",
            "supergateway",
            "--sse",
            "https://mcp.pipedream.net/9148c057-4cf8-4b35-ac39-b596ce6f68bc/google_analytics"
        ],
        "env": {},
        "description": "Google Analytics reporting and metrics"
    },
    # LOCAL PATH EXAMPLE - Customize to your installation!
    "google-search-console": {
        "command": "node",
        "args": [
            "/Users/boazsasson/Roo/mcp-servers/gsc-oauth-mcp/build/index.js"
        ],
        "env": {
            # No defaults - must be set as environment variables
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "")
        },
        "description": "Google Search Console data: search analytics, URL inspection, sitemaps"
    },
    "actors-mcp-server": {
        "command": "npx",
        "args": [
            "-y",
            "@apify/actors-mcp-server"
        ],
        "env": {
            # No default - must be set as environment variable
            "APIFY_TOKEN": os.getenv("APIFY_TOKEN", "")
        },
        "description": "Apify Actor platform: web scraping, automation, data extraction"
    },
    # LOCAL PATH EXAMPLE - Customize to your installation!
    "google-workspace": {
        "command": "/Users/boazsasson/Roo/mcp-servers/google_workspace_mcp/.venv/bin/python",
        "args": [
            "/Users/boazsasson/Roo/mcp-servers/google_workspace_mcp/main.py"
        ],
        "env": {
            "OAUTHLIB_INSECURE_TRANSPORT": "1"
        },
        "description": "Google Workspace: Gmail, Drive, Calendar, Docs, Sheets, Tasks, Chat"
    },
    # Universal NPX-based server (works for everyone)
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        },
        "description": "GitHub: repositories, issues, PRs, code search, CI/CD workflows, security"
    },
    "dataforseo": {
        "command": "npx",
        "args": [
            "-y",
            "dataforseo-mcp-server",
            "local",
            "--debug"
        ],
        "env": {
            # No defaults - must be set as environment variables
            "DATAFORSEO_USERNAME": os.getenv("DATAFORSEO_USERNAME", ""),
            "DATAFORSEO_PASSWORD": os.getenv("DATAFORSEO_PASSWORD", "")
        },
        "description": "DataForSEO: SERP data, keywords, backlinks, domain analytics, content analysis"
    }
}

# Timeout for MCP operations (in seconds)
MCP_TIMEOUT = 300  # 5 minutes
MCP_INIT_TIMEOUT = 30  # 30 seconds for initialization

# Optional: Make timeouts configurable via environment
MCP_TIMEOUT = int(os.getenv("DCL_OPERATION_TIMEOUT", "300"))
MCP_INIT_TIMEOUT = int(os.getenv("DCL_INIT_TIMEOUT", "30"))


@mcp.tool()
def list_available_mcps() -> str:
    """
    List all available MCP servers and their capabilities.
    Use this first to see what tools are available before loading specific tools.
    """
    result = "Available MCP Servers:\n\n"
    
    for name, config in MCP_SERVERS.items():
        result += f"[MCP] {name}\n"
        result += f"      {config['description']}\n"
        
        # Check if this MCP has missing env vars
        if name in REQUIRED_ENV_VARS:
            missing = [var for var in REQUIRED_ENV_VARS[name] if not os.getenv(var)]
            if missing:
                result += f"      ⚠️  Missing env vars: {', '.join(missing)}\n"
        result += "\n"
    
    result += "\nTo use tools from any server, call: load_mcp_tools(mcp_name='server_name')"
    return result


@mcp.tool()
async def load_mcp_tools(mcp_name: str) -> str:
    """
    Load and list available tools from a specific MCP server.
    
    Args:
        mcp_name: Name of the MCP server (use list_available_mcps first to see options)
    
    Returns:
        List of available tools with descriptions from that MCP server
    """
    if mcp_name not in MCP_SERVERS:
        available = ", ".join(MCP_SERVERS.keys())
        return f"[ERROR] Unknown MCP server: {mcp_name}\n\nAvailable servers: {available}"
    
    # Check for missing environment variables
    if mcp_name in REQUIRED_ENV_VARS:
        missing = [var for var in REQUIRED_ENV_VARS[mcp_name] if not os.getenv(var)]
        if missing:
            return f"[ERROR] Cannot load {mcp_name}: Missing required environment variables: {', '.join(missing)}\n\nPlease set these environment variables and restart the DCL wrapper."
    
    config = MCP_SERVERS[mcp_name]
    
    # Create server parameters using official MCP SDK pattern
    server_params = StdioServerParameters(
        command=config["command"],
        args=config["args"],
        env=config.get("env", {})
    )
    
    try:
        # Use official MCP SDK pattern from Context7 docs
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection with timeout
                await asyncio.wait_for(session.initialize(), timeout=MCP_INIT_TIMEOUT)
                
                # List available tools with timeout
                tools_response = await asyncio.wait_for(
                    session.list_tools(),
                    timeout=MCP_TIMEOUT
                )
                
                # Format the response
                result = f"[OK] Tools from {mcp_name}:\n\n"
                
                if not tools_response.tools:
                    result += "No tools available from this server.\n"
                else:
                    for tool in tools_response.tools:
                        result += f"[TOOL] {tool.name}\n"
                        if tool.description:
                            result += f"       {tool.description}\n"
                        result += "\n"
                
                result += f"\nTo call a tool: call_mcp_tool(mcp_name='{mcp_name}', tool_name='tool_name', arguments={{...}})"
                return result
    
    except asyncio.TimeoutError:
        return f"[ERROR] Timeout connecting to {mcp_name} (exceeded {MCP_INIT_TIMEOUT}s for init or {MCP_TIMEOUT}s for operation)"
    except Exception as e:
        error_msg = f"[ERROR] Error connecting to {mcp_name}: {str(e)}\n\n"
        error_msg += "Stack trace:\n"
        error_msg += traceback.format_exc()
        return error_msg


@mcp.tool()
async def call_mcp_tool(
    mcp_name: str, 
    tool_name: str, 
    arguments: Optional[Dict[str, Any]] = None
) -> str:
    """
    Call a specific tool from an MCP server.
    
    Args:
        mcp_name: Name of the MCP server
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments to pass to the tool (optional)
    
    Returns:
        Result from the tool execution
    """
    if mcp_name not in MCP_SERVERS:
        available = ", ".join(MCP_SERVERS.keys())
        return f"[ERROR] Unknown MCP server: {mcp_name}\n\nAvailable servers: {available}"
    
    # Check for missing environment variables
    if mcp_name in REQUIRED_ENV_VARS:
        missing = [var for var in REQUIRED_ENV_VARS[mcp_name] if not os.getenv(var)]
        if missing:
            return f"[ERROR] Cannot use {mcp_name}: Missing required environment variables: {', '.join(missing)}\n\nPlease set these environment variables and restart the DCL wrapper."
    
    if arguments is None:
        arguments = {}
    
    config = MCP_SERVERS[mcp_name]
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=config["command"],
        args=config["args"],
        env=config.get("env", {})
    )
    
    try:
        # Use official MCP SDK pattern from Context7 docs
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection with timeout
                await asyncio.wait_for(session.initialize(), timeout=MCP_INIT_TIMEOUT)
                
                # Call the tool with timeout
                result = await asyncio.wait_for(
                    session.call_tool(tool_name, arguments=arguments),
                    timeout=MCP_TIMEOUT
                )
                
                # Extract text content from result (handle both unstructured and structured)
                output = []
                
                # Handle unstructured content (backward compatible)
                for content in result.content:
                    if hasattr(content, 'text'):
                        output.append(content.text)
                
                # Handle structured content (2025-06-18 spec)
                # Use hasattr to safely check for structuredContent attribute
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    output.append(f"\nStructured content: {json.dumps(result.structuredContent, indent=2)}")
                
                if output:
                    return "\n".join(output)
                else:
                    return f"[OK] Tool executed successfully but returned no text content"
    
    except asyncio.TimeoutError:
        return f"[ERROR] Tool {tool_name} on {mcp_name} timed out (exceeded {MCP_INIT_TIMEOUT}s for init or {MCP_TIMEOUT}s for operation)"
    except Exception as e:
        error_msg = f"[ERROR] Error calling {tool_name} on {mcp_name}: {str(e)}\n\n"
        error_msg += "Stack trace:\n"
        error_msg += traceback.format_exc()
        return error_msg


if __name__ == "__main__":
    # Run the DCL Master MCP server
    mcp.run()
