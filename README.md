# MCP Jira

**[➡️ REPLACE: Write a clear, concise description of your MCP server's purpose. What problems does it solve? What capabilities does it provide to AI tools?]**

## Overview

**[➡️ REPLACE: Provide a more detailed explanation of your MCP server's architecture, key components, and how it integrates with AI tools. What makes it unique or valuable?]**

## Features

**[➡️ REPLACE: List the key features of your MCP server. Some examples:]
- What unique tools does it provide?
- What data sources can it access?
- What special capabilities does it have?
- What performance characteristics are notable?
- What integrations does it support?**

## Installation

### From PyPI (if published)

There are two main ways to use the server if it's published on PyPI:

**Option 1: Install and then Run (Recommended for regular use)**

First, install the package into your Python environment using UV:
```bash
# Install using UV
uv pip install mcp_jira

# If you don't have UV, you can use pip:
# pip install mcp_jira
```

Once installed, you can run the server from your terminal:
```bash
mcp_jira-server
```

**Option 2: Run Directly with `uvx` (For quick use without permanent installation)**

If you want to run the server without installing it into your current environment (or to run a specific version easily), you can use `uvx`. This is handy for one-off tasks or testing.

```bash
# Run the latest version of the server directly from PyPI
uvx mcp_jira mcp_jira-server

# You can also specify a version:
# uvx mcp_jira==1.2.3 mcp_jira-server
```
This command tells `uvx` to fetch the `mcp_jira` package and execute its `mcp_jira-server` command.

### From Source

```bash
# Clone the repository
git clone <your-repository-url>
cd mcp_jira

# Create and activate a virtual environment using UV
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode using UV
uv pip install -e .
```

## Available Tools

### tool_name

**[➡️ REPLACE: For each tool in your MCP server, document:]
- What the tool does
- Its parameters and their types
- What it returns
- Example usage and expected output
- Any limitations or important notes**

Example:
```bash
# Using stdio transport (default)
mcp_jira-client "your command here"

# Using SSE transport
mcp_jira-server --transport sse
curl http://localhost:3001/sse
```

## Usage

This MCP server provides two entry points:

1. `mcp_jira-server`: The MCP server that handles tool requests
   ```bash
   # Run with stdio transport (default)
   mcp_jira-server

   # Run with SSE transport
   mcp_jira-server --transport sse
   ```

## Logging

The server logs all activity to both stderr and a rotating log file. Log files are stored in OS-specific locations:

- **macOS**: `~/Library/Logs/mcp-servers/mcp_jira.log`
- **Linux**: 
  - Root user: `/var/log/mcp-servers/mcp_jira.log`
  - Non-root: `~/.local/state/mcp-servers/logs/mcp_jira.log`
- **Windows**: `%USERPROFILE%\AppData\Local\mcp-servers\logs\mcp_jira.log`

Log files are automatically rotated when they reach 10MB, with up to 5 backup files kept.

You can configure the log level using the `LOG_LEVEL` environment variable:
```bash
# Set log level to DEBUG for more detailed logging
LOG_LEVEL=DEBUG mcp_jira-server
```

Valid log levels are: DEBUG, INFO (default), WARNING, ERROR, CRITICAL

2. `mcp_jira-client`: A convenience client for testing
   ```bash
   mcp_jira-client "your command here"
   ```

**[➡️ REPLACE: Add any additional usage examples, common patterns, or best practices specific to your tools]**

## Requirements

- Python 3.11 or later (< 3.13)
- Operating Systems: Linux, macOS, Windows

**[➡️ REPLACE: Add any additional requirements specific to your MCP server:]
- Special system dependencies
- External services or APIs needed
- Network access requirements
- Hardware requirements (if any)**

## Configuration

**[➡️ REPLACE: Document any configuration options your MCP server supports:]
- Environment variables
- Configuration files
- Command-line options
- API keys or credentials needed

Remove this section if your server requires no configuration.**

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions.

**[➡️ REPLACE: Add any project-specific development notes, guidelines, or requirements]**

## Troubleshooting

Common issues and their solutions:

**[➡️ REPLACE: Add troubleshooting guidance specific to your MCP server. Remove this section if not needed.]**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**[➡️ REPLACE: Add your name and contact information]**

---

[Replace this example Echo server README with documentation specific to your MCP server. Use this structure as a template, but customize all sections to describe your server's actual functionality, tools, and configuration options.]
