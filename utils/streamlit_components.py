# filename: utils/streamlit_components.py

import streamlit as st


@st.dialog("Confirm Action")
def show_confirmation_dialog(
    action_key: str,
    action_name: str,
    action_description: str = None,
    confirm_button_text: str = "Yes, Continue",
    cancel_button_text: str = "Cancel",
    warning_message: str = None,
    danger_level: str = "warning",
):
    """
    Streamlit dialog wrapper for confirmation.
    """
    # Display the confirmation message
    st.markdown(f"### Are you sure you want to {action_name}?")

    if action_description:
        st.write(action_description)

    if warning_message:
        if danger_level == "error":
            st.error(warning_message)
        elif danger_level == "warning":
            st.warning(warning_message)
        else:
            st.info(warning_message)

    # Create columns for buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            confirm_button_text, type="primary", key=f"confirm_btn_{action_key}"
        ):
            st.session_state[f"confirmation_result_{action_key}"] = True
            st.rerun()

    with col2:
        if st.button(cancel_button_text, key=f"cancel_btn_{action_key}"):
            st.session_state[f"confirmation_result_{action_key}"] = False
            st.rerun()


def confirm_action(action_key: str, action_name: str, **dialog_kwargs):
    """
    Helper function to manage confirmation state for actions.

    Args:
        action_key: Unique key for this action
        action_name: Display name for the action
        **dialog_kwargs: Additional arguments for the confirmation dialog

    Returns:
        True if action should proceed, False otherwise
    """
    confirmation_key = f"confirm_{action_key}"
    result_key = f"confirmation_result_{action_key}"

    # Check if we're waiting for confirmation
    if st.session_state.get(confirmation_key) == "pending":
        # Show the dialog
        show_confirmation_dialog(action_key, action_name, **dialog_kwargs)

        # Check if user made a choice
        if result_key in st.session_state:
            result = st.session_state[result_key]
            # Clean up session state
            del st.session_state[confirmation_key]
            del st.session_state[result_key]

            if result:
                return True
            else:
                return False

    return False


def trigger_confirmation(action_key: str):
    """
    Trigger the confirmation dialog for an action.

    Args:
        action_key: Unique key for this action
    """
    st.session_state[f"confirm_{action_key}"] = "pending"
    st.rerun()
