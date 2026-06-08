import streamlit as st

st.set_page_config(page_title="Unicompare")

if "token" not in st.session_state:
    st.session_state.token = None

if "toast_msg" in st.session_state:
    st.toast(st.session_state.toast_msg)
    del st.session_state.toast_msg

directory = st.Page("pages/directory.py", title="University Directory")
account = st.Page("pages/account.py", title="My Account")
dashboard = st.Page("pages/dashboard.py", title="Admin Dashboard")

pg = st.navigation([directory, account, dashboard])
pg.run()
