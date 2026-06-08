import streamlit as st

from services.universities import (
    get_universities,
    search_universities,
    get_programs,
    compare_by_score,
)
from utils.format import format_universities
from components.compare import render_comparison_ui, render_eligible_programs

st.title("University Directory")
st.write("Browse universities, find eligible programs by score, and compare them side-by-side.")

tab1, tab2, tab3 = st.tabs(["Browse", "Find by Score", "Compare Programs"])

with tab1:
    search_q = st.text_input("Search university name...", placeholder="e.g., Universitas Indonesia")
    data = search_universities(search_q) if search_q else get_universities()
    total = data.get("total", len(data)) if isinstance(data, dict) else len(data)
    st.write(f"Showing **{total}** universities")
    st.dataframe(format_universities(data), width="stretch", hide_index=True)

with tab2:
    st.write("Find eligible programs across universities based on your target score.")
    score = st.number_input("Your Score", min_value=0.0, max_value=1000.0, value=700.0, step=10.0)
    if st.button("Find Eligible Programs", type="primary"):
        unis = compare_by_score(score)
        if unis is None:
            st.error("Failed to compare scores.")
        else:
            st.toast(f"Found eligible programs across {len(unis)} universities! 🎯")
            render_eligible_programs(unis)

with tab3:
    unis = get_universities()
    uni_options = {u["name"]: u["id"] for u in unis}
    uni_names = ["Pilih PTN"] + list(uni_options.keys())
    render_comparison_ui(uni_names, uni_options, get_programs)
