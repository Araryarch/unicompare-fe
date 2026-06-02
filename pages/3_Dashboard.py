import streamlit as st
import requests

BASE_URL = "https://unicompare-be.vercel.app/api"

st.title("Admin Dashboard")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in as an administrator to access the dashboard.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

@st.dialog("Add New University")
def add_uni_dialog():
    with st.form("add_uni"):
        c_id = st.text_input("University ID (e.g. ui)")
        c_name = st.text_input("University Name")
        c_sources = st.text_input("Sources (comma separated, e.g. internal_mock)")
        if st.form_submit_button("Submit"):
            sources_list = [s.strip() for s in c_sources.split(",")] if c_sources else []
            res = requests.post(f"{BASE_URL}/admin/universities", headers=headers, json={"id": c_id, "name": c_name, "sources": sources_list})
            if res.status_code == 200:
                st.success("University added.")
                st.rerun()
            else:
                st.error(res.text)

@st.dialog("Edit University")
def edit_uni_dialog(uni_id, current_name):
    with st.form(f"edit_uni_{uni_id}"):
        st.write(f"Editing ID: **{uni_id}**")
        u_name = st.text_input("New Name", value=current_name)
        if st.form_submit_button("Save"):
            res = requests.put(f"{BASE_URL}/admin/universities/{uni_id}", headers=headers, json={"name": u_name})
            if res.status_code == 200:
                st.success("Updated successfully.")
                st.rerun()
            else:
                st.error(res.text)

tab1, tab2 = st.tabs(["Manage Universities", "Users List"])

with tab1:
    col1, col2 = st.columns([3, 1])
    col1.subheader("Universities List")
    if col2.button("➕ Add University", use_container_width=True):
        add_uni_dialog()
        
    res = requests.get(f"{BASE_URL}/universities")
    if res.status_code == 200:
        data = res.json()
        unis = data.get("universities", [])
        if unis:
            # Table Header
            st.write("") # spacing
            h1, h2, h3, h4 = st.columns([2, 4, 1, 1])
            h1.markdown("**ID**")
            h2.markdown("**Name**")
            h3.markdown("**Edit**")
            h4.markdown("**Delete**")
            st.divider()
            
            # Table Rows
            for uni in unis:
                c1, c2, c3, c4 = st.columns([2, 4, 1, 1])
                c1.write(uni.get("id"))
                c2.write(uni.get("name"))
                if c3.button("Edit", key=f"edit_{uni['id']}"):
                    edit_uni_dialog(uni['id'], uni['name'])
                if c4.button("Delete", key=f"del_{uni['id']}", type="primary"):
                    del_res = requests.delete(f"{BASE_URL}/admin/universities/{uni['id']}", headers=headers)
                    if del_res.status_code == 200:
                        st.success(f"Deleted {uni['id']}")
                        st.rerun()
                    else:
                        st.error(del_res.text)
                st.divider()
        else:
            st.info("No universities found.")
    else:
        st.error("Failed to load universities.")

with tab2:
    if st.button("Refresh Users"):
        res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if res.status_code == 200:
            st.dataframe(res.json(), use_container_width=True, hide_index=True)
        else:
            st.error("Failed to fetch users or insufficient permissions.")
