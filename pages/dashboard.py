import streamlit as st

from services.universities import (
    fetch_universities,
    create_university,
    update_university,
    delete_university,
    list_users,
)

st.title("Admin Dashboard")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in as an administrator to access the dashboard.")
    st.stop()


@st.dialog("Add New University")
def add_uni_dialog():
    with st.form("add_uni"):
        c_id = st.text_input("University ID (e.g. ui)")
        c_name = st.text_input("University Name")
        c_sources = st.text_input("Sources (comma separated, e.g. internal_mock)")
        if st.form_submit_button("Submit"):
            sources_list = [s.strip() for s in c_sources.split(",")] if c_sources else []
            success, err = create_university(token, c_id, c_name, sources_list)
            if success:
                st.success("University added.")
                st.rerun()
            else:
                st.error(err)


@st.dialog("Edit University")
def edit_uni_dialog(uni_id, current_name):
    with st.form(f"edit_uni_{uni_id}"):
        st.write(f"Editing ID: **{uni_id}**")
        u_name = st.text_input("New Name", value=current_name)
        if st.form_submit_button("Save"):
            success, err = update_university(token, uni_id, u_name)
            if success:
                st.success("Updated successfully.")
                st.rerun()
            else:
                st.error(err)


tab1, tab2 = st.tabs(["Manage Universities", "Users List"])

with tab1:
    col1, col2 = st.columns([3, 1])
    col1.subheader("Universities List")
    if col2.button("➕ Add University", use_container_width=True):
        add_uni_dialog()

    unis = fetch_universities()
    if unis:
        h1, h2, h3, h4 = st.columns([2, 4, 1, 1])
        h1.markdown("**ID**")
        h2.markdown("**Name**")
        h3.markdown("**Edit**")
        h4.markdown("**Delete**")
        st.divider()

        for uni in unis:
            c1, c2, c3, c4 = st.columns([2, 4, 1, 1])
            c1.write(uni.get("id"))
            c2.write(uni.get("name"))
            if c3.button("Edit", key=f"edit_{uni['id']}"):
                edit_uni_dialog(uni["id"], uni["name"])
            if c4.button("Delete", key=f"del_{uni['id']}", type="primary"):
                success, err = delete_university(token, uni["id"])
                if success:
                    st.success(f"Deleted {uni['id']}")
                    st.rerun()
                else:
                    st.error(err)
            st.divider()
    else:
        st.info("No universities found.")

with tab2:
    if st.button("Refresh Users"):
        users = list_users(token)
        if users is not None:
            st.table(users)
        else:
            st.error("Failed to fetch users or insufficient permissions.")
