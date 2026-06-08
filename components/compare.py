import streamlit as st

_CARD_STYLES = {
    1: {
        "header_bg": "#0d2818",
        "label": "Pilihan Pertama",
        "selectbox_key": "ptn1_sel",
        "prog_key": "prog1_sel",
    },
    2: {
        "header_bg": "#2b0b18",
        "label": "Pilihan Kedua",
        "selectbox_key": "ptn2_sel",
        "prog_key": "prog2_sel",
    },
}


def _render_program_card(
    slot,
    index: int,
    uni_names: list[str],
    uni_options: dict,
    get_programs_fn,
):
    style = _CARD_STYLES[index]
    slot.markdown(
        f"""
        <div style='background-color: {style["header_bg"]}; padding: 10px;
                    border-radius: 8px 8px 0 0; color: white; text-align: center;
                    margin-bottom: 0px;'>
            {style["label"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with slot.container(border=True):
        ptn_name = st.selectbox(
            "Perguruan Tinggi Negeri",
            options=uni_names,
            key=style["selectbox_key"],
        )
        prog_options = ["Pilih Program Studi"]
        prog_map = {}
        if ptn_name != "Pilih PTN":
            progs = get_programs_fn(uni_options[ptn_name])
            prog_map = {p["name"]: p for p in progs}
            prog_options += list(prog_map.keys())
        prog_name = st.selectbox(
            "Program Studi",
            options=prog_options,
            key=style["prog_key"],
        )

    return ptn_name, prog_name, prog_map


def render_comparison_ui(uni_names, uni_options, get_programs_fn):
    c1, c2 = st.columns(2)

    ptn1, prog1, map1 = _render_program_card(c1, 1, uni_names, uni_options, get_programs_fn)
    ptn2, prog2, map2 = _render_program_card(c2, 2, uni_names, uni_options, get_programs_fn)

    st.write("")
    if st.button("Bandingkan Program", width="stretch", type="primary"):
        if "Pilih" in ptn1 or "Pilih" in ptn2 or "Pilih" in prog1 or "Pilih" in prog2:
            st.warning("Silakan lengkapi pilihan PTN dan Program Studi untuk kedua pilihan.")
            return

        p1 = map1[prog1]
        p2 = map2[prog2]

        st.divider()
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.subheader(p1["name"])
            st.caption(ptn1)
            st.metric("Skor Minimal", p1.get("score_text", p1.get("score")))
            st.write(f"**Tingkat:** {p1.get('degree')}")

        with col2:
            st.markdown("<h2 style='text-align: center; color: gray; margin-top: 20px;'>VS</h2>",
                        unsafe_allow_html=True)

        with col3:
            st.subheader(p2["name"])
            st.caption(ptn2)
            st.metric("Skor Minimal", p2.get("score_text", p2.get("score")))
            st.write(f"**Tingkat:** {p2.get('degree')}")


def render_eligible_programs(universities: list[dict]):
    for uni in universities:
        uni_name = uni.get("name", "-")
        progs = uni.get("eligible_programs", [])
        if not progs:
            continue
        with st.expander(f"🏫 {uni_name} ({len(progs)} Programs)", expanded=True):
            from utils.format import format_eligible_programs
            st.dataframe(format_eligible_programs(progs), width="stretch", hide_index=True)
