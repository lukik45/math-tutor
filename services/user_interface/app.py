import streamlit as st
# from streamlit_markdown import st_streaming_markdown
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


# model
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("HF_BASE_URL", "https://ta9u2hpk4yo4jiio.us-east-1.aws.endpoints.huggingface.cloud/v1/")
model_name = os.getenv("MODEL_NAME", "mav23/Qwen2.5-Math-7B-Instruct-GGUF")
llm = ChatOpenAI(
    model = model_name,
    max_completion_tokens=30,
    api_key=openai_api_key,
    base_url=base_url,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
st.set_page_config(page_title="Math Tutor", page_icon="👨‍🏫")

st.title("Math Tutor")



class CustomOutputParser(StrOutputParser):
    def parse(self, text: str) -> str:
        # First, use the original parsing behavior if needed
        parsed_text = super().parse(text)
        # Now, perform your custom replacements.
        # Replace "old" with "new" as an example.
        parsed_text = parsed_text.replace(r"\(", "$").replace(r"\)", "$").replace(r"\[", "$$").replace(r"\]", "$$")
        # Add more replacements if needed:
        # parsed_text = parsed_text.replace("string_to_find", "replacement")
        return parsed_text
    
# get response
def get_response(query, chat_history):
    template = r"""
    Solve with clear and rich explanation for a student, that has a serious backlog. In the form of steps: Step1, Step2...
    Chat history: {chat_history}
    
    User question: {user_question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm |CustomOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": query
    })



# conversation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else: 
        with st.chat_message("AI"):
            st.markdown(message.content)
            
            
# user input
user_query = st.chat_input("Your message")
if user_query is not None and user_query !="":
    st.session_state.chat_history.append(HumanMessage(user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        
        ai_response = st.write_stream(get_response(user_query, st.session_state.chat_history))
        os.write(1,ai_response.encode("utf-8") )
    st.session_state.chat_history.append(AIMessage(ai_response))
    
    
    