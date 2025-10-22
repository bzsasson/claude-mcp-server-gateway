# Changelog

All notable changes to DCL Wrapper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-22

### Added
- Initial release of DCL Wrapper
- Dynamic MCP server loading with on-demand tool exposure
- Support for multiple pre-configured MCP servers:
  - Context7
  - Memory Extension Pro
  - Google Analytics
  - Google Search Console
  - Apify Actors
  - Google Workspace
  - GitHub
  - DataForSEO
- Environment variable management with `.env` support
- Comprehensive error handling and timeout management
- Token usage optimization (95% reduction)
- Three core tools: `list_available_mcps`, `load_mcp_tools`, `call_mcp_tool`
- Automatic connection lifecycle management
- Configurable timeouts via environment variables

### Documentation
- Comprehensive README with installation instructions
- .env.example template for configuration
- Contributing guidelines
- MIT License
- Architecture diagrams and usage examples
