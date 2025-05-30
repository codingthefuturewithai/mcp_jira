import streamlit as st
from mcp_jira.config import load_config, ServerConfig, JiraSiteConfig, ConfigurationError
import os

# Helper function to mask API tokens (from Conduit example, adapted)
def mask_api_token(token: str) -> str:
    """
    Masks an API token.
    - Shows the token as is if it's 8 characters or shorter.
    - For tokens longer than 8 characters, shows the first 4,
      then a fixed number of asterisks (5), then the last 4.
    """
    if not token:
        return "********"  # Default for empty/None

    token_len = len(token)
    fixed_asterisks = "******************************" # 30 asterisks

    if token_len <= 8:
        # If the token is 8 characters or less, show it as is.
        # Masking would offer little benefit or make it confusing.
        return token
    else: # token_len > 8
        # Show first 4, fixed asterisks, and last 4.
        return f"{token[:4]}{fixed_asterisks}{token[-4:]}"

def main():
    st.set_page_config(
        page_title="MCP JIRA Configuration Viewer",
        page_icon="⚙️", # Changed icon for fun
        layout="wide",
    )

    st.title("MCP JIRA Server Configuration")
    st.markdown("---_Read-only view of the active JIRA server configuration_---")

    try:
        # Load configuration using the server's own logic
        # This will also handle template creation if config doesn't exist
        config_data: ServerConfig = load_config()

        st.info(f"**Configuration loaded from:** `{config_data.loaded_config_path}`")
        
        # Display a warning if the loaded config is the template and might need editing.
        # We infer this if the default_site_alias points to the template's placeholder.
        if config_data.default_site_alias == "my_primary_jira" and \
           any(site.api_token == "YOUR_ATLASSIAN_API_TOKEN" for site in config_data.sites.values()):
            st.warning(
                "It appears you are viewing the default template configuration. "
                "Please edit the `config.yaml` file with your actual JIRA site details for the server to function correctly."
            )


        st.subheader("General Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Configuration Name", value=config_data.name, disabled=True)
        with col2:
            st.text_input("Default JIRA Site Alias", value=config_data.default_site_alias, disabled=True)
        st.text_input("Log Level", value=config_data.log_level, disabled=True)


        st.subheader("JIRA Site Details")
        if not config_data.sites:
            st.info("No JIRA sites are configured. Please edit your `config.yaml`.")
        else:
            for alias, site in config_data.sites.items():
                is_default = " (Default)" if alias == config_data.default_site_alias else ""
                with st.expander(f"Site: {alias}{is_default}", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.text_input("Site URL", value=site.url, key=f"url_{alias}", disabled=True)
                        st.text_input("Email", value=site.email, key=f"email_{alias}", disabled=True)
                    with c2:
                        st.text_input("API Token", value=mask_api_token(site.api_token), key=f"token_{alias}", disabled=True)
                        st.checkbox("JIRA Cloud", value=site.cloud, key=f"cloud_{alias}", disabled=True)
        
        st.markdown("--- ")
        st.caption("To modify the configuration, please edit the `config.yaml` file directly at the path shown above.")


    except ConfigurationError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.warning(
            "Could not load JIRA configuration. "
            "If this is the first time running the server or UI, a template `config.yaml` might have been created. "
            "Please check the default configuration paths for your OS (see README.md) and fill in your JIRA details."
        )
        # Attempt to display default paths mentioned in README for user convenience
        st.markdown("**Default Configuration File Locations:**")
        st.markdown("- **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`")
        st.markdown("- **Linux**: `~/.config/mcp_jira/config.yaml`")
        st.markdown("- **Windows**: `%APPDATA%\\MCPJira\\mcp_jira\\config.yaml` (e.g., `C:\\Users\\<username>\\AppData\\Roaming\\MCPJira\\mcp_jira\\config.yaml`)")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.exception(e) # Provides a more detailed traceback for unexpected errors

if __name__ == "__main__":
    # Note: For the Streamlit UI to correctly find the mcp_jira package (and thus mcp_jira.config),
    # you should run it from the root of the mcp_jira project, e.g.,
    # PYTHONPATH=. streamlit run mcp_jira/ui/app.py
    # or ensure mcp_jira is installed in the environment where Streamlit is running.
    main() 