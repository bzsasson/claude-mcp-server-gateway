# Contributing to DCL Wrapper

Thank you for your interest in contributing to DCL Wrapper! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, Claude Desktop version)
- Relevant logs or error messages

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Please open an issue with:
- A clear description of the enhancement
- Why it would be useful
- Any potential implementation ideas

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Testing

Before submitting a PR:
- Test with multiple MCP servers
- Verify environment variable handling
- Check error handling edge cases
- Test with Claude Desktop

### Adding New MCP Servers

When adding pre-configured MCP servers to the default config:
1. Test the MCP server thoroughly
2. Document required environment variables in `.env.example`
3. Add to `REQUIRED_ENV_VARS` dictionary if needed
4. Update the README's "Supported MCP Servers" section
5. Provide a clear description in the `MCP_SERVERS` config

### Documentation

- Update README.md for any user-facing changes
- Add inline comments for complex code
- Update .env.example for new environment variables

## Questions?

Feel free to open an issue for any questions about contributing!
