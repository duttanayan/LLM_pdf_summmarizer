import streamlit as st
import hashlib
import json
import os

USER_DATA_FILE = "users.json"

def initialize_auth():
    """Initialize user data storage"""
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)

def register_user(username, password):
    """Register new user with hashed password"""
    if not os.path.exists(USER_DATA_FILE):
        initialize_auth()
    
    with open(USER_DATA_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}

    if username in users:
        return False
    
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {"password": hashed_pw}
    
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)
    
    return True

def verify_credentials(username, password):
    """Verify user credentials"""
    if not os.path.exists(USER_DATA_FILE):
        initialize_auth()
    
    with open(USER_DATA_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}

    if username not in users:
        return False
    
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    return users[username]["password"] == hashed_input

def auth_component():
    """Authentication UI component"""
    st.markdown("<h1 style='text-align: center; color: #fff;'>🔒 AI Platform Login</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("Login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if verify_credentials(username, password):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("Register"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Create Account"):
                if register_user(new_user, new_pass):
                    st.success("Account created! Please login")
                else:
                    st.error("Username already exists")
