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

# Initialize separate histories and solution context if not already in session state
if "math_chat_history" not in st.session_state:
    st.session_state.math_chat_history = []
if "followup_chat_history" not in st.session_state:
    st.session_state.followup_chat_history = []
if "math_solution" not in st.session_state:
    st.session_state.math_solution = ""

st.set_page_config(page_title="Math Tutor", page_icon="👨‍🏫")
st.title("Math Tutor")

#############################################
# Sidebar with instructions/settings
#############################################
st.sidebar.header("About This App")
st.sidebar.markdown(
    """
    **Math Tutor** is a two-part application:
    
    1. **Solve Math Problem:** Enter a math problem to get a step-by-step explanation.
    2. **Follow-up Chat:** Ask follow-up questions related to the solution.
    
    The math solution is streamed token-by-token (updated after every period) 
    and is then used as context for the follow-up conversation.
    """
)


#############################################
# Utility functions
#############################################
def process_text(text: str) -> str:
    """Replace LaTeX delimiters dynamically."""
    return (text.replace(r"\(", "$")
                .replace(r"\)", "$")
                .replace(r"\[", "$$")
                .replace(r"\]", "$$"))

def get_response(query, chat_history):
    """Return a streaming generator of tokens for the math solution."""
    template = r"""
    Solve with clear and rich explanation for a student with a serious backlog. 
    Present the answer as clear steps: Step1. explanation, Step2. explanation.
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

#############################################
# Pane 1: Math Problem Solver (Single Response)
#############################################
st.header("Solve Math Problem")
with st.expander("Enter Math Problem", expanded=True):
    math_query = st.text_input("Enter your math problem", key="math_problem_input", placeholder="e.g.")
    if st.button("Solve Math Problem"):
        # Append the math problem to the math chat history
        st.session_state.math_chat_history.append(HumanMessage(math_query))
        math_placeholder = st.empty()
        response_text = ""
        token_buffer = ""
        # Stream tokens from the math solution
        for token in get_response(math_query, st.session_state.math_chat_history):
            token_buffer += token
            # Flush buffered tokens when a period is encountered
            if "." in token_buffer:
                response_text += token_buffer
                processed = process_text(response_text)
                math_placeholder.markdown(processed)
                token_buffer = ""
                time.sleep(0.05)
        # Flush any remaining tokens
        if token_buffer:
            response_text += token_buffer
            processed = process_text(response_text)
            math_placeholder.markdown(processed)
        # Save the final math solution in session state for follow-up context
        st.session_state.math_solution = processed
        st.session_state.math_chat_history.append(AIMessage(processed))

#############################################
# Pane 2: Follow-Up Chat with Context
#############################################
st.header("Follow-up Chat")

if not st.session_state.math_solution:
    st.info("Please solve a math problem first before asking follow-up questions.")

else: 
    # Display follow-up conversation history
    for message in st.session_state.followup_chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)
        else:
            with st.chat_message("AI"):
                st.markdown(message.content)

    followup_query = st.chat_input("Ask a follow-up question", key="followup_input")
    if followup_query is not None and followup_query != "":
        # Append the follow-up question to the follow-up chat history
        st.session_state.followup_chat_history.append(HumanMessage(followup_query))
        with st.chat_message("Human"):
            st.markdown(followup_query)
            
        # Prepare a follow-up prompt template that includes the math solution context.
        followup_template = r"""
        Based on the following math solution:
        {math_solution}
        
        And the previous conversation:
        {chat_history}
        
        Answer the following question clearly and with explanations:
        {user_question}
        """
        prompt = ChatPromptTemplate.from_template(followup_template)
        chain = prompt | llm | StrOutputParser()
        context = {
            "math_solution": st.session_state.math_solution,
            "chat_history": "\n".join([msg.content for msg in st.session_state.followup_chat_history]),
            "user_question": followup_query,
        }
        
        with st.chat_message("AI"):
            followup_placeholder = st.empty()
            response_text = ""
            token_buffer = ""
            # Stream tokens from the follow-up agent
            for token in chain.stream(context):
                token_buffer += token
                if "." in token_buffer:
                    response_text += token_buffer
                    processed = process_text(response_text)
                    followup_placeholder.markdown(processed)
                    token_buffer = ""
                    time.sleep(0.05)
            if token_buffer:
                response_text += token_buffer
                processed = process_text(response_text)
                followup_placeholder.markdown(processed)
            st.session_state.followup_chat_history.append(AIMessage(processed))
            os.write(1, str(st.session_state.followup_chat_history).encode("utf-8"))

