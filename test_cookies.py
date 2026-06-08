import streamlit as st
from streamlit_cookies_controller import CookieController

st.write("Testing cookies")
controller = CookieController()

if st.button("Set Cookie"):
    controller.set("my_token", "hello_world")
    st.write("Cookie set!")

if st.button("Get Cookie"):
    val = controller.get("my_token")
    st.write("Cookie value:", val)
