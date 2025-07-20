# MCP JIRA Server Setup Guide

## Quick Start with AI Assistant

Copy this prompt to your AI coding assistant:

```
Please help me set up the MCP JIRA Server. I need to:
1. Install the server using the isolated uv tool method
2. Configure my JIRA API credentials
3. Add it to Claude Desktop/Code
4. Test that it's working properly
```

## Prerequisites

- Python 3.11 or 3.12
- Git
- Claude Desktop or Claude Code CLI
- JIRA account with API access

## Installation (Recommended Method)

### Step 1: Install UV Package Manager

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell as Administrator):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Install MCP JIRA Server

```bash
# Install as an isolated tool (prevents dependency conflicts)
uv tool install git+https://github.com/codingthefuturewithai/mcp_jira.git
```

The server is now available globally as `mcp_jira-server`.

### Step 3: Create JIRA API Token

1. Go to your JIRA instance (e.g., `https://yourcompany.atlassian.net`)
2. Click your profile picture → **Account settings**
3. Navigate to **Security** → **Create and manage API tokens**
4. Click **Create API token**
5. Name it "MCP JIRA Server"
6. **Copy the token immediately** (you won't see it again)

### Step 4: Configure the Server

1. Run the server once to create config template:
   ```bash
   mcp_jira-server
   ```

2. Edit the configuration file:
   - **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`
   - **Linux**: `~/.config/mcp_jira/config.yaml`
   - **Windows**: `%APPDATA%\MCPJira\mcp_jira\config.yaml`

3. Update with your details:
   ```yaml
   name: "My JIRA Server"
   log_level: "INFO"
   
   default_site_alias: "main"
   
   sites:
     main:
       url: "https://your-company.atlassian.net"
       email: "your-email@company.com"
       api_token: "your-api-token-here"
       cloud: true
   ```

### Step 5: Add to Claude Desktop

**macOS/Linux:**
```bash
claude mcp add mcp_jira stdio "$HOME/.local/share/uv/tools/mcp-jira/bin/mcp_jira-server"
```

**Windows:**
```bash
claude mcp add mcp_jira stdio "%USERPROFILE%\.local\share\uv\tools\mcp-jira\Scripts\mcp_jira-server.exe"
```

### Step 6: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

## Testing Your Setup

After restarting Claude Desktop, test with:

1. **Search for issues:**
   ```
   Search for JIRA issues in project ABC
   ```

2. **Create a test issue:**
   ```
   Create a JIRA issue in project ABC with summary "Test from MCP"
   ```

## Troubleshooting

### Installation Issues

**Dependency Conflicts:**
- The `uv tool install` method isolates the installation
- If issues persist, try uninstalling and reinstalling:
  ```bash
  uv tool uninstall mcp-jira
  uv tool install git+https://github.com/codingthefuturewithai/mcp_jira.git
  ```

**Platform-Specific:**
- **Windows**: Run PowerShell as Administrator
- **macOS**: Update certificates if SSL errors: `brew install ca-certificates`
- **Linux**: May need: `sudo apt-get install python3-dev`

### Configuration Issues

**"Authentication failed":**
- Verify API token has no extra spaces
- Ensure email matches your JIRA account
- Check URL includes `https://`
- For cloud JIRA, ensure `cloud: true`

**"Command not found":**
- Verify installation path is correct
- Check the executable exists at the specified location
- Ensure proper file permissions

### MCP Client Issues

**"No MCP tools available":**
- Restart Claude Desktop completely
- Check for error messages in Claude Desktop logs
- Verify the server starts without errors:
  ```bash
  mcp_jira-server
  ```

## Alternative Installation Methods

### Quick Test with UVX (Not Recommended for Production)
```bash
# ⚠️ WARNING: May cause dependency conflicts
uvx mcp_jira-server
```

### Development Installation
```bash
git clone https://github.com/codingthefuturewithai/mcp_jira.git
cd mcp_jira
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

## Security Best Practices

1. **Never share your API token**
2. **Don't commit config.yaml to version control**
3. **Use a dedicated JIRA user for automation**
4. **Regularly rotate API tokens**
5. **Set appropriate JIRA permissions**

## Getting Help

- [GitHub Issues](https://github.com/codingthefuturewithai/mcp_jira/issues)
- [MCP Documentation](https://modelcontextprotocol.io)
- [JIRA API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

## Advanced Configuration

### Multiple JIRA Sites

```yaml
sites:
  production:
    url: "https://prod.atlassian.net"
    email: "prod@company.com"
    api_token: "your-prod-token-here"
    cloud: true
  
  staging:
    url: "https://staging.atlassian.net"
    email: "staging@company.com"
    api_token: "your-staging-token-here"
    cloud: true

default_site_alias: "production"
```

### Custom Fields

Use `additional_fields` to set custom fields:

```python
{
  "project": "ABC",
  "summary": "Test Issue",
  "description": "Description here",
  "additional_fields": {
    "priority": {"name": "High"},
    "labels": ["mcp", "automated"],
    "duedate": "2024-12-31"
  }
}
```