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
from mcp_jira.services.jira_service import JiraClient, JiraServiceError, convert_markdown_to_adf
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
        description="Creates a new JIRA issue.",
    )
    def create_jira_issue_tool(
        project: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        site_alias: Optional[str] = None, # To specify which JIRA site to use
    ) -> types.TextContent:
        """Wrapper around the create_jira_issue tool implementation."""
        logger.debug(
            f"create_jira_issue_tool called with project_key (from project param): {project}, "
            f"summary: {summary}, issue_type: {issue_type}, site_alias: {site_alias}"
        )
        try:
            active_site_config = get_active_jira_config(alias=site_alias, server_config=config)
            
            jira_client = JiraClient(
                url=active_site_config.url,
                email=active_site_config.email,
                api_token=active_site_config.api_token,
                cloud=active_site_config.cloud,
            )
            
            created_issue_key, issue_url = jira_tools.create_jira_issue_implementation(
                jira_client=jira_client,
                project_key=project,
                summary=summary,
                description_markdown=description, # The tool takes markdown
                issue_type=issue_type,
            )
            return types.TextContent(
                text=f"Successfully created JIRA issue: {created_issue_key}. URL: {issue_url}"
            )
        except JiraServiceError as e:
            logger.error(f"JiraServiceError in create_jira_issue_tool: {e}", exc_info=True)
            # Return an error response that MCP can understand if possible, or re-raise
            # For now, returning a simple text error message
            return types.TextContent(text=f"Error creating JIRA issue: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in create_jira_issue_tool: {e}", exc_info=True)
            return types.TextContent(text=f"An unexpected error occurred: {e}")

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