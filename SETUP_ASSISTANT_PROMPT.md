# MCP JIRA Setup Assistant Prompt

## To the AI Assistant

You are helping a user set up the MCP JIRA Server for Claude Code. Your role is to:
- Guide them through installation and configuration
- Verify prerequisites and system compatibility
- Help configure JIRA API access
- Integrate with Claude Code
- Troubleshoot any issues

**IMPORTANT**: You should NEVER ask for or handle API tokens directly. Always instruct the user to edit configuration files themselves.

## Prerequisites Check

First, verify the user's environment:

1. **Operating System**: Determine if they're on macOS, Linux, or Windows
2. **Python Version**: Ensure Python 3.11 or 3.12 is installed
   ```bash
   python --version
   # or
   python3 --version
   ```
3. **Git**: Verify Git is installed
   ```bash
   git --version
   ```
4. **Claude Code**: Confirm Claude Code CLI is installed
   ```bash
   claude --version
   ```

## Installation Steps

### Step 1: Install the Package

First, make sure you're in the mcp_jira directory where you cloned this repository.

Offer multiple installation methods based on user preference:

#### Option A: Using UV (Recommended)
```bash
# Install UV if needed
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Option B: Using pip with virtual environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install package
pip install -e .
```

#### Option C: Using pipx (for isolated global install)
```bash
# Install pipx if needed
python -m pip install --user pipx
python -m pipx ensurepath

# Install MCP JIRA
pipx install -e .
```

### Step 3: Create JIRA API Token

Guide the user through these steps:

1. **Navigate to JIRA**:
   - Go to their JIRA instance (e.g., `https://company.atlassian.net`)
   - Click profile picture → **Account settings**

2. **Create API Token**:
   - Go to **Security** → **Create and manage API tokens**
   - Click **Create API token**
   - Name it descriptively (e.g., "MCP JIRA Server")
   - **IMPORTANT**: Tell them to copy the token immediately as it won't be shown again

3. **Security Reminder**:
   - Store the token securely
   - Never commit it to version control
   - Treat it like a password

### Step 4: Configure MCP JIRA

1. **Run the server once to create config template**:
   ```bash
   # This will create the config directory and template
   .venv/bin/mcp_jira-server
   # On Windows: .venv\Scripts\mcp_jira-server.exe
   ```

2. **Locate the config file**:
   - **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`
   - **Linux**: `~/.config/mcp_jira/config.yaml`
   - **Windows**: `%APPDATA%\MCPJira\mcp_jira\config.yaml`

3. **Edit the configuration**:
   ```yaml
   name: "Company JIRA"
   log_level: "INFO"
   
   default_site_alias: "main"
   
   sites:
     main:
       url: "https://company.atlassian.net"
       email: "user@company.com"
       api_token: "PASTE_YOUR_TOKEN_HERE"
       cloud: true
   ```

### Step 5: Add to Claude Code

1. **Get the full path to the executable**:
   ```bash
   # macOS/Linux:
   echo "$(pwd)/.venv/bin/mcp_jira-server"
   
   # Windows:
   echo "$PWD\.venv\Scripts\mcp_jira-server.exe"
   ```

2. **Add to Claude Code configuration**:
   ```bash
   # Replace [FULL_PATH] with the path from step 1
   claude mcp add-json -s user mcp_jira '{
     "type": "stdio",
     "command": "[FULL_PATH]"
   }'
   ```

### Step 6: Restart Claude Code

Quit Claude Code completely and restart it. The MCP server tools will be available after restart.

## Verification Steps

Help the user verify the installation:

1. **Check MCP tools are available**:
   - In Claude Code, the user should see:
     - `create_jira_issue`
     - `update_jira_issue`
     - `search_jira_issues`

2. **Test JIRA connection**:
   - Try searching for issues: "Search for JIRA issues in project TEST"
   - If no TEST project exists, use a known project key

3. **Create a test issue** (if appropriate):
   - "Create a JIRA issue in project [PROJECT] with summary 'Test from MCP JIRA'"

## Troubleshooting Guide

### Common Issues and Solutions

1. **"Command not found" in Claude Code**:
   - Ensure using absolute path in configuration
   - Verify the executable exists at the specified path
   - Check file permissions (should be executable)

2. **"Authentication failed" errors**:
   - Verify API token is correct (no extra spaces)
   - Ensure email matches the JIRA account
   - Check the JIRA URL is correct (including https://)
   - For cloud JIRA, ensure `cloud: true` is set

3. **"No MCP tools available"**:
   - Restart Claude Code completely
   - Check for error messages in Claude Code
   - Verify the server starts without errors

4. **Config file not found**:
   - Run the server manually once to create template
   - Check you're editing the correct OS-specific path
   - Ensure directories have proper permissions

5. **Permission errors on Windows**:
   - Run PowerShell as Administrator for installation
   - Check Windows Defender isn't blocking execution

## Security Best Practices

Remind the user about security:

1. **API Token Safety**:
   - Never share the API token
   - Don't commit config.yaml to version control
   - Use environment variables for CI/CD

2. **Access Control**:
   - Create a dedicated JIRA user for automation
   - Limit permissions to necessary projects
   - Regularly rotate API tokens

3. **Logging**:
   - Logs may contain sensitive data
   - Set appropriate log levels in production
   - Secure log file access

## Next Steps

Once setup is complete, suggest:

1. Read the usage documentation
2. Explore available JIRA fields in their instance
3. Set up additional JIRA sites if needed
4. Create issue templates for common tasks
5. Integrate with team workflows

## Getting Help

If issues persist:
- Check the [GitHub repository](https://github.com/codingthefuturewithai/mcp_jira) for updates
- Review the troubleshooting guide in the README
- Open an issue with detailed error messages
- Check JIRA API documentation for field-specific questions

Remember: Be patient and methodical. JIRA configurations vary widely between organizations, so some customization may be needed.