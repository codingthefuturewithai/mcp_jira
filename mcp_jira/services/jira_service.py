"""
Service layer for interacting with the JIRA API.
This includes the JiraClient class that wraps the atlassian-python-api
and any JIRA-specific helper functions like markdown conversion.
"""

from atlassian import Jira
from typing import Dict, Any, List # Added List for markdown_to_jira which splits lines

from markdown2 import markdown # Added for Markdown to HTML
from docbuilder import DocumentBuilder # Added for HTML to ADF

# Custom exception for JIRA service related errors
class JiraServiceError(Exception):
    pass

# Renamed and updated to convert Markdown to ADF via HTML
def convert_markdown_to_adf(markdown_input: str) -> Dict[str, Any]:
    """Convert markdown content to Atlassian Document Format (ADF)
    by first converting Markdown to HTML, then HTML to ADF.
    """
    if not markdown_input:
        # Return an empty ADF document if input is empty
        return DocumentBuilder().paragraph().end().build() # Or more simply: {"type": "doc", "version": 1, "content": []}

    try:
        # Add extensions for better Markdown compatibility, e.g., fenced-code-blocks
        html_output = markdown(markdown_input, extras=["fenced-code-blocks", "tables", "strike"])
        
        # Ensure DocumentBuilder is robust against potentially empty/malformed HTML from markdown2 if input is odd
        if not html_output.strip(): 
             return {"type": "doc", "version": 1, "content": []} # Handle cases where HTML is empty

        adf_document = DocumentBuilder.from_html(html_output).build()
        return adf_document
    except Exception as e:
        # Log the error and perhaps return a simple ADF paragraph with the error or fallback content
        # For now, re-raising as a JiraServiceError to make it visible
        # In a production system, might want to return a valid empty ADF or error ADF
        # print(f"Error during Markdown to ADF conversion: {e}") # Optional: for server-side logging
        raise JiraServiceError(f"Failed to convert Markdown to ADF: {e}")


class JiraClient:
    """
    Client for interacting with the JIRA API using the atlassian-python-api.
    Mirrors conduit's client structure for relevant parts.
    """
    def __init__(self, url: str, email: str, api_token: str, cloud: bool = True):
        """
        Initializes the JiraClient.
        (This __init__ remains as previously designed for mcp_jira, 
         as conduit's __init__ and connect are different and handle config loading internally)
        """
        try:
            self.jira = Jira(
                url=url,
                username=email,
                password=api_token,
                cloud=cloud # Retaining explicit cloud parameter as per mcp_jira design
            )
        except Exception as e:
            raise JiraServiceError(f"Failed to initialize Jira API client: {e}")

    # This method is now aligned with conduit's create_issue parameter handling and logic
    def create_issue(self, **kwargs) -> Dict[str, Any]:
        """
        Creates a new issue in JIRA.
        Aligned with conduit's `create` method.

        Args:
            **kwargs: Expects 'project' (as dict with 'key'), 'summary', 
                      'description' (markdown), and optionally 'issuetype' (as dict with 'name').
        
        Returns:
            A dictionary representing the created issue.

        Raises:
            JiraServiceError: If the API call fails.
        """
        try:
            description_markdown = kwargs.get("description", "") 
            adf_description = {"type": "doc", "version": 1, "content": []} # Default empty ADF
            if description_markdown:
                adf_description = convert_markdown_to_adf(description_markdown) # Call new ADF conversion

            project_arg = kwargs.get("project")
            if not isinstance(project_arg, dict) or "key" not in project_arg:
                raise JiraServiceError("Missing or malformed 'project' argument; expected a dict with 'key'.")

            summary_arg = kwargs.get("summary")
            if summary_arg is None:
                raise JiraServiceError("Missing 'summary' argument.")
            
            issuetype_name = "Task" # Default as per conduit
            issuetype_arg = kwargs.get("issuetype")
            if isinstance(issuetype_arg, dict) and "name" in issuetype_arg:
                issuetype_name = issuetype_arg["name"]
            elif isinstance(issuetype_arg, str): # Allow string for issuetype name directly
                issuetype_name = issuetype_arg


            fields = {
                "project": {"key": project_arg["key"]},
                "summary": summary_arg,
                "description": adf_description, # Use the ADF dictionary here
                "issuetype": {"name": issuetype_name},
            }
            
            created_issue = self.jira.issue_create(fields=fields)
            if not created_issue:
                raise JiraServiceError("JIRA API returned an empty response for issue creation.")
            return created_issue
        except Exception as e:
            # Preserve mcp_jira's more specific error context if possible, but ensure error is re-raised
            # if it's not a JiraServiceError already
            if isinstance(e, JiraServiceError):
                raise
            # Attempt to provide more context if available from the exception (e.g., response text)
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
                error_detail = f"{e} - {e.response.text}"

            project_key_for_error = kwargs.get("project", {}).get("key", "unknown_project")
            raise JiraServiceError(f"Failed to create JIRA issue for project '{project_key_for_error}': {error_detail}")

