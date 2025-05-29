"""
Implementation logic for JIRA MCP tools.
Functions here are called by the tool wrappers in server/app.py.
"""

from typing import Dict, Any
from mcp_jira.services.jira_service import JiraClient, JiraServiceError

def create_jira_issue_implementation(
    jira_client: JiraClient, 
    project_key: str, 
    summary: str, 
    description_markdown: str,
    issue_type: str
) -> tuple[str, str]:
    """
    Calls the JiraClient to create an issue, aligning with conduit's **kwargs approach for the client.

    Args:
        jira_client: An initialized instance of JiraClient.
        project_key: The JIRA project key.
        summary: The issue summary.
        description_markdown: The issue description (Markdown).
        issue_type: The type of issue.

    Returns:
        A tuple containing the created issue key and its browseable URL.

    Raises:
        JiraServiceError: If the underlying client call fails.
    """
    try:
        # Prepare data in the format expected by JiraClient.create_issue(**kwargs)
        # which mirrors conduit's `fields` structure internally.
        issue_data = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description_markdown, # The client will call markdown_to_jira on this
            "issuetype": {"name": issue_type} # Pass as a dict with name, like conduit
        }
        
        created_issue_response = jira_client.create_issue(**issue_data)
        
        issue_key = created_issue_response.get('key')
        if not issue_key:
            raise JiraServiceError("Issue created, but no 'key' found in JIRA response.")

        # Construct browseable URL (common pattern, requires client's URL)
        # The client.jira.url might be the base API URL, ensure it's the browseable one.
        # Assuming client.jira.url is the base (e.g., https://instance.atlassian.net)
        browse_url = f"{jira_client.jira.url}/browse/{issue_key}"

        return issue_key, browse_url

    except JiraServiceError: # Explicitly re-raise to indicate it's an expected error type
        raise
    except Exception as e: # Catch any other unexpected error and wrap it
        # Add more context if possible
        err_msg = f"An unexpected error occurred in create_jira_issue_implementation: {str(e)}"
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
            err_msg += f" - Response: {e.response.text}"
        raise JiraServiceError(err_msg)

# Future JIRA tool implementations (e.g., search, update) would go here.
# def search_jira_issues_implementation(jira_client: JiraClient, jql_query: str) -> List[Dict[str,Any]]:
#     # ...
#     pass 