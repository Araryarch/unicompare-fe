import streamlit as st

from services.auth import get_profile

from services.universities import (
    fetch_universities,
    fetch_programs,
    create_university,
    update_university,
    delete_university,
    create_program,
    update_program,
    delete_program,
    list_users,
)

if "toast_msg" in st.session_state:
    st.toast(st.session_state.toast_msg)
    del st.session_state.toast_msg

st.title("Admin Dashboard")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in as an administrator to access the dashboard.")
    st.stop()

user_data = get_profile(token)
if not user_data or user_data.get("role") != "admin":
    st.error("Access Denied: You must be an administrator to view this page.")
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
                st.session_state.toast_msg = "University added"
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
                st.session_state.toast_msg = "Updated successfully"
                st.rerun()
            else:
                st.error(err)


@st.dialog("Add Program")
def add_program_dialog(uni_id):
    with st.form(f"add_prog_{uni_id}"):
        name = st.text_input("Program Name")
        degree = st.text_input("Degree (e.g. S1, S2)")
        score = st.number_input("Score", min_value=0.0, max_value=1000.0, step=0.1)
        if st.form_submit_button("Submit", type="primary"):
            if not name or not degree:
                st.error("Name and Degree are required.")
            else:
                success, err = create_program(token, uni_id, name, score, degree)
                if success:
                    st.session_state.toast_msg = "Program added"
                    st.rerun()
                else:
                    st.error(err)


@st.dialog("Edit Program")
def edit_program_dialog(uni_id, pid, current_name, current_degree, current_score):
    with st.form(f"edit_prog_{uni_id}_{pid}"):
        name = st.text_input("Program Name", value=current_name)
        degree = st.text_input("Degree", value=current_degree)
        score = st.number_input("Score", value=float(current_score), step=0.1)
        if st.form_submit_button("Save", type="primary"):
            if not name or not degree:
                st.error("Name and Degree are required.")
            else:
                success, err = update_program(token, uni_id, pid, name, score, degree)
                if success:
                    st.session_state.toast_msg = "Program updated"
                    st.rerun()
                else:
                    st.error(err)


tab1, tab2 = st.tabs(["Universities & Programs", "Users List"])

with tab1:
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.subheader("Universities & Programs")
    uni_search = col2.text_input("Cari PTN", placeholder="Search by name...", label_visibility="collapsed")
    if col3.button("Add University", width="stretch"):
        add_uni_dialog()

    unis = fetch_universities()
    if uni_search:
        q = uni_search.lower().strip()
        unis = [u for u in unis if q in u.get("name", "").lower() or q in u.get("id", "").lower()]

    if not unis:
        st.info("No universities found." if not uni_search else f"No universities matching '{uni_search}'.")
    else:
        st.caption(f"Showing {len(unis)} university/universities")
        for uni in unis:
            uid = uni["id"]
            with st.expander(f"**{uni.get('name')}** ({uid})"):
                head_col, btn_col1, btn_col2 = st.columns([6, 2, 2], vertical_alignment="center")
                head_col.markdown(f"#### {uni.get('name')}")
                if btn_col1.button("Edit Name", key=f"edit_{uid}", width="stretch"):
                    edit_uni_dialog(uid, uni["name"])
                if btn_col2.button("Delete", key=f"del_{uid}", type="primary", width="stretch"):
                    success, err = delete_university(token, uid)
                    if success:
                        st.session_state.toast_msg = f"Deleted {uid}"
                        st.rerun()
                    else:
                        st.error(err)
                st.divider()

                programs = fetch_programs(uid)
                prog_search = st.text_input(
                    "Cari program", placeholder="Filter programs...",
                    key=f"prog_search_{uid}", label_visibility="collapsed",
                )
                if prog_search:
                    q = prog_search.lower().strip()
                    programs = [p for p in programs if q in p.get("name", "").lower()]

                st.markdown(f"**Programs** ({len(programs)})")
                if st.button("Add Program", key=f"add_prog_{uid}", width="stretch"):
                    add_program_dialog(uid)

                if not programs:
                    st.info("No programs." if not prog_search else f"No programs matching '{prog_search}'.")
                else:
                    for prog in programs:
                        pid = prog.get("id") or prog.get("_id")
                        name = prog.get("name", "-")
                        cur_degree = prog.get("degree", "-")
                        cur_score = float(prog.get("score", 0))

                        col_a, col_b, col_c, col_d, col_e = st.columns([2, 1.5, 1, 1, 1], vertical_alignment="center")
                        col_a.markdown(f"**{name}**")
                        col_b.text_input(
                            "Degree", value=cur_degree,
                            key=f"deg_{uid}_{pid}", label_visibility="collapsed",
                        )
                        col_c.number_input(
                            "Score", value=cur_score, step=0.1,
                            key=f"score_{uid}_{pid}", label_visibility="collapsed",
                        )
                        if col_d.button("Edit", key=f"edit_prog_{uid}_{pid}"):
                            edit_program_dialog(uid, pid, name, cur_degree, cur_score)
                        if col_e.button("Delete", key=f"del_prog_{uid}_{pid}"):
                            success, err = delete_program(token, uid, pid)
                            if success:
                                st.session_state.toast_msg = "Program deleted"
                                st.rerun()
                            else:
                                st.error(err)

                    if st.button("Save All Changes", key=f"save_{uid}", type="primary", width="stretch"):
                        ok = True
                        for prog in programs:
                            pid = prog.get("id") or prog.get("_id")
                            p_name = prog.get("name", "-")
                            p_deg = st.session_state.get(f"deg_{uid}_{pid}", prog.get("degree", "-"))
                            p_score = st.session_state.get(f"score_{uid}_{pid}", float(prog.get("score", 0)))
                            s, err = update_program(token, uid, pid, p_name, float(p_score), p_deg)
                            if not s:
                                st.error(f"Failed to update {p_name}: {err}")
                                ok = False
                        if ok:
                            st.session_state.toast_msg = "All changes saved"
                            st.rerun()

with tab2:
    users = list_users(token)
    if users is None:
        st.error("Failed to fetch users or insufficient permissions.")
    else:
        user_search = st.text_input("Cari user", placeholder="Search by username...", label_visibility="collapsed")
        if user_search:
            q = user_search.lower().strip()
            users = [u for u in users if q in str(u.get("username", "")).lower()]
        st.caption(f"Showing {len(users)} user(s)")
        st.dataframe(users, width="stretch", hide_index=True)