# Example Usage (for testing this file directly, not part of the MCP server flow)
# if __name__ == '__main__':
#     # Test markdown conversion (using the conduit version now)
#     md_text = "# This is a H1\\n## This is H2\\n* item 1\\n- item 2\\nThis has `inline code` and then `another one`."
#     jira_text = markdown_to_jira(md_text)
#     print("--- Markdown to JIRA ---")
#     print(md_text)
#     print("--- JIRA Markup ---")
#     print(jira_text)
#     print("-------------------------")

    # Test JiraClient.create_issue
    # This requires environment variables for a test JIRA instance
    # TEST_JIRA_URL, TEST_JIRA_EMAIL, TEST_JIRA_TOKEN, TEST_JIRA_PROJECT_KEY
    # import os
    # TEST_JIRA_URL = os.getenv("TEST_JIRA_URL")
    # TEST_JIRA_EMAIL = os.getenv("TEST_JIRA_EMAIL")
    # TEST_JIRA_TOKEN = os.getenv("TEST_JIRA_TOKEN")
    # TEST_JIRA_PROJECT_KEY = os.getenv("TEST_JIRA_PROJECT_KEY_REAL") # Use a real project key

    # if all([TEST_JIRA_URL, TEST_JIRA_EMAIL, TEST_JIRA_TOKEN, TEST_JIRA_PROJECT_KEY]):
    #     print(f"\\n--- Testing JiraClient.create_issue with {TEST_JIRA_URL} ---")
    #     try:
    #         client = JiraClient(url=TEST_JIRA_URL, email=TEST_JIRA_EMAIL, api_token=TEST_JIRA_TOKEN)
    #         print("JiraClient initialized.")
            
    #         test_issue_data = {
    #             "project": {"key": TEST_JIRA_PROJECT_KEY},
    #             "summary": "Test Issue from mcp_jira (Conduit Style)",
    #             "description": "## Test Description\\n* Bullet 1\\n* Bullet 2\\nThis is `inline code`.",
    #             "issuetype": {"name": "Task"} # or "Bug", "Story" etc.
    #         }
    #         print(f"Attempting to create issue with data: {test_issue_data}")
            
    #         new_issue = client.create_issue(**test_issue_data)
    #         issue_key = new_issue.get('key')
    #         issue_url = new_issue.get('self') # JIRA typically returns the API URL in 'self'
    #         if issue_key:
    #             print(f"Successfully created issue: {issue_key}")
    #             # Construct a browseable URL (common pattern)
    #             browse_url = f"{TEST_JIRA_URL}/browse/{issue_key}"
    #             print(f"Issue Browse URL: {browse_url}")
    #             print(f"API 'self' URL: {issue_url}")
    #         else:
    #             print(f"Issue created, but key not found in response: {new_issue}")

    #     except JiraServiceError as e:
    #         print(f"JiraServiceError during create_issue test: {e}")
    #     except Exception as e:
    #         print(f"Unexpected error during create_issue test: {e}")
    # else:
    #     print("\\nSkipping JiraClient.create_issue live test: Required TEST_JIRA_... environment variables not set.") 