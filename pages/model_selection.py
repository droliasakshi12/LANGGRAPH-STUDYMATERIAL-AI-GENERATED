import streamlit as st
from langchain_openai import ChatOpenAI
import json
import os

if 'register' not in st.session_state:
    st.session_state['register'] = False

if st.session_state['register'] == True:

    # loading the json model file
    model_file = "model.json"

    model_list = [
        "gpt-4.1-nano",
        "gpt-4.1-mini",
        "gpt-5-nano",
        "gpt-4o-mini-search-preview"]

    # creating a function load model

    def load_model():
        # used to find if file exists on the device or not
        if os.path.exists(model_file):
            # reading the json file
            with open(model_file, 'r') as file:
                try:
                    # json.load is used to read the data from json file
                    data = json.load(file)
                    return data

                except json.JSONDecodeError:
                    return model_list
        else:
            return model_list

    # saving the data in model file

    def save_model(model_input):
        # using the json file to insert the new data

        with open(model_file, "w") as file:
            # dump is used to insert the data into json file
            json.dump(model_input, file, indent=4)

    def list_model():
        if 'model_list' not in st.session_state:
            # getting the data from file
            st.session_state['model_list'] = load_model()

    def inserting_new_model():

        # inserting new model
        model_input = st.text_input("ENTER THE MODEL NAME")
        model_input = model_input.replace('"', '').replace("/", '')
        st.caption("make sure to enter the full name of the model")

        # creating a button to add new model
        insert_model = st.button("INSERT NEW MODEL", use_container_width=True)

        if insert_model:
            if model_input.strip() == "":
                st.error("model input cannot be empty !!")

            elif model_input in st.session_state['model_list']:
                st.error("model already exists!!")

            else:

                st.session_state['model_list'].append(model_input)
                save_model(st.session_state['model_list'])
                st.success(f"MODEL : {model_input} ADDED!!")

    def selecting_model():

        list_model()
        model_selection = st.sidebar.radio(
            label="SELECT MODEL", options=st.session_state['model_list'])
        st.success(f"MODEL : {model_selection} SELECTED")

        return model_selection

    list_model()
    inserting_new_model()
    selecting_model()


else:
    st.switch_page("password.py")
