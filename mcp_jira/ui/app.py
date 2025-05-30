import streamlit as st

# UI specific modules
from mcp_jira.ui import state_manager
from mcp_jira.ui import config_io
from mcp_jira.ui import components

def main():
    st.set_page_config(
        page_title="MCP JIRA Configuration Editor",
        page_icon="⚙️",
        layout="wide",
    )

    # Display INFO/WARNING messages (e.g., from site deletion) at the top
    if 'action_feedback_message' in st.session_state and \
       st.session_state.action_feedback_message and \
       st.session_state.action_feedback_message.get("type") != "success":
        feedback = st.session_state.action_feedback_message
        message_type = feedback.get("type", "info") # Default to info if type somehow missing
        text = feedback.get("text", "Action completed.")
        if message_type == "warning":
            st.warning(text)
        # elif message_type == "error": # Errors from save_config_io are displayed directly by it
        #     st.error(text) # Unlikely to be set here for error type by other functions
        else: # Default to info for other non-success types
            st.info(text)
        del st.session_state.action_feedback_message # Clear after displaying

    # Remove old toast flags if they somehow persist (defensive cleanup)
    if st.session_state.get('show_save_success_toast'):
        del st.session_state.show_save_success_toast
    if st.session_state.get('show_delete_toast'):
        del st.session_state.show_delete_toast

    st.title("MCP JIRA Server Configuration Editor")

    state_manager.initialize_session_state() # Ensures config is loaded into session_state

    # Handle initial loading errors
    if st.session_state.config_error_message and not st.session_state.get('editable_config'):
        st.error(f"Initial Configuration Error: {st.session_state.config_error_message}")
        st.warning(
            "Could not load JIRA configuration for editing. "
            "If this is the first time, a template `config.yaml` might have been created. "
            "Please check the default configuration paths (see README.md), ensure it's valid, then refresh this page."
        )
        st.markdown("---")
        st.markdown("**Default Configuration File Locations (for reference):**")
        st.markdown("- **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`")
        st.markdown("- **Linux**: `~/.config/mcp_jira/config.yaml`")
        st.markdown("- **Windows**: `%APPDATA%\\\\MCPJira\\\\mcp_jira\\\\config.yaml`")
        return 

    if not st.session_state.get('editable_config'):
        st.error("Configuration could not be loaded or is not available in session state. Please check logs or the config file and refresh.")
        return

    # --- Main UI Rendering using components ---
    editable_config = st.session_state.editable_config
    loaded_path = st.session_state.get('loaded_config_path', "Not identified")
    
    st.info(f"**Editing configuration file:** `{loaded_path}`")

    components.render_general_settings(editable_config)
    components.render_jira_sites_editor(editable_config)

    # --- Action Buttons ---
    col_add_button, _ = st.columns([1,6]) # Column for add button, adjust ratio if needed
    with col_add_button:
        if st.button("Add New JIRA Site"):
            state_manager.add_new_site_to_state() # This function now handles the rerun
            # No explicit rerun here as add_new_site_to_state should call it
    
    st.markdown("---") # Separator before save area

    # Display SUCCESS messages (typically from saving) directly above the Save button
    if 'action_feedback_message' in st.session_state and \
       st.session_state.action_feedback_message and \
       st.session_state.action_feedback_message.get("type") == "success":
        st.success(st.session_state.action_feedback_message.get("text"))
        del st.session_state.action_feedback_message # Clear after displaying

    # Save button in the main app, separated for clarity
    if st.button("Save Configuration", type="primary"):
        if config_io.save_configuration_to_file(editable_config, loaded_path):
            # Success message is now set by save_configuration_to_file in session_state
            state_manager.reset_and_reload_state() # This re-runs initialize_session_state
            st.rerun() # Rerun to display the success message and refreshed state
        # else: error messages are handled by save_configuration_to_file directly using st.error

if __name__ == "__main__":
    # Note: For the Streamlit UI to correctly find the mcp_jira package (and thus mcp_jira.config),
    # you should run it from the root of the mcp_jira project, e.g.,
    # PYTHONPATH=. streamlit run mcp_jira/ui/app.py
    # or ensure mcp_jira is installed in the environment where Streamlit is running.
    main() 