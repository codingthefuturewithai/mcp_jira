"""
Business logic for JIRA MCP tools.
These functions contain the actual implementation logic called by the MCP server endpoints.
"""

from typing import Dict, Any, Optional, List
from mcp_jira.services.jira_service import JiraClient, JiraServiceError
from mcp_jira.config import get_active_jira_config, ServerConfig


def create_jira_issue(
    project: str, 
    summary: str, 
    description: str, 
    issue_type: str = "Task", 
    site_alias: Optional[str] = None,
    assignee: Optional[str] = None,
    additional_fields: Optional[Dict[str, Any]] = None,
    server_config: Optional[ServerConfig] = None
) -> Dict[str, Any]:
    """
    Create a JIRA issue with markdown description converted to ADF.
    
    Args:
        project: Project key (e.g., 'ABC')
        summary: Issue summary/title
        description: Issue description in markdown format
        issue_type: Type of issue (default: "Task")
        site_alias: Optional site alias for multi-site configurations
        assignee: Optional assignee email address
        additional_fields: Optional dict of additional JIRA fields
        server_config: Server configuration object
        
    Returns:
        Dict containing created issue information (id, key, url)
        
    Raises:
        JiraServiceError: If issue creation fails
    """
    try:
        # Get active JIRA site configuration
        active_site_config = get_active_jira_config(alias=site_alias, server_config=server_config)
        
        # Create JiraClient instance
        jira_client = JiraClient(site_config=active_site_config)
        
        # Create the issue
        result = jira_client.create_issue(
            project_key=project,
            summary=summary,
            description=description,  # Will be converted to ADF by JiraClient
            issue_type=issue_type,
            assignee=assignee,
            **(additional_fields or {})
        )
        
        return result
        
    except JiraServiceError:
        # Re-raise JiraServiceError as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise JiraServiceError(f"Unexpected error creating JIRA issue: {e}")


def update_jira_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None, 
    issue_type: Optional[str] = None,
    site_alias: Optional[str] = None,
    assignee: Optional[str] = None,
    additional_fields: Optional[Dict[str, Any]] = None,
    server_config: Optional[ServerConfig] = None
) -> Dict[str, Any]:
    """
    Update an existing JIRA issue. Only provided fields will be updated.
    
    Args:
        issue_key: The issue key to update (e.g., 'ABC-123')
        summary: Optional new summary
        description: Optional new description in markdown format
        issue_type: Optional new issue type
        site_alias: Optional site alias for multi-site configurations
        assignee: Optional new assignee email address
        additional_fields: Optional dict of additional JIRA fields to update
        server_config: Server configuration object
        
    Returns:
        Dict containing updated issue information (key, updated_fields, url)
        
    Raises:
        JiraServiceError: If issue update fails
    """
    try:
        # Get active JIRA site configuration
        active_site_config = get_active_jira_config(alias=site_alias, server_config=server_config)
        
        # Create JiraClient instance
        jira_client = JiraClient(site_config=active_site_config)
        
        # Update the issue
        result = jira_client.update_issue(
            issue_key=issue_key,
            summary=summary,
            description=description,  # Will be converted to ADF by JiraClient if provided
            issue_type=issue_type,
            assignee=assignee,
            **(additional_fields or {})
        )
        
        return result
        
    except JiraServiceError:
        # Re-raise JiraServiceError as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise JiraServiceError(f"Unexpected error updating JIRA issue: {e}")


def search_jira_issues_implementation(
    query: str,
    site_alias: Optional[str] = None,
    max_results: int = 50,
    basic_only: bool = False
) -> Dict[str, Any]:
    """
    Implementation for searching JIRA issues using JQL.
    Returns the query and parameters for the JiraClient.search call.
    The site_alias is used by the calling layer for configuration resolution.
    
    Args:
        query: JQL query string
        site_alias: Optional site alias for multi-site configurations
        max_results: Maximum number of results to return (default: 50)
        basic_only: If True, return only key, summary, and description for each issue (default: False)
    """
    try:
        # Prepare search parameters for the client
        search_data = {
            "jql_query": query,
            "max_results": max_results,
            "basic_only": basic_only
        }
        
        # Note: site_alias is used by the MCP server layer for configuration resolution
        # and doesn't need to be included in the returned data
        
        return search_data

    except JiraServiceError as e:
        # Re-raise JiraServiceError to be handled by the MCP framework
        raise
    except Exception as e:
        # Catch any other unexpected errors and wrap them in JiraServiceError
        raise JiraServiceError(f"Unexpected error occurred in search_jira_issues_implementation: {e}") 