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
Create **separate full HTML files for each topic** (Topic 1 → one file, Topic 2 → next file, etc.).
Use the **exact CSS below inside `<style>`** and follow all rules strictly.
```html
<style>
  body {font-family:"Segoe UI",Arial,sans-serif;background:#fff;margin:0;padding:2rem 1rem;color:#000;}
  .container {max-width:900px;margin:0 auto;background:#fff;border-radius:10px;box-shadow:0 4px 8px rgba(22,60,107,0.1);padding:2rem 2.5rem;}
  h1,h2,h3 {color:#163c6b;margin-top:0;}
  section {border-left:5px solid #163c6b;padding-left:1rem;margin-bottom:2rem;}
  pre {background:#163c6b;color:#dfefff;border-radius:8px;padding:1rem;overflow-x:auto;}
  a {color:#163c6b;text-decoration:underline;}
</style>
### RULES
* One **complete HTML document per topic**
* Keep **original content, order, structure exactly**
* Use `<section>` blocks
* Wrap code in:
  ```html
  <pre><code>...</code></pre>
  ```
* Keep `<a>` and `<img>` as given
* Use tables only if present
* **Subtopic headings must be bold** using `<strong>`
### DO NOT
* Add, remove, rewrite, or summarize content
* Change order or structure
* Add comments or explanations
### OUTPUT
Return **ONLY valid HTML** for **all topic files together**
### INPUT
Convert the study material exactly as provided.
''', height=500 , width='stretch')
    
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


