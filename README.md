# MCP JIRA Server

A Model Context Protocol (MCP) server that provides seamless JIRA integration for AI tools. Create and manage JIRA issues with rich markdown formatting, automatic conversion to Atlassian Document Format (ADF), and flexible field management.

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
  - Standard fields: project, summary, description, issue type, assignee
  - Additional fields via `additional_fields` parameter for labels, priority, due dates, components, etc.
  - Graceful degradation for unavailable fields across different JIRA configurations

- **Multi-Site Configuration**: Support for multiple JIRA instances with site aliases
- **Comprehensive Error Handling**: Detailed error messages and logging
- **Transport Flexibility**: Support for both stdio and SSE transport modes

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/codingthefuturewithai/mcp_jira.git
cd mcp_jira

# Create and activate a virtual environment using UV
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode using UV
uv pip install -e .
```

## Configuration

### JIRA Configuration

Create a configuration file at one of these locations:
- `~/.config/mcp-servers/mcp_jira.yaml` (Linux/macOS)
- `%APPDATA%\mcp-servers\mcp_jira.yaml` (Windows)
- Set `MCP_JIRA_CONFIG_PATH` environment variable to specify custom location

Example configuration:
```yaml
name: "MCP JIRA Server"
default_site_alias: "main"
sites:
  main:
    url: "https://your-domain.atlassian.net"
    email: "your-email@example.com"
    api_token: "your-api-token"
  staging:
    url: "https://staging-domain.atlassian.net"
    email: "your-email@example.com"
    api_token: "staging-api-token"
logging:
  level: "INFO"
  max_file_size_mb: 10
  backup_count: 5
```

### JIRA API Token

1. Log into your JIRA instance
2. Go to Account Settings → Security → API Tokens
3. Create a new API token
4. Add the token to your configuration file

## Available Tools

### create_jira_issue

Creates a new JIRA issue with markdown description converted to ADF format.

**Parameters:**
- `project` (string, required): JIRA project key (e.g., "ACT", "DEV")
- `summary` (string, required): Issue summary/title
- `description` (string, required): Issue description in markdown format
- `issue_type` (string, optional): Issue type (default: "Task")
- `site_alias` (string, optional): Which JIRA site to use (default: configured default)
- `assignee` (string, optional): Assignee email address
- `additional_fields` (object, optional): Additional JIRA fields as key-value pairs

**Example Usage:**
```json
{
  "project": "ACT",
  "summary": "Implement user authentication feature",
  "description": "# Authentication Feature\n\nImplement OAuth2 authentication:\n\n- [ ] Set up OAuth provider\n- [ ] Create login/logout endpoints\n- [ ] Add session management\n\n```python\ndef authenticate_user(token):\n    return validate_token(token)\n```",
  "assignee": "developer@example.com",
  "additional_fields": {
    "labels": ["security", "authentication"],
    "priority": {"name": "High"},
    "duedate": "2024-03-01"
  }
}
```

**Returns:**
```
Successfully created JIRA issue: ACT-123 (ID: 10001). URL: https://your-domain.atlassian.net/browse/ACT-123
```

## Usage

### Run the MCP Server

```bash
# Run with stdio transport (default)
mcp_jira-server

# Run with SSE transport
mcp_jira-server --transport sse --port 3001

# Use custom configuration file
mcp_jira-server --config /path/to/config.yaml
```

### Example: Creating a JIRA Issue

```python
# Example markdown description with rich formatting
description = """
# Bug Report: Login Page Issue

## Problem Description
Users are experiencing login failures when using special characters in passwords.

## Steps to Reproduce
1. Navigate to login page
2. Enter username with special characters: `user+test@example.com`
3. Enter password with symbols: `P@ssw0rd!`
4. Click "Login" button

## Expected vs Actual
- **Expected**: User should be logged in successfully
- **Actual**: Error message "Invalid credentials"

## Code Investigation
Found issue in validation function:

```python
def validate_password(password):
    # This regex is too restrictive
    pattern = r'^[a-zA-Z0-9]+$'  # Missing special chars!
    return re.match(pattern, password)
```

## Fix Required
Update regex pattern to allow special characters in password validation.
"""

# Create the issue
create_jira_issue(
    project="BUG",
    summary="Login fails with special characters in password",
    description=description,
    issue_type="Bug",
    assignee="security-team@example.com",
    additional_fields={
        "labels": ["security", "login", "urgent"],
        "priority": {"name": "High"},
        "components": [{"name": "Authentication"}]
    }
)
```

## Logging

The server logs all activity to both stderr and a rotating log file. Log files are stored in OS-specific locations:

- **macOS**: `~/Library/Logs/mcp-servers/mcp_jira.log`
- **Linux**: 
  - Root user: `/var/log/mcp-servers/mcp_jira.log`
  - Non-root: `~/.local/state/mcp-servers/logs/mcp_jira.log`
- **Windows**: `%USERPROFILE%\AppData\Local\mcp-servers\logs\mcp_jira.log`

Log files are automatically rotated when they reach 10MB, with up to 5 backup files kept.

Configure log level using the `LOG_LEVEL` environment variable:
```bash
# Set log level to DEBUG for detailed API communication
LOG_LEVEL=DEBUG mcp_jira-server
```

Valid log levels: DEBUG, INFO (default), WARNING, ERROR, CRITICAL

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
