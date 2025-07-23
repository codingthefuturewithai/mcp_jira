---
description: Install and configure the MCP JIRA Server for Claude Code integration
usage: /quick-setup-jira
example: /quick-setup-jira
---

# Quick Setup MCP JIRA Server

I'll help you install and configure the MCP JIRA Server to enable JIRA integration in Claude Code.

## Step 1: Check Prerequisites

First, let me verify that UV package manager is installed:

```bash
uv --version
```

If UV is not installed, I'll provide the installation command for your platform:
- **macOS/Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows**: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Step 2: Verify MCP JIRA Server Installation

Let me verify that the MCP JIRA Server package is available:

```bash
uvx --from ctf-mcp-jira ctf-mcp-jira-server --help
```

This will download the package if needed and show the available options.

## Step 3: Launch Configuration UI

I'll now launch the web-based configuration interface:

```bash
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui
```

This will open your browser with the Streamlit configuration UI at http://localhost:8501.

### Configuration Instructions:
1. **JIRA URL**: Enter your JIRA domain (e.g., "mycompany" for mycompany.atlassian.net)
2. **Email**: Enter your JIRA login email
3. **API Token**: You'll need to create one:
   - Log into your JIRA instance
   - Go to Account Settings → Security → API tokens
   - Click "Create API token"
   - Copy the token (you won't see it again!)
4. Click "Save Configuration" when done

The configuration will be saved to:
- **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`
- **Linux**: `~/.config/mcp_jira/config.yaml`
- **Windows**: `%APPDATA%\MCPJira\mcp_jira\config.yaml`

## Step 4: Add to Claude Code

Now I'll add the MCP server to Claude Code using the uvx command:

```bash
claude mcp add mcp_jira stdio "uvx --from ctf-mcp-jira ctf-mcp-jira-server"
```

This tells Claude Code to run the MCP server using uvx, which will handle downloading and running the server in an isolated environment.

## Step 5: Verify Installation

Let me verify the MCP server is properly configured:

```bash
claude mcp list
```

You should see `mcp_jira` in the list of configured servers.

## Step 6: Test JIRA Integration

The following MCP tools are now available:
- `mcp__mcp_jira__create_jira_issue` - Create new JIRA issues
- `mcp__mcp_jira__update_jira_issue` - Update existing issues
- `mcp__mcp_jira__search_jira_issues` - Search for issues using JQL

Would you like me to test the integration by searching for issues in one of your projects?

## ✅ Setup Complete!

The MCP JIRA Server is now installed and configured. You can use it to:
- Search JIRA issues directly from Claude Code
- Create new issues with markdown descriptions
- Update existing issues
- Work with multiple JIRA sites if configured

To use a different JIRA site than the default, add the `site_alias` parameter to any command.

**Note**: To reconfigure the server in the future, you can run:
```bash
uvx --from ctf-mcp-jira ctf-mcp-jira-server --ui
```

**Important**: Using `uvx` means the package is downloaded fresh each time, which can help avoid stale environment issues but requires an internet connection for each use.