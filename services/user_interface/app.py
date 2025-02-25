import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Model setup
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("HF_BASE_URL", "https://ta9u2hpk4yo4jiio.us-east-1.aws.endpoints.huggingface.cloud/v1/")
model_name = os.getenv("MODEL_NAME", "mav23/Qwen2.5-Math-7B-Instruct-GGUF")
llm = ChatOpenAI(
    model=model_name,
    max_completion_tokens=30,
    api_key=openai_api_key,
    base_url=base_url,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Math Tutor", page_icon="👨‍🏫")
st.title("Math Tutor")

# get_response returns a streaming generator of tokens
def get_response(query, chat_history):
    template = r"""
    Solve with clear and rich explanation for a student, that has a serious backlog. In the form of steps: Step1. explanation Step2. explanation
    Chat history: {chat_history}
    
    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    # Chain: prompt -> llm -> StrOutputParser
    chain = prompt | llm | StrOutputParser()
    return chain.stream({
        "chat_history": chat_history,
        "user_question": query
    })

# Define a function for processing replacements dynamically
def process_text(text: str) -> str:
    return (text.replace(r"\(", "$")
                .replace(r"\)", "$")
                .replace(r"\[", "$$")
                .replace(r"\]", "$$"))

# Display conversation history
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

# User input
user_query = st.chat_input("Your message")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        # Create a placeholder to update dynamically
        placeholder = st.empty()
        response_text = ""
        token_buffer = ""
        # Stream tokens from the response
        for token in get_response(user_query, st.session_state.chat_history):
            token_buffer += token
            # Check if the divider (".") is present in the token_buffer
            if "." in token_buffer:
                # Append buffered tokens to the complete response
                response_text += token_buffer
                # Process the accumulated text (apply replacements)
                processed = process_text(response_text)
                # Update the UI placeholder
                placeholder.markdown(processed)
                # Clear the token_buffer after flushing
                token_buffer = ""
                # Optional: add a small delay to allow the UI to update smoothly
                time.sleep(0.05)
        # Flush any remaining tokens after streaming finishes
        if token_buffer:
            response_text += token_buffer
            processed = process_text(response_text)
            placeholder.markdown(processed)
        
        ai_response = processed  # The final accumulated response
    st.session_state.chat_history.append(AIMessage(ai_response))
    os.write(1, str(st.session_state.chat_history).encode("utf-8"))
