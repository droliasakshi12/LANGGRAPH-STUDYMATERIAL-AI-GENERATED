import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv(dotenv_path=r"password.env")

stored_username = os.getenv("username1")
stored_password = os.getenv("password1")


input_username = st.text_input("ENTER USERNAME:")
input_password = st.text_input("ENTER PASSWORD:", type="password")

insert_button = st.button("LOGIN", use_container_width=True)

if insert_button:
    if input_username == stored_username and input_password == stored_password:
        st.success("Login successful!")
        st.session_state['register'] = True
        st.switch_page("pages/material.py")

    else:
        st.error("Incorrect username or password")
        st.session_state['register'] = False
        
        



