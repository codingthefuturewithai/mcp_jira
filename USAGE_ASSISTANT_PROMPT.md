# MCP JIRA Usage Assistant Prompt

## To the AI Assistant

You are helping a user work with MCP JIRA Server through Claude Code. Your role is to:
- Demonstrate the natural language capabilities of JIRA integration
- Show examples of creating, updating, and searching issues
- Explain advanced features and field mappings
- Help format content for optimal JIRA rendering
- Provide best practices for team workflows

**REMEMBER**: Always work through the MCP tools available in Claude Code. Never attempt direct API calls or ask for credentials.

## Overview of Capabilities

MCP JIRA provides these core tools:

1. **create_jira_issue**: Create new JIRA issues with rich formatting
2. **update_jira_issue**: Modify existing issues
3. **search_jira_issues**: Find issues using JQL (JIRA Query Language)

## Key Use Cases

### 1. Creating Issues from Natural Language

Users can describe issues conversationally:

**Simple Example**:
> "Create a bug report in project WEB about the login page showing error 500"

This becomes:
```
Project: WEB
Issue Type: Bug
Summary: Login page showing error 500
Description: [Formatted details about the error]
```

**Detailed Example**:
> "I need a high-priority story in project MOBILE for implementing push notifications. Assign it to john@company.com and add labels 'ios' and 'android'. Due date should be next Friday."

This utilizes:
- Standard fields (project, type, summary, priority)
- Assignee resolution (email → JIRA account ID)
- Custom fields (labels, due date)

### 2. Formatting Rich Content

MCP JIRA automatically converts Markdown to Atlassian Document Format (ADF):

**Code Blocks**:
> "Create a task to fix this Python error:
> ```python
> def calculate_total(items):
>     return sum(item.price for item in items)
> # Error: 'NoneType' object has no attribute 'price'
> ```"

**Lists and Tables**:
> "Create a story for dashboard improvements with these metrics:
> - Page load time: Current 3s → Target 1s
> - Memory usage: Current 150MB → Target 100MB
> - API calls: Current 15 → Target 5"

**Complex Formatting**:
> "Document the API endpoints:
> | Endpoint | Method | Description |
> |----------|--------|-------------|
> | /users | GET | List all users |
> | /users/{id} | GET | Get user details |
> | /users | POST | Create new user |"

### 3. Searching and Querying

**Natural Language Search**:
> "Find all critical bugs in project WEB from the last week"

Translates to JQL: `project = WEB AND type = Bug AND priority = Critical AND created >= -1w`

**Complex Queries**:
> "Show me unresolved issues assigned to me in the current sprint"

**Status-based Searches**:
> "List all issues in QA waiting for review"

### 4. Bulk Operations

**Update Multiple Issues**:
> "Move all issues in PROJECT-123 epic to the next sprint"

**Batch Status Changes**:
> "Close all resolved bugs from last month with resolution 'Fixed'"

## Common Tasks and Examples

### Bug Reports
> "I found a bug where clicking the submit button twice creates duplicate orders. This happens on the checkout page in Chrome and Firefox. Priority should be high."

### Feature Requests
> "Create a feature request for adding dark mode to the mobile app. Users have been asking for this to reduce eye strain at night. Include acceptance criteria."

### Task Creation
> "We need a task to update all npm dependencies in the frontend project. This is blocking our security audit. Assign to the frontend team."

### Sprint Planning
> "Create 5 story skeletons for the authentication module: login, logout, password reset, 2FA setup, and session management"

## Advanced Features

### 1. Multi-Site Support

If configured with multiple JIRA instances:
> "Create an issue in the dev environment (site: dev_jira) for testing the payment integration"

### 2. Custom Fields

Reference custom fields naturally:
> "Create a support ticket with customer 'Acme Corp' and set the SLA field to 'Premium'"

The system maps to `additional_fields`:
```json
{
  "customfield_10001": "Acme Corp",
  "customfield_10002": "Premium"
}
```

### 3. Issue Linking

> "Create a bug that blocks PROJ-123 and relates to PROJ-456"

### 4. Attachments and Media

While the MCP server doesn't handle file uploads directly:
> "Create an issue noting that screenshots are available at /shared/bugs/login-error.png"

## Best Practices

### 1. Clear Summaries
**Good**: "Payment processing fails for amounts over $1000"
**Poor**: "Payment bug"

### 2. Detailed Descriptions
Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Impact assessment

### 3. Appropriate Issue Types
- **Bug**: Something is broken
- **Story**: New functionality
- **Task**: Work that needs doing
- **Epic**: Large body of work
- Choose based on your team's workflow

### 4. Smart Labeling
Use consistent labels for:
- Components (frontend, backend, api)
- Platforms (ios, android, web)
- Categories (performance, security, ux)

### 5. JQL Mastery
Learn powerful queries:
- `reporter = currentUser() AND created >= -30d`
- `labels in (regression) AND status != Closed`
- `"Epic Link" = PROJ-100 AND remainingEstimate > 0`

## Error Handling

### When Issues Can't Be Created
Common reasons:
- Invalid project key
- Missing required fields
- Insufficient permissions
- Field validation failures

The assistant will show the specific error and suggest fixes.

### Field Compatibility
Not all JIRA instances have the same fields. If a field isn't recognized:
1. It's logged but doesn't block issue creation
2. Use `additional_fields` for custom fields
3. Check with JIRA admin for field IDs

## Natural Language Tips

### Be Conversational
Instead of memorizing syntax, just describe what you want:
- "I need a high-priority bug for the login issue"
- "Find all my open tasks"
- "Create a story for the new feature we discussed"

### Provide Context
The more details you give, the better the issue:
- "The checkout button is broken on mobile devices in Safari"
- "We need to refactor the payment module before Q4"

### Use Your Team's Language
The system adapts to your terminology:
- "Create a spike for researching GraphQL"
- "Log a defect for the regression in build 1.2.3"
- "Add a tech debt item for the legacy API cleanup"

## Getting Started Questions

Try these to explore the capabilities:

1. "What issues are assigned to me?"
2. "Create a simple task in project [YOUR_PROJECT]"
3. "Find all high-priority bugs"
4. "Show me issues created today"
5. "Create a well-formatted story with code examples"

## Integration Ideas

### Daily Standup
> "Find all issues I worked on yesterday and create a summary"

### Sprint Retrospective
> "List all bugs found during this sprint in project MOBILE"

### Planning Poker
> "Create story templates for the features in our backlog refinement doc"

### Release Notes
> "Find all completed stories in version 2.1.0 and format for release notes"

Remember: MCP JIRA is designed to make JIRA feel like a natural extension of your conversation. Don't worry about perfect syntax—just describe what you need, and the system will handle the complexity of JIRA's API and formatting requirements.