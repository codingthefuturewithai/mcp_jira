# MCP JIRA Server

A Model Context Protocol (MCP) server that provides seamless JIRA integration for AI tools. Create and manage JIRA issues with rich markdown formatting, automatic conversion to Atlassian Document Format (ADF), and flexible field management.

## Quick Setup with Claude Code

### 🚀 Let AI Help You Set Up

Copy and paste one of these prompts to your AI coding assistant:

**For Setup Help:**
```
Please help me set up the MCP JIRA Server for Claude Code. 
Read the setup guide at: SETUP_ASSISTANT_PROMPT.md
```

**For Usage Examples:**
```
Show me how to use MCP JIRA Server effectively.
Read the usage guide at: USAGE_ASSISTANT_PROMPT.md
```

### ⚡ Quick Install (if you know what you're doing)

```bash
# Install UV if not already installed:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure JIRA settings via web UI:
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui

# Add to Claude Code:
claude mcp add mcp_jira stdio "uvx --from ctf-mcp-jira ctf-mcp-jira-server"
```

Then restart Claude Code. See full instructions below.

## Overview

This MCP server enables AI assistants to interact directly with JIRA instances through the JIRA REST API v3. It handles the complexity of markdown-to-ADF conversion, field mapping, and multi-site configuration, allowing AI tools to create well-formatted JIRA issues with minimal setup.

Key architectural components:
- **MCP Server**: FastMCP-based server with stdio/SSE transport support
- **JIRA Client**: Direct REST API integration with authentication handling
- **Markdown Converter**: Converts markdown to Atlassian Document Format (ADF)
- **Configuration System**: Multi-site JIRA configuration with flexible site selection
- **Field Management**: Support for both standard and custom JIRA fields

## Features

- **Rich Markdown Support**: Convert markdown descriptions to properly formatted ADF with support for:
  - Headers, paragraphs, and text formatting (bold, italic, inline code)
  - Fenced code blocks with syntax highlighting
  - Bullet and numbered lists
  - Tables and complex formatting elements

- **Flexible Field Management**:
  - Create and update JIRA issues with standard fields: project, summary, description, issue type.
  - Robust assignee handling: Provide an email address, and the server resolves it to the correct JIRA `accountId` for reliable assignment.
  - `additional_fields` parameter supports labels, priority, due dates, and other custom fields.
  - Graceful degradation for unavailable fields across different JIRA configurations.

- **Multi-Site Configuration**: Support for multiple JIRA instances with site aliases, configurable in `config.yaml`.
- **Comprehensive Error Handling**: Detailed error messages and logging.
- **Transport Flexibility**: Support for both stdio and SSE transport modes.

## Installation

### Recommended Method

Use `uvx` to run MCP JIRA Server without persistent installation:

```bash
# Install UV if not already installed
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Configure JIRA settings via web UI:
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui

# This launches a web interface at http://localhost:8501 for configuration
```

**Benefits of uvx:**
- No persistent installation to manage
- Always runs in a fresh, isolated environment
- Automatically downloads updates when available
- No "uninstall and reinstall" issues

**Note:** uvx downloads the package on first use and caches it. Subsequent runs are faster but still use a fresh environment.

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/codingthefuturewithai/mcp_jira.git
cd mcp_jira

# Create and activate a virtual environment using UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

### Troubleshooting Installation

**Common Issues:**
- **"Command not found"**: Ensure UV is installed and in your PATH
- **Port already in use**: Use `--ui-port 8502` (or another port) when launching the UI
- **Connection errors**: Check your internet connection as uvx downloads packages on demand
- For development, always use a virtual environment

**Platform-Specific Issues:**
- **Windows**: Run PowerShell as Administrator if you encounter permission errors
- **macOS**: If you get SSL errors, ensure certificates are updated: `brew install ca-certificates`
- **Linux**: May need to install additional system packages: `sudo apt-get install python3-dev`

