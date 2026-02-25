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
**🎨 DESIGN GUIDELINES (Strictly Follow)**
* Clean white page background
* Centered white container (max-width: 900px)
* Font: Segoe UI, Arial, sans-serif
* h1, h2, h3 color: #163c6b
* Section boxes with left border in #163c6b
* Rounded containers with soft shadows
* Code blocks: dark theme, rounded, color #dfefff
* “Outcome” boxes: green #dfefff, placed immediately after examples
* Tables (if present): clean, readable, consistent with design

⚠️ Keep design format fully consistent. No visual or structural changes.
**🧱 STRUCTURE RULES**
* Use only existing content (title, subtitle, introduction, topics)
* Maintain original sequence and order
* Use sections only where naturally supported
* Wrap all code strictly in `<pre><code>`
* Use tables only if already present
* Keep links as `<a>` and images as `<img>`
**🚫 STRICTLY PROHIBITED**
* Do not add, remove, rewrite, summarize, or generate new content
* Do not change structure or order
* No extra text, comments, or explanations

**✅ OUTPUT REQUIREMENT**
Return **ONLY valid HTML**.
''',
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

