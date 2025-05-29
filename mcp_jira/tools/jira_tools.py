"""
Implementation logic for JIRA MCP tools.
Functions here are called by the tool wrappers in server/app.py.
"""

from typing import Dict, Any, Optional
from mcp_jira.services.jira_service import JiraClient, JiraServiceError

def create_jira_issue_implementation(
    project: str, 
    summary: str, 
    description: str, 
    issue_type: str = "Task", 
    site_alias: Optional[str] = None,
    additional_fields: Optional[Dict[str, Any]] = None # For any other fields
) -> Dict[str, Any]:
    """
    Implementation for creating a JIRA issue. 
    The description is taken as raw Markdown and passed through.
    """
    try:
        # Initialize JiraClient (which now takes site_config from get_active_jira_config)
        # This part relies on get_active_jira_config being available and working correctly.
        # For simplicity in this function, we assume config resolution happens upstream (e.g., in the MCP tool wrapper in app.py)
        # or that JiraClient is instantiated with a pre-resolved site_config.
        # However, the MCP tool definition itself receives the site_alias.
        # The actual JiraClient instantiation will be handled by the MCP server layer using this site_alias.

        # The input description is raw Markdown and should be passed as such.
        # The JiraClient will handle conversion to ADF.
        # jira_wiki_description = convert_markdown_to_jira_wiki(description) # REMOVE THIS LINE

        # The JiraClient will be instantiated by the server framework using site_alias to get the config.
        # Here, we'd normally receive the client as an argument or it would be part of a class.
        # For this standalone function, we'll assume it's called by a part of the system 
        # that has access to the correctly configured JiraClient instance.
        
        # This function is the *implementation* called by the tool wrapper.
        # The tool wrapper in app.py will handle client instantiation.
        # So, this implementation function should expect a JiraClient instance.
        
        # Let's adjust the thought process: the client is created in app.py's tool method.
        # This implementation function should *receive* the client.
        # For now, I will proceed assuming this function will eventually be called by app.py
        # which will pass the description to the client's create_issue method.
        # The key change is that description passed to client.create_issue should be JIRA wiki markup.

        # **This function's role is primarily to prepare the arguments for the client.**
        # The actual client call happens in the MCP tool wrapper if we follow that pattern.
        # Or, if this is the final point before calling the client directly (and client is passed in):
        
        # client.create_issue(project_key=project, summary=summary, description=jira_wiki_description, issue_type=issue_type, **(additional_fields or {}))
        # Since we are returning a dictionary that will be used by client.create_issue
        # this function should return all necessary fields for the client call.
        
        issue_data = {
            "project_key": project,
            "summary": summary,
            "description": description, # Pass the raw Markdown description
            "issue_type": issue_type
        }
        if additional_fields:
            issue_data.update(additional_fields) # Add any other fields passed in
        
        # The actual JiraClient().create_issue call will be made in server/app.py using these returned details.
        return issue_data # Return the prepared data for client.create_issue

    except JiraServiceError as e:
        # Re-raise JiraServiceError to be handled by the MCP framework
        raise
    except Exception as e:
        # Catch any other unexpected errors and wrap them in JiraServiceError
        # Log the original exception here if logging is set up
        raise JiraServiceError(f"An unexpected error occurred in create_jira_issue_implementation: {e}")

# Future JIRA tool implementations (e.g., search, update) would go here.
# def search_jira_issues_implementation(jira_client: JiraClient, jql_query: str) -> List[Dict[str,Any]]:
#     # ...
#     pass 