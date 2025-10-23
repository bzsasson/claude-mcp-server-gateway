# Contributing to Claude MCP Server Gateway

Thank you for your interest in improving Claude MCP Server Gateway - the intelligent gateway for Claude Desktop MCP servers!

## Overview

Claude MCP Server Gateway acts as a dynamic routing layer for Model Context Protocol servers, and we welcome contributions that enhance its gateway capabilities.

## Quick Contribution Guide

### Adding New MCP Servers to the Gateway

Want to add support for a new MCP server? Here's how:

1. Fork `claude-mcp-server-gateway`
2. Add your MCP server configuration to the `MCP_SERVERS` dictionary in `gateway.py`
3. Test with Claude Desktop to ensure gateway integration works
4. Submit a PR with:
   - MCP server configuration
   - Required environment variables
   - Brief description of the MCP server's capabilities

### Example MCP Server Addition

```python
# In gateway.py (or dcl_wrapper.py before rename)
MCP_SERVERS = {
    # ... existing servers ...
    
    "your-mcp-server": {
        "command": "npx",  # or python path
        "args": ["-y", "@your-org/mcp-server"],
        "env": {
            "API_KEY": os.getenv("YOUR_API_KEY", "")
        },
        "description": "Your MCP server description for Claude"
    }
}
```

### Improving Gateway Features

Ideas for gateway enhancements:
- Load balancing between multiple MCP server instances
- Caching frequently used MCP tool responses
- Gateway middleware for authentication/logging
- Performance monitoring and metrics
- Circuit breaker patterns for failing MCP servers
- Request routing optimization

## Development Setup

```bash
# Clone the gateway
git clone https://github.com/bzsasson/claude-mcp-server-gateway.git
cd claude-mcp-server-gateway

# Set up development environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install pytest flake8 black mypy  # Common dev tools

# Run the gateway locally
python gateway.py  # or dcl_wrapper.py before rename
```

## Testing Your Changes

### Manual Testing with Claude Desktop

1. Update your Claude Desktop config to point to your local gateway:
   ```json
   {
     "mcpServers": {
       "claude-mcp-server-gateway-dev": {
         "command": "/path/to/your/dev/.venv/bin/python",
         "args": ["/path/to/your/dev/gateway.py"],
         "env": {}
       }
     }
   }
   ```

2. Restart Claude Desktop

3. Test the three gateway commands:
   - "List available MCP servers"
   - "Load [server name] MCP tools"
   - "Use [tool name] to [action]"

### Automated Testing

```bash
# Run tests (when available)
python -m pytest tests/

# Check code style
python -m flake8 .

# Format code
python -m black .
```

### Testing Checklist

Before submitting a PR, ensure:
- [ ] All existing MCP servers still work
- [ ] Token usage remains optimized (check with Claude)
- [ ] Error handling works for connection failures
- [ ] Timeouts are properly configured
- [ ] Gateway commands respond correctly
- [ ] Documentation is updated if needed

## Gateway Architecture Contributions

When contributing to core gateway functionality:

### Design Principles

1. **Minimal Token Usage**: The gateway should always minimize Claude's context usage
2. **Dynamic Loading**: MCP servers connect only when needed
3. **Error Isolation**: One failing MCP shouldn't affect others
4. **Protocol Compliance**: Follow the Model Context Protocol specification
5. **Universal Compatibility**: Support Python, Node.js, and TypeScript MCPs

### Core Components

- **Discovery Layer**: How the gateway finds and lists MCP servers
- **Dynamic Loader**: On-demand MCP server initialization
- **Execution Engine**: Tool invocation and response handling
- **Lifecycle Manager**: Connection pooling and cleanup

### Adding New Features

When adding features, consider:
- Backward compatibility with existing setups
- Impact on token usage
- Error handling and recovery
- Performance implications
- Claude Desktop compatibility

## Reporting Issues

Found a bug in the gateway? Open an issue with:

### Bug Report Template

```markdown
**Environment:**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.11.5]
- Claude Desktop version: [e.g., 1.0.0]
- Gateway version/commit: [e.g., v2.0.0 or commit hash]

**MCP Server:**
- Name: [e.g., github]
- Version: [if applicable]

**Description:**
[Clear description of the issue]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [etc.]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Logs:**
```
[Paste relevant logs from ~/.claude-mcp-gateway/logs/]
```

**Additional Context:**
[Any other relevant information]
```

## Documentation

Help us improve gateway documentation:

### Documentation Areas

- **README.md**: Main documentation and quick start
- **CONTRIBUTING.md**: This file - contribution guidelines
- **Wiki**: Extended tutorials and guides (if applicable)
- **Code Comments**: Inline documentation for complex logic

### Documentation Standards

- Use clear, concise language
- Include code examples where helpful
- Keep SEO in mind (use relevant keywords naturally)
- Test all code examples before submitting
- Update version numbers and dates where applicable

## Pull Request Process

1. **Fork and Clone**: Fork the repo and clone locally
2. **Branch**: Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit**: Make commits with clear messages
4. **Test**: Thoroughly test your changes
5. **Push**: Push to your fork
6. **PR**: Open a Pull Request with:
   - Clear title and description
   - Link to any related issues
   - Screenshots/logs if applicable
   - Test results

### PR Title Format

```
[Type] Brief description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- style: Code style/formatting
- refactor: Code restructuring
- test: Testing improvements
- perf: Performance improvements
```

## Code of Conduct

We're committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive
- Welcome newcomers and help them get started
- Focus on what's best for the community
- Show empathy towards other contributors

## Questions?

- **GitHub Discussions**: For general questions and ideas
- **Issues**: For bugs and feature requests
- **PR Comments**: For code-specific discussions

## Recognition

Contributors are recognized in:
- The project README (major contributors)
- Release notes (per-release contributors)
- GitHub's contributor graph

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make Claude MCP Server Gateway better! Your contributions help the entire Claude community work more efficiently with MCP servers.
