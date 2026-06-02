import streamlit as st

st.set_page_config(page_title="Unicompare")
st.title("Welcome to Unicompare")
st.write("Please select a page from the sidebar to interact with the API.")

if "token" not in st.session_state:
    st.session_state.token = None
