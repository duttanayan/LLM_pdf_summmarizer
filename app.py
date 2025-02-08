import streamlit as st
from core.auth import auth_component, initialize_auth
from core.companion import code_companion_interface
from core.analyzer import document_analyzer_interface

initialize_auth()

if not st.session_state.get("logged_in"):
    auth_component()
    st.stop()

st.sidebar.header(f"👋 Welcome, {st.session_state.current_user}")
app_mode = st.sidebar.radio("Select Mode", ["Code Companion", "Document Analyzer"])

if app_mode == "Code Companion":
    code_companion_interface()
else:
    document_analyzer_interface()

st.sidebar.button("Logout", on_click=lambda: st.session_state.clear() or st.rerun())