For detailed troubleshooting, see the [Confluence documentation](https://codingthefuturewithai.atlassian.net/wiki/spaces/ACT/pages/89161729).

## Configuration

### JIRA Configuration

The server requires a `config.yaml` file to connect to your JIRA instance(s). The server will attempt to load this file from the following locations, in order of precedence:

1.  The path specified by the `--config` command-line argument.
2.  The path specified by the `MCP_JIRA_CONFIG_PATH` environment variable.
3.  The default OS-specific user configuration directory:
    *   **Linux**: `~/.config/mcp_jira/config.yaml`
    *   **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`
    *   **Windows**: `%APPDATA%\MCPJira\mcp_jira\config.yaml` (Note: `%APPDATA%` usually resolves to `C:\Users\<username>\AppData\Roaming`)

If the configuration file is not found at any of these locations, the server will automatically create the necessary directory (if it doesn't exist) and a template `config.yaml` file at the default OS-specific path. You will then need to edit this template with your actual JIRA site details.

Example of a filled-in `config.yaml`:
```yaml
name: "My Company JIRA Integration"
log_level: "INFO" # Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

default_site_alias: "prod_jira"

sites:
  prod_jira:
    url: "https://mycompany.atlassian.net"
    email: "automation-user@mycompany.com"
    api_token: "abc123xyz789efg_your_token_here_jkl"
    cloud: true

  dev_jira:
    url: "https://dev-mycompany.atlassian.net"
    email: "dev-automation@mycompany.com"
    api_token: "another_token_for_dev_environment"
    cloud: true

# Optional: Advanced logging configuration (defaults are usually sufficient)
# log_file_path: "/var/log/custom_mcp_jira/activity.log" # Overrides default log file paths
# log_max_bytes: 20971520  # Max log file size in bytes (e.g., 20MB)
# log_backup_count: 10     # Number of backup log files to keep
```

### JIRA API Token

1. Log into your JIRA instance.
2. Go to **Account Settings** (usually by clicking your avatar/profile picture).
3. Navigate to **Security** > **API token** (the exact path might vary slightly depending on your JIRA version).
4. Click **Create API token**.
5. Give your token a descriptive label (e.g., `mcp_jira_server_token`).
6. Copy the generated token immediately. **You will not be able to see it again.**
7. Add the copied token to your `config.yaml` file.

## Configuration Editor UI

This project includes a web-based configuration editor built with Streamlit to easily manage your `config.yaml` file.

### Features
- View and edit all general settings (Server Name, Log Level, Default Site Alias).
- View, edit, add, and delete JIRA site configurations (Alias, URL, Email, API Token, Cloud status).
- Changes are saved directly to the `config.yaml` file used by the MCP server.
- The editor automatically uses the same configuration file path logic as the server itself (CLI override, environment variable, or OS-specific default).

### Running the Editor

Use the `--ui` flag with the MCP server command to launch the configuration interface:

```bash
# Using uvx (recommended - no installation required)
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui

# Or specify a custom port
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui --ui-port 8502
```

This will open your browser with the Streamlit configuration UI at http://localhost:8501 (or your specified port).

### Screenshot

![MCP JIRA Server Configuration Editor](docs/images/mcp-server-config-editor.png)

## Usage

### Running the MCP Server

When using with Claude Code, the server is automatically started via the `claude mcp add` command shown in the quick setup. For manual testing or other uses:

```bash
# Run with stdio transport (default) using uvx
uvx --from ctf-mcp-jira ctf-mcp-jira-server

# Run with SSE transport
uvx --from ctf-mcp-jira ctf-mcp-jira-server --transport sse --port 3001

# Use custom configuration file
uvx --from ctf-mcp-jira ctf-mcp-jira-server --config /path/to/config.yaml

# Launch configuration UI
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui
```

**Note:** Using `uvx` ensures the server runs in a fresh, isolated environment each time, avoiding potential dependency conflicts.

### Available Tools

This server exposes the following tools for interacting with JIRA:

#### create_jira_issue

Creates a new JIRA issue. You can specify the project, summary, a detailed description in markdown (which will be converted to JIRA's rich text format), issue type, assignee, and other custom fields.

#### update_jira_issue

Updates an existing JIRA issue. You can modify fields such as the summary, description (markdown supported), assignee, issue type, or other custom fields. Only the fields you provide will be changed.

#### search_jira_issues

Search for JIRA issues using JQL (JIRA Query Language) syntax. Specify a JQL query to find issues matching your criteria.

**Parameters:**
- `query` (required): JQL query string to search for issues
- `site_alias` (optional): Site alias for multi-site configurations
- `basic_only` (optional, default: False): Controls the level of detail returned
  - When `False` (default): Returns comprehensive issue data including all standard fields, issue links, remote links, comments, and worklogs
  - When `True`: Returns only key, summary, and description for better performance

**Returns:**
- In basic mode: Issue key, summary, and description
- In full mode: Complete issue details including:
  - Standard fields (project, type, status, priority, assignee, dates)
  - Issue links (relationships to other JIRA issues like blocks, is blocked by, relates to, etc.)
  - Remote links (web links, Confluence pages, etc.)
  - Comments with author and timestamp
  - Worklogs with time tracking information

Example queries:
- `project = MYPROJECT`
- `project = MYPROJECT AND status = 'In Progress'`
- `assignee = currentUser() AND created >= -7d`

Example usage:
```
# Get basic issue information (faster)
search_jira_issues(query="project = ABC", basic_only=True)

# Get comprehensive issue details (default)
search_jira_issues(query="project = ABC AND updated >= -7d")
```

## Logging

The server logs activity to both stderr and a rotating log file.

**Log File Locations:**
Log files are stored in OS-specific locations by default:
- **macOS**: `~/Library/Logs/mcp_jira/mcp_jira.log`
- **Linux**:
  - If running as root: `/var/log/mcp_jira/mcp_jira.log`
  - If running as non-root: `~/.local/state/mcp_jira/mcp_jira.log`
- **Windows**: `%LOCALAPPDATA%\MCPJira\mcp_jira\Logs\mcp_jira.log` (Note: `%LOCALAPPDATA%` usually resolves to `C:\Users\<username>\AppData\Local`)

**Configuration:**
Logging behavior (level, file path, rotation settings) is configured via the `config.yaml` file. See the example `config.yaml` in the "Configuration" section for details on `log_level`, `log_file_path`, `log_max_bytes`, and `log_backup_count`.

The log level can also be overridden using the `MCP_JIRA_LOG_LEVEL` environment variable. If set, this environment variable takes precedence over the `log_level` in `config.yaml`.

```bash
# Example: Set log level to DEBUG for detailed API communication
MCP_JIRA_LOG_LEVEL=DEBUG mcp_jira-server
```
Valid log levels: `DEBUG`, `INFO` (default if not specified), `WARNING`, `ERROR`, `CRITICAL`.

## Requirements

- Python 3.11 or later (< 3.13)
- Operating Systems: Linux, macOS, Windows
- Network access to JIRA instance(s)
- Valid JIRA API token(s)

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions, including:
- Setting up the development environment
- Running tests
- Contributing guidelines
- Architecture overview

## Troubleshooting

### Common Issues

**Authentication Errors**
- Verify API token is correct and hasn't expired
- Ensure email address matches JIRA account
- Check JIRA instance URL is accessible

**Field Errors**
- Use `additional_fields` for custom or optional fields
- Check field availability in your JIRA configuration
- Server gracefully ignores unavailable fields

**Markdown Conversion Issues**
- Ensure fenced code blocks use proper syntax
- Complex tables may need manual formatting
- Check logs for conversion warnings

**Connection Issues**
- Verify network connectivity to JIRA instance
- Check firewall/proxy settings
- Ensure JIRA REST API v3 is accessible

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Coding the Future with AI**
- GitHub: [codingthefuturewithai](https://github.com/codingthefuturewithai)
- Email: codingthefuturewithai@gmail.com
