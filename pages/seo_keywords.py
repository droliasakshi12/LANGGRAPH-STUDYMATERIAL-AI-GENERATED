#GOOGLE KEYWORD PLANNER 

from langgraph.graph import StateGraph , START , END 
from dotenv import load_dotenv
import os 
from langchain_openai import ChatOpenAI 
from typing import TypedDict, Annotated , Literal
from pydantic import BaseModel ,Field 
import operator
import streamlit as st 
from pages.model_selection import selecting_model

if 'register' not in st.session_state:
    st.session_state['register'] = False

if st.session_state['register'] == True:

    #loading the env 
    load_dotenv(dotenv_path=r"my_api_key.env")
    os.environ["OPENAI_API_KEY"] = os.getenv("openai_api")

    #getting the models 
    models = selecting_model()
    model = ChatOpenAI(model=models)
    evaluate_model = ChatOpenAI(model="gpt-3.5-turbo")
    optimized_model = ChatOpenAI(model="gpt-5-nano-2025-08-07")



    #creating a basemodel 
    class evaluation(BaseModel):
        evalaute : Literal["approved","not_approved"] = Field(description="evaluating the content")
        feedback : str=Field(description="feedback for the content generated")
        
        
    #giving the struct to the model to evaluate 
    struct_model = evaluate_model.with_structured_output(evaluation)

    #creating a state class 
    class keywordstate(TypedDict):
        topic :str = Field(description="topic to generate the keyword")
        keywords : str = Field(description="keyword for the topic")
        evaluate : Literal["approved","not_approved"] 
        feedback : str 
        iteration : int 
        max_iteration :int 
        keywords_history :str = Annotated[list[str],operator.add]
        feedback_history : str = Annotated[list[str],operator.add]
        

    #creating the function to get the keyword 
    def generate_keyword(state:keywordstate):
        prompt = f"""
            you are a seo generator you have to create the keywords based on the {state['topic']}.Ensure to include all kind of keywords .Provide the best keyword for seo. """
            
        response = model.invoke(prompt).content
        
        return {"keywords":response , "keywords_history":[response]}

    #evaluating the model 
    def evaluate_keyword(state:keywordstate):
        prompt = f"""
            you are a evaluator who have to evaluate the keyword {state['keywords']} and based on that make sure to provide the best and most searched keywords.and provide the history if the generated content is approved or not provide me the top listed keywords.
        """
        response = struct_model.invoke(prompt)
        
        return {"evaluate":response.evaluate,"feedback":response.feedback,"feedback_history":response.feedback}


    def optimizing(state:keywordstate):
        prompt = f"""
            you have to optimize the content on topic {state['topic']} , content generated {state['keywords']} and the feedback gievn {state['feedback']}. 
        """
        
        response = optimized_model.invoke(prompt)
        iteration = state['iteration']+1
        
        return {"keywords":response , "iteration":iteration , "feedback_history":[response]}


    def evaluate_route(state:keywordstate):
        if state['evaluate'] == "approved" or state['iteration'] > state["max_iteration"]:
            return "approved"

        else :
            return "not_approved"
        
        

    #taking user input 
    user_input = st.text_input(label = "ENTER THE TOPIC")
    generate = st.button(label="GENERATE KEYWORD")

    #creating he graph 
    graph = StateGraph(keywordstate)

    #creating the nodes 
    graph.add_node("keyword",generate_keyword)
    graph.add_node("evaluate",evaluate_keyword)
    graph.add_node("optimize",optimizing)


    #creating edges 
    graph.add_edge(START , "keyword")
    graph.add_conditional_edges("evaluate",evaluate_route,{"approved":END , "not_approved":"optimize"})
    graph.add_edge("optimize","evaluate")


    #compilin the graph 
    keyword_workflow = graph.compile()

    initial_state = {
        "topic":user_input,
        "iteration":1,
        "max_iteration":3
    }

    #compling the graph 
    final_output = keyword_workflow.invoke(initial_state)

    if generate :
        st.markdown(final_output['keywords'])
        

else:
    st.switch_page("password.py")