# Development Guide

This guide is for developers working on the MCP JIRA Server codebase.

## Prerequisites

- Python 3.11 or 3.12
- UV package manager
- Node.js (for MCP Inspector)

## Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/codingthefuturewithai/mcp_jira.git
cd mcp_jira
```

2. Create a virtual environment and install in development mode:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Testing with MCP Inspector

MCP Inspector is the primary tool for testing MCP servers during development.

### Running the Server with MCP Inspector

```bash
mcp dev mcp_jira/server/app.py
```

This will:
1. Start the MCP JIRA server
2. Open MCP Inspector in your browser
3. Allow you to interactively test all available tools

### Available Tools for Testing

- **echo** - Simple test tool for verifying the server is working
- **create_jira_issue** - Create JIRA issues with markdown descriptions
- **update_jira_issue** - Update existing JIRA issues
- **search_jira_issues** - Search using JQL syntax

### Configuration for Development

The server will use configuration from:
1. `MCP_JIRA_CONFIG_PATH` environment variable (if set)
2. Default OS location:
   - macOS: `~/Library/Application Support/mcp_jira/config.yaml`
   - Linux: `~/.config/mcp_jira/config.yaml`
   - Windows: `%APPDATA%\MCPJira\mcp_jira\config.yaml`

If no config exists, a template will be created automatically.

## Running Tests

```bash
# Run any unit tests (when implemented)
pytest
```

## Code Structure

- `mcp_jira/server/app.py` - Main server implementation with FastMCP
- `mcp_jira/services/jira_service.py` - JIRA API client
- `mcp_jira/tools/` - Individual tool implementations
- `mcp_jira/converters/` - Markdown to ADF conversion
- `mcp_jira/ui/` - Streamlit configuration interface

## Making Changes

1. Create a feature branch
2. Make your changes
3. Test thoroughly with MCP Inspector
4. Submit a pull request

## Debugging Tips

- Check logs at:
  - macOS: `~/Library/Logs/mcp-servers/mcp_jira.log`
  - Linux: `~/.local/state/mcp_jira/mcp_jira.log`
  - Windows: `%LOCALAPPDATA%\MCPJira\mcp_jira\Logs\mcp_jira.log`

- Use `log_level: "DEBUG"` in config.yaml for verbose logging
- The server creates a module-level instance for `mcp dev` compatibility