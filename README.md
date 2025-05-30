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
  - Create and update JIRA issues with standard fields: project, summary, description, issue type.
  - Robust assignee handling: Provide an email address, and the server resolves it to the correct JIRA `accountId` for reliable assignment.
  - `additional_fields` parameter supports labels, priority, due dates, and other custom fields.
  - Graceful degradation for unavailable fields across different JIRA configurations.

- **Multi-Site Configuration**: Support for multiple JIRA instances with site aliases, configurable in `config.yaml`.
- **Comprehensive Error Handling**: Detailed error messages and logging.
- **Transport Flexibility**: Support for both stdio and SSE transport modes.

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
  "description": "# Authentication Feature\n\nImplement OAuth2 authentication:\n\n- [ ] Set up OAuth provider\n- [ ] Create login/logout endpoints\n- [ ] Add session management\n\n```python\ndef authenticate_user(token):\n    # Validates the provided token\n    return validate_token(token)\n```",
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

### update_jira_issue

Updates an existing JIRA issue. Only provided fields will be updated.

**Parameters:**
- `issue_key` (string, required): The key of the JIRA issue to update (e.g., "ACT-123").
- `summary` (string, optional): New issue summary/title.
- `description` (string, optional): New issue description in markdown format. Converts to ADF.
- `assignee` (string, optional): New assignee's email address. To unassign, provide an empty string `""` or `null` (behavior then depends on JIRA project's default assignee settings).
- `additional_fields` (object, optional): Additional JIRA fields to update, as key-value pairs (e.g., labels, priority, due date).
- `issue_type` (string, optional): New issue type (e.g., "Bug", "Story"). Note: Changing issue types can be restricted by JIRA workflow configurations.
- `site_alias` (string, optional): Which JIRA site to use (defaults to the `default_site_alias` in `config.yaml`).

**Example Usage:**
```json
{
  "issue_key": "ACT-123",
  "summary": "Implement user authentication feature (updated)",
  "description": "# Authentication Feature (Revised)\n\nOAuth2 implementation details:\n\n- [x] Set up OAuth provider\n- [ ] Create login/logout endpoints (in progress)\n- [ ] Add session management\n\n```python\ndef authenticate_user(token):\n    # Validates the provided token securely\n    return secure_validate_token(token)\n```",
  "assignee": "another.developer@example.com",
  "additional_fields": {
    "labels": ["security", "authentication", "oauth2"],
    "priority": {"name": "Highest"},
    "duedate": "2024-03-15"
  }
}
```

**Returns:**
```
Successfully updated JIRA issue: ACT-123. URL: https://your-domain.atlassian.net/browse/ACT-123
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
