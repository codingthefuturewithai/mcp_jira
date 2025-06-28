"""MCP server implementation with Echo tool"""

import asyncio
import click
import sys # Ensure sys is imported for sys.exit
from typing import Optional, List, Dict, Any

from mcp import types
from mcp.server.fastmcp import FastMCP

from mcp_jira.config import ServerConfig, JiraSiteConfig, load_config, ConfigurationError, get_active_jira_config
from mcp_jira.logging_config import setup_logging, logger
from mcp_jira.tools.echo import echo
from mcp_jira.services.jira_service import JiraClient, JiraServiceError
from mcp_jira.tools import jira_tools


def create_mcp_server(config: Optional[ServerConfig] = None) -> FastMCP:
    """Create and configure the MCP server instance"""
    if config is None:
        # This will load default config (env var or platformdirs, creating one if necessary)
        config = load_config() 
    
    # Set up logging first, using the loaded (or passed) config
    setup_logging(config) # Pass the config object to setup_logging
    
    logger.info(f"Creating FastMCP server named: {config.name}")
    logger.info(f"Configuration loaded from: {config.loaded_config_path}")
    logger.info(f"Default JIRA site alias: {config.default_site_alias}")
    logger.info(f"Available JIRA sites: {list(config.sites.keys())}")

    mcp_server = FastMCP(config.name)

    # Register all tools with the server, passing the config for JIRA tools
    register_tools(mcp_server, config)

    return mcp_server


