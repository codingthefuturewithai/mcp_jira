"""
Service layer for interacting with the JIRA API.
This includes the JiraClient class that wraps the JIRA REST API
and any JIRA-specific helper functions like markdown conversion.
"""

import json
import requests
from typing import Dict, Any, Optional, List
from mcp_jira.converters.markdown_to_adf import MarkdownToADFConverter
from mcp_jira.config import JiraSiteConfig
from mcp_jira.logging_config import logger

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

            # Only attempt to find and add assignee if a non-empty assignee string is provided
            if assignee and assignee.strip():
                account_id = self._get_user_account_id(assignee)
                if account_id:
                    converted_fields["assignee"] = {"accountId": account_id}
                else:
                    # Log a warning if a provided assignee email can't be resolved
                    logger.warning(f"CREATE_ISSUE: Assignee email '{assignee}' could not be resolved to a Jira accountId. Issue will be created unassigned.")
            else:
                logger.debug(f"CREATE_ISSUE: Skipped assignee processing because assignee_param is None or empty.")

            logger.debug(f"CREATE_ISSUE: converted_fields before merging: {converted_fields}")
            
            # Merge converted fields with any existing kwargs
            all_additional_fields = converted_fields
            if kwargs:
                all_additional_fields.update(kwargs)
            
            # Add all additional fields to issue data
            if all_additional_fields:
                issue_data["fields"].update(all_additional_fields)
            
            logger.debug(f"CREATE_ISSUE: issue_data['fields'] after merging all_additional_fields: {issue_data['fields']}")
            
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
    
    def update_issue(self, issue_key: str, summary: Optional[str] = None, 
                    description: Optional[str] = None, issue_type: Optional[str] = None, 
                    assignee: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Update a JIRA issue with provided fields.
        
        Args:
            issue_key: The issue key to update (e.g., 'ACT-123')
            summary: Optional new summary
            description: Optional new description in markdown format
            issue_type: Optional new issue type
            assignee: Optional new assignee email
            **kwargs: Additional fields to update via JIRA API
            
        Returns:
            Dict containing the updated issue information
            
        Raises:
            JiraServiceError: If issue update fails
        """
        try:
            # Build update data - only include provided (non-None) fields
            update_data = {"fields": {}}
            
            # Handle basic fields (only if provided)
            if summary is not None:
                update_data["fields"]["summary"] = summary
                
            if description is not None:
                # Reuse the same markdown-to-ADF conversion
                adf_description = self.converter.convert(description)
                update_data["fields"]["description"] = adf_description
                
            if issue_type is not None:
                update_data["fields"]["issuetype"] = {"name": issue_type}
            
            # Handle assignee (reuse same logic as create)
            converted_fields = {}

            # Only attempt to find and add assignee if a non-empty assignee string is provided for update
            if assignee and assignee.strip():
                account_id = self._get_user_account_id(assignee)
                if account_id:
                    converted_fields["assignee"] = {"accountId": account_id}
                else:
                    logger.warning(f"UPDATE_ISSUE: Assignee email '{assignee}' for update could not be resolved to a Jira accountId. Assignee will not be changed.")
            else:
                logger.debug(f"UPDATE_ISSUE: Skipped assignee processing because assignee_param is None or empty.")

            logger.debug(f"UPDATE_ISSUE: converted_fields before merging: {converted_fields}")
            
            # Merge converted fields with any existing kwargs (reuse same pattern)
            all_additional_fields = converted_fields
            if kwargs:
                # Only include non-None values from kwargs
                filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                all_additional_fields.update(filtered_kwargs)
            
            # Add all additional fields to update data
            if all_additional_fields:
                update_data["fields"].update(all_additional_fields)
            
            logger.debug(f"UPDATE_ISSUE: update_data['fields'] after merging all_additional_fields: {update_data['fields']}")
            
            # If no fields to update, return early
            if not update_data["fields"]:
                return {
                    "key": issue_key,
                    "url": f"{self.base_url}/browse/{issue_key}",
                    "message": "No fields provided for update"
                }
            
            # Make API request - PUT for update
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            response = self.session.put(url, json=update_data)
            
            if response.status_code == 204:  # Success for update (No Content)
                return {
                    "key": issue_key,
                    "url": f"{self.base_url}/browse/{issue_key}",
                    "updated_fields": list(update_data["fields"].keys())
                }
            else:
                error_msg = f"Failed to update issue: {response.status_code} - {response.text}"
                raise JiraServiceError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise JiraServiceError(f"Network error updating issue: {str(e)}")
        except Exception as e:
            raise JiraServiceError(f"Error updating issue: {str(e)}")

    def search(self, jql_query: str, max_results: int = 50, basic_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search for JIRA issues using JQL (Jira Query Language).
        
        Args:
            jql_query: JQL query string (e.g., "project = ABC AND status = 'In Progress'")
            max_results: Maximum number of results to return (default: 50)
            basic_only: If True, return only key, summary, and description (default: False)
            
        Returns:
            List of issue dictionaries containing search results
            
        Raises:
            JiraServiceError: If search fails
        """
        try:
            # Build search parameters
            if basic_only:
                # For basic_only mode, request only key, summary, and description
                fields = "key,summary,description"
            else:
                # For full mode, request all standard fields including issue links
                fields = "key,summary,status,assignee,priority,created,updated,description,issuetype,project,issuelinks"
            
            params = {
                "jql": jql_query,
                "maxResults": max_results,
                "fields": fields
            }
            
            # Make API request
            url = f"{self.base_url}/rest/api/3/search"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                issues = result.get("issues", [])
                
                # Format issues for easier consumption
                formatted_issues = []
                for issue in issues:
                    fields = issue.get("fields", {})
                    
                    # Extract and convert ADF description back to markdown for consistency
                    description = None
                    adf_description = fields.get("description")
                    if adf_description:
                        # For now, extract text content from ADF structure
                        # This is a simplified extraction - could be enhanced later
                        description = self._extract_text_from_adf(adf_description)
                    
                    if basic_only:
                        # Basic mode: only include key, summary, and description
                        formatted_issue = {
                            "key": issue.get("key"),
                            "summary": fields.get("summary"),
                            "description": description
                        }
                    else:
                        # Full mode: include all standard fields
                        formatted_issue = {
                            "key": issue.get("key"),
                            "id": issue.get("id"),
                            "summary": fields.get("summary"),
                            "description": description,
                            "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                            "assignee_email": fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None,
                            "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                            "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
                            "project": fields.get("project", {}).get("key") if fields.get("project") else None,
                            "created": fields.get("created"),
                            "updated": fields.get("updated"),
                            "url": f"{self.base_url}/browse/{issue.get('key')}"
                        }
                        
                        # Process issue links (links to other JIRA issues)
                        issue_links = []
                        if fields.get("issuelinks"):
                            for link in fields.get("issuelinks", []):
                                link_data = {
                                    "type": link.get("type", {}).get("name"),
                                    "inward": link.get("type", {}).get("inward"),
                                    "outward": link.get("type", {}).get("outward")
                                }
                                
                                # Check if it's an inward or outward link
                                if "inwardIssue" in link:
                                    linked_issue = link["inwardIssue"]
                                    link_data["direction"] = "inward"
                                    link_data["issue_key"] = linked_issue.get("key")
                                    link_data["issue_summary"] = linked_issue.get("fields", {}).get("summary")
                                    link_data["issue_status"] = linked_issue.get("fields", {}).get("status", {}).get("name")
                                elif "outwardIssue" in link:
                                    linked_issue = link["outwardIssue"]
                                    link_data["direction"] = "outward"
                                    link_data["issue_key"] = linked_issue.get("key")
                                    link_data["issue_summary"] = linked_issue.get("fields", {}).get("summary")
                                    link_data["issue_status"] = linked_issue.get("fields", {}).get("status", {}).get("name")
                                
                                issue_links.append(link_data)
                        
                        formatted_issue["issue_links"] = issue_links
                        
                        # Fetch additional data for full mode
                        issue_key = issue.get("key")
                        
                        # Get remote links
                        formatted_issue["remote_links"] = self.get_issue_remote_links(issue_key)
                        
                        # Get comments
                        formatted_issue["comments"] = self.get_issue_comments(issue_key)
                        
                        # Get worklogs
                        formatted_issue["worklogs"] = self.get_issue_worklogs(issue_key)
                    formatted_issues.append(formatted_issue)
                
                logger.debug(f"SEARCH: Found {len(formatted_issues)} issues for query: {jql_query}")
                return formatted_issues
            else:
                error_msg = f"Failed to search issues: {response.status_code} - {response.text}"
                raise JiraServiceError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise JiraServiceError(f"Network error searching issues: {str(e)}")
        except Exception as e:
            raise JiraServiceError(f"Error searching issues: {str(e)}")

    def get_issue_remote_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get remote links for a specific issue.
        
        Args:
            issue_key: The JIRA issue key (e.g., "ABC-123")
            
        Returns:
            List of remote link dictionaries
            
        Raises:
            JiraServiceError: If fetching remote links fails
        """
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/remotelink"
            response = self.session.get(url)
            
            if response.status_code == 200:
                remote_links = response.json()
                formatted_links = []
                
                for link in remote_links:
                    formatted_link = {
                        "id": link.get("id"),
                        "url": link.get("object", {}).get("url"),
                        "title": link.get("object", {}).get("title"),
                        "relationship": link.get("relationship"),
                        "application": link.get("application", {}).get("name") if link.get("application") else None
                    }
                    formatted_links.append(formatted_link)
                
                return formatted_links
            else:
                logger.warning(f"Failed to fetch remote links for {issue_key}: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching remote links: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching remote links: {str(e)}")
            return []

    def get_issue_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get comments for a specific issue.
        
        Args:
            issue_key: The JIRA issue key (e.g., "ABC-123")
            
        Returns:
            List of comment dictionaries
            
        Raises:
            JiraServiceError: If fetching comments fails
        """
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                comments = result.get("comments", [])
                formatted_comments = []
                
                for comment in comments:
                    # Extract text from body (can be plain text or ADF)
                    body_text = ""
                    body = comment.get("body")
                    if body:
                        logger.debug(f"Comment body structure: {json.dumps(body, indent=2)}")
                        if isinstance(body, str):
                            # Plain text format
                            body_text = body
                        elif isinstance(body, dict):
                            # ADF format
                            body_text = self._extract_text_from_adf(body)
                        logger.debug(f"Extracted text: '{body_text}'")
                    
                    formatted_comment = {
                        "id": comment.get("id"),
                        "author": comment.get("author", {}).get("displayName"),
                        "created": comment.get("created"),
                        "updated": comment.get("updated"),
                        "body": body_text
                    }
                    formatted_comments.append(formatted_comment)
                
                return formatted_comments
            else:
                logger.warning(f"Failed to fetch comments for {issue_key}: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching comments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return []

    def get_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get worklogs for a specific issue.
        
        Args:
            issue_key: The JIRA issue key (e.g., "ABC-123")
            
        Returns:
            List of worklog dictionaries
            
        Raises:
            JiraServiceError: If fetching worklogs fails
        """
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/worklog"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                worklogs = result.get("worklogs", [])
                formatted_worklogs = []
                
                for worklog in worklogs:
                    # Extract text from ADF comment if present
                    comment_text = ""
                    if worklog.get("comment"):
                        comment_text = self._extract_text_from_adf(worklog["comment"])
                    
                    formatted_worklog = {
                        "id": worklog.get("id"),
                        "author": worklog.get("author", {}).get("displayName"),
                        "created": worklog.get("created"),
                        "updated": worklog.get("updated"),
                        "started": worklog.get("started"),
                        "timeSpent": worklog.get("timeSpent"),
                        "timeSpentSeconds": worklog.get("timeSpentSeconds"),
                        "comment": comment_text
                    }
                    formatted_worklogs.append(formatted_worklog)
                
                return formatted_worklogs
            else:
                logger.warning(f"Failed to fetch worklogs for {issue_key}: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching worklogs: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching worklogs: {str(e)}")
            return []

    def _extract_text_from_adf(self, adf_content: Dict[str, Any]) -> str:
        """
        Extract plain text content from ADF structure for display purposes.
        This is a simplified extraction that gets the basic text content.
        """
        if not adf_content or not isinstance(adf_content, dict):
            return ""
        
        def extract_text_recursive(node):
            if not isinstance(node, dict):
                return ""
            
            text_parts = []
            
            # If this node has text directly
            if "text" in node:
                text_parts.append(node["text"])
            
            # If this node has content (nested nodes)
            if "content" in node and isinstance(node["content"], list):
                for child in node["content"]:
                    text_parts.append(extract_text_recursive(child))
            
            return " ".join(filter(None, text_parts))
        
        return extract_text_recursive(adf_content).strip()

    def _get_user_account_id(self, email_or_username: str) -> Optional[str]:
        logger.debug(f"_GET_USER_ACCOUNT_ID: Received email_or_username: '{email_or_username}'")
        """Get user account ID by email or username for Jira Cloud."""
        try:
            # Use direct REST API call since atlassian-python-api search_users is broken
            url = f"{self.base_url}/rest/api/3/user/search"
            response = self.session.get(url, params={"query": email_or_username})
            
            if response.status_code == 200:
                users = response.json()
                if users and len(users) > 0:
                    logger.debug(f"_GET_USER_ACCOUNT_ID: Resolved '{email_or_username}' to accountId '{users[0]['accountId']}'")
                    return users[0]['accountId']
                else:
                    logger.debug(f"_GET_USER_ACCOUNT_ID: User '{email_or_username}' not found or no accountId returned by JIRA API.")
            else:
                logger.warning(f"_GET_USER_ACCOUNT_ID: JIRA API search for user '{email_or_username}' failed with status {response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"_GET_USER_ACCOUNT_ID: Error looking up user {email_or_username}: {e}")
            return None

    # ... (other JiraClient methods can be added here later) ...