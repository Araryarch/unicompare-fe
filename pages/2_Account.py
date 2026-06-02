import streamlit as st
import requests

BASE_URL = "https://unicompare-be.vercel.app/api"

st.title("My Account")

if st.session_state.get("token"):
    st.success("You are logged in.")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if res.status_code == 200:
        user_data = res.json()
        st.write("### Profile Information")
        st.write(f"**Username**: {user_data.get('username')}")
        st.write(f"**Role**: {user_data.get('role', 'User')}")
    else:
        st.error("Session expired. Please log in again.")
        st.session_state.token = None
        
    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
else:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            l_username = st.text_input("Username")
            l_password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
        if submit_login:
            res = requests.post(f"{BASE_URL}/auth/login", json={"username": l_username, "password": l_password})
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    with tab2:
        with st.form("register_form"):
            r_username = st.text_input("New Username")
            r_password = st.text_input("New Password", type="password")
            submit_reg = st.form_submit_button("Register")
            
        if submit_reg:
            res = requests.post(f"{BASE_URL}/auth/register", json={"username": r_username, "password": r_password})
            if res.status_code == 200:
                st.success("Registration successful! Please login.")
            else:
                st.error(f"Registration failed: {res.text}")
