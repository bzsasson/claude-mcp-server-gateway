# Changelog

## [2.0.0] - 2025-10-23

### 🎉 Major Release: Claude MCP Server Gateway

#### Changed
- **Renamed**: Project renamed from `dcl-wrapper` to `claude-mcp-server-gateway`
  - Better SEO alignment with search intent
  - Clearer positioning as a gateway solution
  - Matches enterprise naming patterns (Microsoft, IBM gateways)

#### Enhanced
- **Documentation**: Complete README overhaul with gateway architecture focus
- **Positioning**: Emphasized dynamic gateway pattern vs static loading
- **SEO**: Optimized for "claude-mcp-server" and "server gateway" keywords

#### Technical
- No breaking changes to code functionality
- Backward compatible with existing configurations
- All MCP server integrations remain unchanged

### Why Gateway?
This release positions the project as a gateway rather than a wrapper, aligning with industry standards for service management layers. The gateway pattern better describes our dynamic routing and lifecycle management capabilities.

---

## [1.0.1] - 2025-10-22

### Added
- Support for Google Analytics MCP
- Support for Google Search Console MCP  
- Support for Apify Actors MCP
- Support for Google Workspace MCP (Gmail, Drive, Calendar, Docs, Sheets, Tasks, Chat)
- Support for DataForSEO MCP (SERP data, keywords, backlinks)
- Support for Memory Extension Pro MCP
- Support for Context7 MCP
- GitHub MCP support (repositories, issues, PRs, code search, CI/CD workflows, security)
- Comprehensive error handling with timeouts
- Environment variable configuration via .env file
- Automatic connection lifecycle management

### Changed
- Updated documentation with detailed troubleshooting guide
- Improved installation instructions for different operating systems

### Technical Details
- Requires Python 3.11+
- Uses MCP Python SDK patterns from Context7 documentation
- Implements Model Context Protocol specification (2025-06-18)
- Supports both stdio and HTTP+SSE transports

## [1.0.0] - 2025-10-22

### Initial Release
- Dynamic MCP server loading for Claude Desktop
- Token usage optimization (95% reduction)
- Environment variable management with .env
- Compatible with Claude Desktop, Claude API, and Claude Code
- Pre-configured support for 8 popular MCP servers
- Comprehensive documentation and examples