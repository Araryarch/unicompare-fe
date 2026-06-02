import streamlit as st
import requests

BASE_URL = "https://unicompare-be.vercel.app/api"

@st.cache_data
def get_universities():
    res = requests.get(f"{BASE_URL}/universities")
    if res.status_code == 200:
        data = res.json()
        return data.get("universities", [])
    return []

@st.cache_data
def get_programs(uni_id):
    if not uni_id: return []
    res = requests.get(f"{BASE_URL}/universities/{uni_id}")
    if res.status_code == 200:
        return res.json().get("programs", [])
    return []

def format_universities(data):
    if isinstance(data, dict) and "universities" in data:
        data = data["universities"]
    if not isinstance(data, list):
        return data
    formatted = []
    for uni in data:
        formatted.append({
            "University": uni.get("name", "-"),
            "Programs": uni.get("program_count", 0)
        })
    return formatted

st.title("University Directory")
st.write("Browse universities, find eligible programs by score, and compare them side-by-side.")

tab1, tab2, tab3 = st.tabs(["Browse", "Find by Score", "Compare Programs"])

with tab1:
    search_q = st.text_input("Search university name...", placeholder="e.g., Universitas Indonesia")
    if search_q:
        res = requests.get(f"{BASE_URL}/universities/search", params={"q": search_q})
    else:
        res = requests.get(f"{BASE_URL}/universities")
        
    if res.status_code == 200:
        data = res.json()
        total = data.get("total", 0) if isinstance(data, dict) else len(data)
        st.write(f"Showing **{total}** universities")
        st.dataframe(format_universities(data), use_container_width=True, hide_index=True)
    else:
        st.error("Failed to fetch universities.")

with tab2:
    st.write("Find eligible programs across universities based on your target score.")
    score = st.number_input("Your Score", min_value=0.0, max_value=1000.0, value=700.0, step=10.0)
    if st.button("Find Eligible Programs", type="primary"):
        res = requests.get(f"{BASE_URL}/compare", params={"score": score})
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict) and "universities" in data:
                unis = data["universities"]
            else:
                unis = data if isinstance(data, list) else []
                
            total_eligible = len(unis)
            st.success(f"Found eligible programs across {total_eligible} universities!")
            
            for uni in unis:
                uni_name = uni.get("name", "-")
                progs = uni.get("eligible_programs", [])
                if progs:
                    # Tampilkan tabel terpisah per universitas
                    with st.expander(f"🏫 {uni_name} ({len(progs)} Programs)", expanded=True):
                        formatted_progs = []
                        for p in progs:
                            formatted_progs.append({
                                "Program": p.get("name", "-"),
                                "Degree": p.get("degree", "-"),
                                "Min Score": p.get("score", "-")
                            })
                        st.dataframe(formatted_progs, use_container_width=True, hide_index=True)
        else:
            st.error("Failed to compare scores.")

with tab3:
    unis = get_universities()
    uni_options = {u["name"]: u["id"] for u in unis}
    uni_names = ["Pilih PTN"] + list(uni_options.keys())

    # Card 1
    st.markdown("""
        <div style='background-color: #0d2818; padding: 10px; border-radius: 8px 8px 0 0; color: white; text-align: center; margin-bottom: 0px;'>
            Pilihan Pertama
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        ptn1_name = st.selectbox("Perguruan Tinggi Negeri", options=uni_names, key="ptn1_sel")
        prog1_options = ["Pilih Program Studi"]
        prog1_map = {}
        if ptn1_name != "Pilih PTN":
            progs1 = get_programs(uni_options[ptn1_name])
            prog1_map = {p["name"]: p for p in progs1}
            prog1_options += list(prog1_map.keys())
        prog1_name = st.selectbox("Program Studi", options=prog1_options, key="prog1_sel")

    st.write("")

    # Card 2
    st.markdown("""
        <div style='background-color: #2b0b18; padding: 10px; border-radius: 8px 8px 0 0; color: white; text-align: center; margin-bottom: 0px;'>
            Pilihan Kedua
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        ptn2_name = st.selectbox("Perguruan Tinggi Negeri", options=uni_names, key="ptn2_sel")
        prog2_options = ["Pilih Program Studi"]
        prog2_map = {}
        if ptn2_name != "Pilih PTN":
            progs2 = get_programs(uni_options[ptn2_name])
            prog2_map = {p["name"]: p for p in progs2}
            prog2_options += list(prog2_map.keys())
        prog2_name = st.selectbox("Program Studi", options=prog2_options, key="prog2_sel")

    st.write("")
    if st.button("Bandingkan Program", use_container_width=True, type="primary"):
        if ptn1_name == "Pilih PTN" or ptn2_name == "Pilih PTN" or prog1_name == "Pilih Program Studi" or prog2_name == "Pilih Program Studi":
            st.warning("Silakan lengkapi pilihan PTN dan Program Studi untuk kedua pilihan.")
        else:
            p1 = prog1_map[prog1_name]
            p2 = prog2_map[prog2_name]
            
            st.divider()
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.subheader(p1["name"])
                st.caption(ptn1_name)
                st.metric("Skor Minimal", p1.get("score_text", p1.get("score")))
                st.write(f"**Tingkat:** {p1.get('degree')}")
            
            with c2:
                st.markdown("<h2 style='text-align: center; color: gray; margin-top: 20px;'>VS</h2>", unsafe_allow_html=True)
                
            with c3:
                st.subheader(p2["name"])
                st.caption(ptn2_name)
                st.metric("Skor Minimal", p2.get("score_text", p2.get("score")))
                st.write(f"**Tingkat:** {p2.get('degree')}")
