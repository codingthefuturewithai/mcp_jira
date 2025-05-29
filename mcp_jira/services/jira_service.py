"""
Service layer for interacting with the JIRA API.
This includes the JiraClient class that wraps the atlassian-python-api
and any JIRA-specific helper functions like markdown conversion.
"""

from atlassian import Jira
from typing import Dict, Any, List # Added List for markdown_to_jira which splits lines

# Custom exception for JIRA service related errors
class JiraServiceError(Exception):
    pass

# This function is now an exact replica of conduit's markdown_to_jira function
def markdown_to_jira(content: str) -> str:
    """Convert markdown content to Jira markup format.

    Handles common markdown elements and converts them to Jira's expected format:
    - Headers (# -> h1. ## -> h2. etc)
    - Lists (- or * -> -)
    - Code blocks (``` -> {code})
    - Inline code (` -> {{)
    """
    lines = content.split("\\n")
    converted_lines = []

    for line in lines:
        # Convert headers
        if line.startswith("# "):
            line = "h1. " + line[2:]
        elif line.startswith("## "):
            line = "h2. " + line[3:]
        elif line.startswith("### "):
            line = "h3. " + line[4:]

        # Convert list items (preserve existing list numbers if present)
        elif line.strip().startswith("- "):
            line = "* " + line[2:]
        elif line.strip().startswith("* "):
            line = "* " + line[2:]

        # Convert inline code
        if "`" in line:
            # Handle inline code (single backticks)
            while "`" in line:
                if line.count("`") >= 2:
                    line = line.replace("`", "{{", 1).replace("`", "}}", 1)
                else:
                    # If there's an unpaired backtick, just replace it
                    line = line.replace("`", "{{")

        converted_lines.append(line)

    return "\\n".join(converted_lines)


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
            # Restore getting description from kwargs and calling markdown_to_jira
            description_markdown = kwargs.get("description", "") 
            jira_formatted_description = "" 
            if description_markdown:
                jira_formatted_description = markdown_to_jira(description_markdown)

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
                "description": jira_formatted_description, # Use the JIRA wiki markup string from markdown_to_jira
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