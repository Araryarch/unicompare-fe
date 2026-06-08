import streamlit as st

from services.auth import login, register, get_profile

st.title("My Account")

if st.session_state.get("token"):
    st.toast("You are logged in. 🟢")
    user_data = get_profile(st.session_state.token)
    if user_data:
        st.write("### Profile Information")
        st.write(f"**Username**: {user_data.get('username')}")
        st.write(f"**Role**: {user_data.get('role', 'User')}")
    else:
        st.error("Session expired. Please log in again.")
        st.session_state.token = None
        st.query_params.clear()

    if st.button("Logout"):
        st.session_state.token = None
        st.query_params.clear()
        st.rerun()
else:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            l_username = st.text_input("Username")
            l_password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                token = login(l_username, l_password)
                if token:
                    st.session_state.token = token
                    st.query_params["token"] = token
                    st.session_state.toast_msg = "Login successful! 🎉"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

    with tab2:
        with st.form("register_form"):
            r_username = st.text_input("New Username")
            r_password = st.text_input("New Password", type="password")
            if st.form_submit_button("Register"):
                success, err = register(r_username, r_password)
                if success:
                    st.toast("Registration successful! Please login. 🎉")
                else:
                    st.error(f"Registration failed: {err}")
