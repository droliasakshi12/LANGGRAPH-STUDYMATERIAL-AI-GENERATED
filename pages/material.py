import streamlit as st 

if 'register' not in st.session_state:
    st.session_state['register'] = False

if st.session_state['register'] == True:

    st.title("📚Generate Study Material")
    st.caption("✅Select below to Generate Your content")
    roadmap_button = st.button("GENERATE ROADMAP",use_container_width=True)
    outline_button = st.button("GENERATE OUTLINE",use_container_width=True)
    final_material_button = st.button("GENERATE MATERIAL",use_container_width=True)
    html_content   = st.button("GENERATE HTML",use_container_width=True)

    if roadmap_button:
        st.switch_page("pages/road_map.py")
    if outline_button:
        st.switch_page("pages/outline.py")

    if final_material_button:
        st.switch_page("pages/final_material.py")

    if  html_content:
        st.switch_page("pages/convert_html.py")



else:
    st.switch_page("password.py")
    
