from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import streamlit as st
from docx import Document
import streamlit.components.v1 as component
from pages.model_selection import selecting_model
import time 

if 'register' not in st.session_state:
    st.session_state['register'] = False

if st.session_state['register'] == True:

    load_dotenv(dotenv_path=r"my_api_key.env")
    os.environ["OPENAI_API_KEY"] = os.getenv("openai_api")
    st.title("🖼️HTML Generation")
    st.space("small")
    models = selecting_model()
    model = ChatOpenAI(model=models)
    st.sidebar.warning(
        "NOTE - To generate html use model - 'gpt-4.1-mini' for better results")

    class htmlstate(TypedDict):
        topic: str
        prompt : str
        html: str

    def html_format(state: htmlstate):

        prompt = f"""You are an HTML study-material generator.

            Convert the CONTENT into a complete professional HTML study page.
            Bsed on the given prompt :{state['prompt']} you have to generate the content 
            for the topic:{state['topic']}
        """
        response = model.invoke(prompt).content

        return {"html": response , 'prompt': response}

    # uploading the file
    st.space("small")
    st.subheader("Upload Your File Below👇")
    st.caption("✅Make sure The File Must Be Docx File")
    uploaded_file = st.file_uploader("choose the file")
    full_text = []

    if uploaded_file is not None:
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            full_text.append(para.text)
    else:
        st.warning("Please upload the file first!!")

    content = "\n".join(full_text)
    st.markdown(content)

    # creating a graph
    graph = StateGraph(htmlstate)

    # creating a node
    graph.add_node("html", html_format)

    # creating edge
    graph.add_edge(START, "html")
    graph.add_edge("html", END)

    # compiling graph
    workflow = graph.compile()
    st.space("small")
    st.subheader("✍️Prompting")
    st.caption("you can edit the prompt as per your requirements")
    prompt = st.text_area(label="Enter Prompt",value='''
            You are an HTML study-material generator.
            Convert the CONTENT into a complete professional HTML study page.
            DESIGN - follow the same format for all the content generated. (no changes are to be made)
            White page background for whole content 
            Centered white container (max-width: 900px)
            Font: Segoe UI, Arial, sans-serif
            Blue h1, h2, h3 headings
            Section boxes with a left blue border
            Dark, rounded code blocks
            Green “Outcome” boxes after examples
            Soft shadow and rounded corners for containers

            STRUCTURE (use only what exists in the content) 
            Title + subtitle
            Introduction
            keep  all the code in <pre><code>.
            the topics included in the content 

            RULES (Strictly follow the rules for all)
            Nothing extra is to be included.
            Do not add, remove, summarize, or generate any content
            Use the structure only where the content supports it
            Wrap all code strictly inside <pre><code>
            Keep links as plain <a> tags
            Return ONLY valid HTML
            No explanations, comments, or extra text outside the HTML
            do not change the sequence of the content keep it as it is 
            make sure to keep the images in the image tag.''',
            height=500 , width='stretch')
    
    initial_state = {
        "topic": content,
        "prompt":prompt
    }

    generate = st.button("GENERATE HTML", use_container_width=True)

    if generate:
        with st.spinner("⛷️Generating Response...."):
            time.sleep(5)
            # invoking graph
            final_output = workflow.invoke(initial_state)
            html_output = final_output["html"]
            st.markdown(html_output)
            # create a session state
            st.session_state['html_output'] = html_output
            component.html(st.session_state['html_output'], height=800, scrolling=True) #giving the output in html format

    try:
        insert_html = st.button("INSERT DATA INTO FILE",use_container_width=True)

        if insert_html:
            html_file_name = uploaded_file.name.replace(".docx", ".html")
            if "html_output" not in st.session_state:
                st.warning("please generate the content first")

            else:
                with open(f"{html_file_name}", 'w', encoding="utf-8") as file:
                    file.write(st.session_state['html_output'])
            st.success("📝Data inserted successfully!!")

            st.download_button(
                label="DOWNLOAD HTML FILE",
                data=st.session_state['html_output'],
                file_name=f"{html_file_name}",
                mime="text/html",
                icon=":material/download:",
                width ='stretch'

            )
    except Exception as e:
        st.error(f"Error {e}")


# buttons to access others files
    roadmap_button = st.button("GENERATE ROADMAP", use_container_width=True)
    outline_button = st.button("GENERATE OUTLINE", use_container_width=True)
    final_material_button = st.button(
        "GENERATE MATERIAL", use_container_width=True)

    if roadmap_button:
        st.switch_page("pages/road_map.py")
    if outline_button:
        st.switch_page("pages/outline.py")

    if final_material_button:
        st.switch_page("pages/final_material.py")

else:
    st.switch_page("password.py")
