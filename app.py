import streamlit as st
from streamlit_cookies_controller import CookieController

st.set_page_config(page_title="Unicompare")

if "cookie_controller" not in st.session_state:
    st.session_state.cookie_controller = CookieController()
    
controller = st.session_state.cookie_controller
cookie_token = controller.get("token")

if "token" not in st.session_state:
    st.session_state.token = st.query_params.get("token") or cookie_token or None

if st.session_state.token and st.session_state.token != cookie_token:
    controller.set("token", st.session_state.token)
elif st.session_state.token is None and cookie_token is not None:
    controller.remove("token")


directory = st.Page("pages/directory.py", title="University Directory")
account = st.Page("pages/account.py", title="My Account")
dashboard = st.Page("pages/dashboard.py", title="Admin Dashboard")

pg = st.navigation([directory, account, dashboard])
pg.run()
