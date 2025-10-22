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

__version__ = "1.1.0"

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

# Default MCP servers (NPX-based, work universally - no local paths needed)
DEFAULT_MCP_SERVERS = {
    "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "env": {},
        "description": "Context7 for checking current code documentation"
    },
    "google-analytics": {
        "command": "npx",
        "args": ["-y", "supergateway", "--sse", 
                 "https://mcp.pipedream.net/9148c057-4cf8-4b35-ac39-b596ce6f68bc/google_analytics"],
        "env": {},
        "description": "Google Analytics reporting and metrics"
    },
    "actors-mcp-server": {
        "command": "npx",
        "args": ["-y", "@apify/actors-mcp-server"],
        "env": {
            "APIFY_TOKEN": os.getenv("APIFY_TOKEN", "")
        },
        "description": "Apify Actor platform: web scraping, automation, data extraction"
    },
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
        "args": ["-y", "dataforseo-mcp-server", "local", "--debug"],
        "env": {
            "DATAFORSEO_USERNAME": os.getenv("DATAFORSEO_USERNAME", ""),
            "DATAFORSEO_PASSWORD": os.getenv("DATAFORSEO_PASSWORD", "")
        },
        "description": "DataForSEO: SERP data, keywords, backlinks, domain analytics, content analysis"
    }
}


def load_config_file() -> Dict[str, Any]:
    """
    Load additional MCP servers from mcp_config.json if it exists.
    This file is git-ignored and contains user-specific paths.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'mcp_config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                servers = config.get('servers', {})
                
                # Process environment variables in the config
                for server_name, server_config in servers.items():
                    if 'env' in server_config:
                        # Replace empty strings with actual env vars
                        for env_key, env_val in server_config['env'].items():
                            if env_val == "":
                                server_config['env'][env_key] = os.getenv(env_key, "")
                
                if servers:
                    print(f"✅ Loaded {len(servers)} custom MCP server(s) from mcp_config.json", 
                          file=sys.stderr)
                return servers
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Could not parse mcp_config.json: {e}", file=sys.stderr)
            print(f"   Using only default MCP servers.", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Warning: Error loading mcp_config.json: {e}", file=sys.stderr)
            print(f"   Using only default MCP servers.", file=sys.stderr)
    else:
        print(f"ℹ️  No mcp_config.json found. Using only default MCP servers.", file=sys.stderr)
        print(f"   Copy mcp_config.example.json to mcp_config.json to add custom servers.", 
              file=sys.stderr)
    
    return {}


# Combine default and custom servers
MCP_SERVERS = {**DEFAULT_MCP_SERVERS, **load_config_file()}

# Check for required environment variables at startup
# Default requirements for built-in servers
REQUIRED_ENV_VARS = {
    "actors-mcp-server": ["APIFY_TOKEN"],
    "dataforseo": ["DATAFORSEO_USERNAME", "DATAFORSEO_PASSWORD"],
    "github": ["GITHUB_PERSONAL_ACCESS_TOKEN"]
}


def get_required_env_vars_from_config() -> Dict[str, list]:
    """Extract required env vars from custom config."""
    config_path = os.path.join(os.path.dirname(__file__), 'mcp_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                servers = config.get('servers', {})
                
                custom_reqs = {}
                for server_name, server_config in servers.items():
                    env_vars = server_config.get('env', {})
                    # Get keys that need to be set (those with empty string values)
                    required = [k for k, v in env_vars.items() if v == ""]
                    if required:
                        custom_reqs[server_name] = required
                return custom_reqs
        except:
            pass
    return {}


# Update with custom server requirements
REQUIRED_ENV_VARS.update(get_required_env_vars_from_config())


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

# Timeout for MCP operations (configurable via environment variables)
MCP_TIMEOUT = int(os.getenv("DCL_OPERATION_TIMEOUT", "300"))  # Default: 5 minutes
MCP_INIT_TIMEOUT = int(os.getenv("DCL_INIT_TIMEOUT", "30"))  # Default: 30 seconds


@mcp.tool()
def get_version() -> str:
    """Get DCL Wrapper version information."""
    return f"DCL Wrapper v{__version__}"


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
    except BaseException as e:  # Catches Exception, ExceptionGroup, and other exceptions
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
                
                # Handle structured content (MCP spec)
                # Use hasattr to safely check for structuredContent attribute
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    output.append(f"\nStructured content: {json.dumps(result.structuredContent, indent=2)}")
                
                if output:
                    return "\n".join(output)
                else:
                    return f"[OK] Tool executed successfully but returned no text content"
    
    except asyncio.TimeoutError:
        return f"[ERROR] Tool {tool_name} on {mcp_name} timed out (exceeded {MCP_INIT_TIMEOUT}s for init or {MCP_TIMEOUT}s for operation)"
    except BaseException as e:  # Catches Exception, ExceptionGroup, and other exceptions
        error_msg = f"[ERROR] Error calling {tool_name} on {mcp_name}: {str(e)}\n\n"
        error_msg += "Stack trace:\n"
        error_msg += traceback.format_exc()
        return error_msg


if __name__ == "__main__":
    # Run the DCL Master MCP server
    mcp.run()
