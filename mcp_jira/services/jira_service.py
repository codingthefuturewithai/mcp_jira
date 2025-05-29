"""
Service layer for interacting with the JIRA API.
This includes the JiraClient class that wraps the JIRA REST API
and any JIRA-specific helper functions like markdown conversion.
"""

import json
import requests
from typing import Dict, Any, Optional
from mcp_jira.converters.markdown_to_adf import MarkdownToADFConverter
from mcp_jira.config import JiraSiteConfig

# Custom exception for JIRA service related errors
class JiraServiceError(Exception):
    pass

class JiraClient:
    """Client for interacting with JIRA using direct REST API calls with proper ADF formatting."""
    
    def __init__(self, site_config: JiraSiteConfig):
        """
        Initialize the JiraClient with site configuration.
        
        Args:
            site_config: JiraSiteConfig object containing 'url', 'email' (for username), 'api_token'
        """
        self.base_url = site_config.url.rstrip('/')
        self.username = site_config.email
        self.api_token = site_config.api_token
        
        # Initialize the markdown to ADF converter
        self.converter = MarkdownToADFConverter()
        
        # Set up session for API calls
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_issue(self, project_key: str, summary: str, description: str, 
                    issue_type: str = "Task", assignee: Optional[str] = None, 
                    **kwargs) -> Dict[str, Any]:
        """
        Create a JIRA issue with markdown description converted to ADF.
        
        Args:
            project_key: Project key
            summary: Issue summary
            description: Issue description in markdown format
            issue_type: Type of issue (default: "Task")
            assignee: Optional assignee email
            **kwargs: Additional fields to pass to JIRA API
            
        Returns:
            Dict containing the created issue information
            
        Raises:
            JiraServiceError: If issue creation fails
        """
        try:
            # Convert markdown description to ADF
            adf_description = self.converter.convert(description)
            
            # Build issue data
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": adf_description,  # Pass as dict, not string
                    "issuetype": {"name": issue_type}
                }
            }
            
            # Convert dedicated parameters to additional_fields format
            converted_fields = {}
            if assignee:
                converted_fields["assignee"] = {"emailAddress": assignee}
            
            # Merge converted fields with any existing kwargs
            all_additional_fields = converted_fields
            if kwargs:
                all_additional_fields.update(kwargs)
            
            # Add all additional fields to issue data
            if all_additional_fields:
                issue_data["fields"].update(all_additional_fields)
            
            # Make API request
            url = f"{self.base_url}/rest/api/3/issue"
            response = self.session.post(url, json=issue_data)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "id": result["id"],
                    "key": result["key"],
                    "url": f"{self.base_url}/browse/{result['key']}"
                }
            else:
                error_msg = f"Failed to create issue: {response.status_code} - {response.text}"
                raise JiraServiceError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise JiraServiceError(f"Network error creating issue: {str(e)}")
        except Exception as e:
            raise JiraServiceError(f"Error creating issue: {str(e)}")
    
    # ... (other JiraClient methods can be added here later) ...