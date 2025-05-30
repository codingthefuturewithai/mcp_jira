# Placeholder for UI component rendering functions 

import streamlit as st
from mcp_jira.ui import state_manager # Import state_manager to call delete function

def mask_api_token(token: str) -> str:
    """
    Masks an API token for display.
    - Shows the token as is if it's 8 characters or shorter.
    - For tokens longer than 8 characters, shows the first 4,
      then a fixed number of asterisks (30), then the last 4.
    """
    if not token:
        return "********"  # Default for empty/None

    token_len = len(token)
    fixed_asterisks = "******************************" # 30 asterisks

    if token_len <= 8:
        return token
    else: # token_len > 8
        return f"{token[:4]}{fixed_asterisks}{token[-4:]}"

def render_general_settings(editable_config: dict):
    """Renders input fields for general configuration settings."""
    st.subheader("General Settings")
    editable_config['name'] = st.text_input(
        "Configuration Name", 
        value=editable_config.get('name', 'MCP Jira')
    )
    
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    current_log_level = editable_config.get('log_level', 'INFO').upper()
    current_log_level_idx = log_levels.index(current_log_level) if current_log_level in log_levels else log_levels.index("INFO")
    editable_config['log_level'] = st.selectbox(
        "Log Level", 
        options=log_levels, 
        index=current_log_level_idx
    )

    sites_list = editable_config.get('sites_list', [])
    site_aliases_options = [site.get('alias', '') for site in sites_list if site.get('alias', '').strip()]
    current_default_alias = editable_config.get('default_site_alias', '')

    if not site_aliases_options:
        editable_config['default_site_alias'] = st.text_input(
             "Default JIRA Site Alias (No sites defined yet)", 
             value=current_default_alias,
             help="Add and name sites below, then select a default.",
             disabled=True
        )
    else:
        default_alias_idx = site_aliases_options.index(current_default_alias) if current_default_alias in site_aliases_options else 0
        if not current_default_alias and site_aliases_options:
             editable_config['default_site_alias'] = site_aliases_options[0]
        
        editable_config['default_site_alias'] = st.selectbox(
            "Default JIRA Site Alias", 
            options=site_aliases_options, 
            index=default_alias_idx,
            help="Select the default JIRA connection to use."
        )
    st.markdown("---")

def render_single_site_form(site_dict: dict, is_default_site: bool, site_index: int):
    """Renders the input form for a single JIRA site using its ui_id for keys."""
    ui_id = site_dict['ui_id']
    alias_for_display = site_dict.get('alias', f'Site {site_index + 1}')
    expander_label = f"Site: {alias_for_display} {'(Default)' if is_default_site else ''}"
    
    with st.expander(expander_label, expanded=True):
        # Use columns for layout: one for inputs, one for delete button
        col1, col2 = st.columns([4, 1]) # Adjust ratio as needed
        
        with col1:
            site_dict['alias'] = st.text_input(
                "Site Alias", 
                value=site_dict.get('alias', ''), 
                key=f"alias_{ui_id}",
                help="Unique identifier for this JIRA site configuration (e.g., prod_jira, dev_env)."
            )
            site_dict['url'] = st.text_input("Site URL", value=site_dict.get('url', ''), key=f"url_{ui_id}")
            site_dict['email'] = st.text_input("Email", value=site_dict.get('email', ''), key=f"email_{ui_id}")
            site_dict['api_token'] = st.text_input("API Token", value=site_dict.get('api_token', ''), key=f"token_{ui_id}", type="password") 
            site_dict['cloud'] = st.checkbox("JIRA Cloud", value=site_dict.get('cloud', True), key=f"cloud_{ui_id}")

        with col2: 
            st.write("\n") # Add some spacing above the button
            st.write("\n") 
            if st.button("Delete Site", key=f"delete_{ui_id}", type="secondary", help=f"Remove the '{alias_for_display}' site configuration."):
                state_manager.delete_site_from_state(ui_id)
                # delete_site_from_state handles the rerun, so no explicit st.rerun() here.

def render_jira_sites_editor(editable_config: dict):
    """Renders the editor for all JIRA sites."""
    st.subheader("JIRA Site Details")
    sites_list = editable_config.get('sites_list', [])
    default_site_alias = editable_config.get('default_site_alias', '')

    if not sites_list:
        st.info("No JIRA sites configured. Click \"Add New JIRA Site\" to begin.")

    for idx, site_dict_item in enumerate(sites_list):
        is_default = (site_dict_item.get('alias', '') == default_site_alias and default_site_alias != '')
        render_single_site_form(site_dict_item, is_default, idx)
    
    st.markdown("---") 