def register_tools(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Register all MCP tools with the server"""

    @mcp_server.tool(
        name="echo",
        description="Echo back the input text with optional case transformation",
    )
    def echo_tool(text: str, transform: Optional[str] = None) -> types.TextContent:
        """Wrapper around the echo tool implementation"""
        return echo(text, transform)

    # --- JIRA Tools --- 

    @mcp_server.tool(
        name="create_jira_issue",
        description="Creates a new JIRA issue from Markdown description.",
    )
    def create_jira_issue_tool(
        project: str,
        summary: str,
        description: str, # This will be Markdown input
        issue_type: str = "Task",
        site_alias: str = None,
        assignee: str = None,
        additional_fields: Dict[str, Any] = None # For future flexibility
    ) -> types.TextContent:
        """
Instruction to LLM (for Jira ADF compatibility):

When passing content that includes code, always use fenced code blocks
formatted like this Markdown example:

Example content:

This is a paragraph introducing a code block.

```python
def hello():
    print("Hello, world!")
```

Create a JIRA issue with markdown description converted to ADF.
"""
        logger.debug(
            f"create_jira_issue_tool received: project={project}, summary={summary}, "
            f"issue_type={issue_type}, site_alias={site_alias}, assignee={assignee}, additional_fields_present={additional_fields is not None}"
        )
        try:
            # Call the business logic function directly
            result = jira_tools.create_jira_issue(
                project=project,
                summary=summary,
                description=description,
                issue_type=issue_type,
                site_alias=site_alias,
                assignee=assignee,
                additional_fields=additional_fields,
                server_config=config
            )
            
            logger.info(f"JIRA issue creation result: {result}")
            
            issue_key = result.get('key')
            issue_id = result.get('id')
            browse_url = result.get('url', "N/A")

            return types.TextContent(
                type="text",
                text=f"Successfully created JIRA issue: {issue_key} (ID: {issue_id}). URL: {browse_url}",
                format="text/plain"
            )
        except JiraServiceError as e:
            logger.error(f"JiraServiceError in create_jira_issue_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"Error creating JIRA issue: {e}",
                format="text/plain"
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_jira_issue_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"An unexpected error occurred: {e}",
                format="text/plain"
            )

    @mcp_server.tool(
        name="update_jira_issue",
        description="Updates an existing JIRA issue. Only provided fields will be updated.",
    )
    def update_jira_issue_tool(
        issue_key: str,  # Required - which issue to update
        summary: str = None,
        description: str = None,  # This will be Markdown input
        issue_type: str = None,
        site_alias: str = None,
        assignee: str = None,
        additional_fields: Dict[str, Any] = None  # For future flexibility
    ) -> types.TextContent:
        """
        Update an existing JIRA issue with markdown description converted to ADF.
        Only provided (non-None) fields will be updated.
        """
        logger.debug(
            f"update_jira_issue_tool received: issue_key={issue_key}, summary={summary is not None}, "
            f"description={description is not None}, issue_type={issue_type}, site_alias={site_alias}, "
            f"assignee={assignee}, additional_fields_present={additional_fields is not None}"
        )
        try:
            # Call the business logic function directly
            result = jira_tools.update_jira_issue(
                issue_key=issue_key,
                summary=summary,
                description=description,
                issue_type=issue_type,
                site_alias=site_alias,
                assignee=assignee,
                additional_fields=additional_fields,
                server_config=config
            )
            
            logger.info(f"JIRA issue update result: {result}")

            issue_key_result = result.get('key')
            updated_fields = result.get('updated_fields', [])
            browse_url = result.get('url', "N/A")

            return types.TextContent(
                type="text",
                text=f"Successfully updated JIRA issue: {issue_key_result}. Updated fields: {', '.join(updated_fields)}. URL: {browse_url}",
                format="text/plain"
            )
        except JiraServiceError as e:
            logger.error(f"JiraServiceError in update_jira_issue_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"Error updating JIRA issue: {e}",
                format="text/plain"
            )
        except Exception as e:
            logger.error(f"Unexpected error in update_jira_issue_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"An unexpected error occurred: {e}",
                format="text/plain"
            )

    @mcp_server.tool(
        name="search_jira_issues",
        description="Search for Jira issues using JQL (Jira Query Language) syntax",
    )
    def search_jira_issues_tool(
        query: str,
        site_alias: str = None,
        basic_only: bool = False
    ) -> types.TextContent:
        """
        Search for JIRA issues using JQL syntax.
        
        Args:
            query: JQL query string (e.g., "project = ABC AND status = 'In Progress'")
            site_alias: Optional site alias for multi-site configurations
            basic_only: If True, return only key, summary, and description for each issue (default: False)
        """
        logger.debug(
            f"search_jira_issues_tool received: query='{query}', site_alias={site_alias}, basic_only={basic_only}"
        )
        try:
            # 1. Get the prepared search data (using default max_results)
            search_data = jira_tools.search_jira_issues_implementation(
                query=query,
                site_alias=site_alias,
                max_results=50,  # Default value similar to conduit
                basic_only=basic_only
            )
            logger.debug(f"Search data prepared by implementation: {search_data}")

            # 2. Get active JIRA site configuration
            active_site_config_dict = get_active_jira_config(alias=site_alias, server_config=config)
            logger.debug(f"Using JIRA site config for alias '{site_alias}'")

            # 3. Instantiate JiraClient with the specific site config
            jira_client = JiraClient(site_config=active_site_config_dict)
            logger.debug("JiraClient instantiated.")

            # 4. Call the JiraClient to search for issues
            search_results = jira_client.search(
                jql_query=search_data["jql_query"],
                max_results=search_data["max_results"],
                basic_only=search_data["basic_only"]
            )
            logger.info(f"JIRA search found {len(search_results)} issues")

            # Format results based on basic_only mode
            if not search_results:
                response_text = f"No issues found for query: {query}"
            else:
                formatted_results = []
                for issue in search_results:
                    if search_data["basic_only"]:
                        # Basic mode: show only key, summary, and description
                        issue_lines = [
                            f"**{issue['key']}**: {issue['summary']}"
                        ]
                        
                        # Include description if available
                        if issue.get('description'):
                            issue_lines.append(f"  - **Description**: {issue['description']}")
                    else:
                        # Full mode: show all available information
                        issue_lines = [
                            f"**{issue['key']}**: {issue['summary']}",
                            f"  - **Project**: {issue['project'] or 'N/A'}",
                            f"  - **Type**: {issue['issue_type'] or 'N/A'}",
                            f"  - **Status**: {issue['status'] or 'N/A'}",
                            f"  - **Priority**: {issue['priority'] or 'N/A'}",
                            f"  - **Assignee**: {issue['assignee'] or 'Unassigned'}",
                            f"  - **Created**: {issue['created'] or 'N/A'}",
                            f"  - **Updated**: {issue['updated'] or 'N/A'}",
                            f"  - **URL**: {issue['url']}"
                        ]
                        
                        # Include description if available
                        if issue.get('description'):
                            issue_lines.append(f"  - **Description**: {issue['description']}")
                        
                        # Include issue links (links to other JIRA issues)
                        if issue.get('issue_links'):
                            issue_lines.append(f"  - **Issue Links**:")
                            for link in issue['issue_links']:
                                if link.get('direction') == 'inward':
                                    issue_lines.append(f"    - {link['inward']}: {link['issue_key']} - {link['issue_summary']} ({link['issue_status']})")
                                else:
                                    issue_lines.append(f"    - {link['outward']}: {link['issue_key']} - {link['issue_summary']} ({link['issue_status']})")
                        
                        # Include remote links if available
                        if issue.get('remote_links'):
                            issue_lines.append(f"  - **Remote Links**:")
                            for link in issue['remote_links']:
                                if link.get('url') and link.get('title'):
                                    issue_lines.append(f"    - [{link['title']}]({link['url']})")
                        
                        # Include comments if available
                        if issue.get('comments'):
                            issue_lines.append(f"  - **Comments** ({len(issue['comments'])} total):")
                            # Show first 3 comments to avoid too much output
                            for comment in issue['comments'][:3]:
                                issue_lines.append(f"    - **{comment['author']}** ({comment['created']}):")
                                # Truncate long comments
                                body = comment['body'][:200] + "..." if len(comment['body']) > 200 else comment['body']
                                issue_lines.append(f"      {body}")
                            if len(issue['comments']) > 3:
                                issue_lines.append(f"    - ... and {len(issue['comments']) - 3} more comments")
                        
                        # Include worklogs if available
                        if issue.get('worklogs'):
                            total_seconds = sum(w.get('timeSpentSeconds', 0) for w in issue['worklogs'])
                            total_hours = total_seconds / 3600
                            issue_lines.append(f"  - **Worklogs** ({len(issue['worklogs'])} entries, {total_hours:.1f} hours total)")
                    
                    formatted_results.append("\n".join(issue_lines))
                
                response_text = f"Found {len(search_results)} issues:\n\n" + "\n\n".join(formatted_results)

            return types.TextContent(
                type="text",
                text=response_text,
                format="text/plain"
            )
        except JiraServiceError as e:
            logger.error(f"JiraServiceError in search_jira_issues_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"Error searching JIRA issues: {e}",
                format="text/plain"
            )
        except Exception as e:
            logger.error(f"Unexpected error in search_jira_issues_tool: {e}", exc_info=True)
            return types.TextContent(
                type="text",
                text=f"An unexpected error occurred: {e}",
                format="text/plain"
            )

    # Add other JIRA tools here, using the 'config' object to get site details

# --- Server Instantiation and CLI --- 

# Create a server instance at the module level using default config loading.
# This is the instance that `mcp dev` or `mcp_jira/__init__.py` expects.
server: FastMCP = create_mcp_server()

@click.command()
@click.option(
    "--config", "config_path_override", 
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the YAML configuration file.",
    default=None
)
@click.option(
    "--port", default=3001, show_default=True, help="Port to listen on for SSE."
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"], case_sensitive=False),
    default="stdio",
    show_default=True,
    help="Transport type (stdio or sse).",
)
def main(config_path_override: Optional[str], port: int, transport: str) -> int:
    """Run the MCP JIRA server with specified transport and configuration."""
    try:
        # Create a new server instance for this specific CLI execution,
        # configured by CLI args if provided, otherwise default.
        # This ensures that CLI arguments for config are respected for this run.
        runtime_config = load_config(config_file_path_override=config_path_override)
        cli_server = create_mcp_server(config=runtime_config)
        
        logger.info(f"Starting server with transport: {transport}, port: {port}")

        if transport == "stdio":
            asyncio.run(cli_server.run_stdio_async())
        else: # sse
            cli_server.settings.port = port # type: ignore
            asyncio.run(cli_server.run_sse_async())
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())