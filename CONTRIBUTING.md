# Contributing

## Adding a new MCP server

Edit `dcl_wrapper.py` and add to `MCP_SERVERS`:

```python
"your-server": {
    "command": "npx",
    "args": ["-y", "@your-org/mcp-server"],
    "env": {
        "API_KEY": os.getenv("YOUR_API_KEY", "")
    },
    "description": "What it does"
}
```

Test it works, submit a PR.

## Bug reports

Open an issue with:
- What broke
- How to reproduce it
- Error messages/logs

## Pull requests

1. Fork it
2. Make your changes
3. Test with Claude Desktop
4. Submit PR

That's it.
