import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from pydantic import BaseModel
from typing import Dict

import os
import time
import json
from openai import OpenAI  # OpenAI client for transformation step

load_dotenv()

# Set up API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
hf_math_key = os.getenv("HF_MATH_KEY")

# Model setup for the math solution
base_url = os.getenv("HF_BASE_URL", "https://ta9u2hpk4yo4jiio.us-east-1.aws.endpoints.huggingface.cloud/v1/")
math_model_name = os.getenv("MODEL_NAME", "mav23/Qwen2.5-Math-7B-Instruct-GGUF")
math_llm = ChatOpenAI(
    model=math_model_name,
    max_completion_tokens=1000,
    api_key=hf_math_key,
    base_url=base_url,
)

# Model setup for follow-up chat (using gpt-4o-mini)
followup_llm = ChatOpenAI(
    model="gpt-4o-mini",
    max_completion_tokens=1000,
    api_key=openai_api_key,
)

# Initialize session state variables
if "math_chat_history" not in st.session_state:
    st.session_state.math_chat_history = []
if "followup_chat_history" not in st.session_state:
    st.session_state.followup_chat_history = []
if "math_solution_markdown" not in st.session_state:
    st.session_state.math_solution_markdown = ""
if "math_solution_json" not in st.session_state:
    st.session_state.math_solution_json = ""

st.set_page_config(page_title="Math Tutor", page_icon="👨‍🏫")
st.title("Math Tutor")

#############################################
# Sidebar with instructions/settings
#############################################
st.sidebar.header("About This App")
st.sidebar.markdown(
    """
    **Math Tutor** is a three-part application:
    
    1. **Solve Math Problem:** Enter a math problem to get a step-by-step explanation (in markdown).
    2. **Transform to JSON:** Convert the markdown solution into a structured JSON format.
    3. **Follow-up Chat:** Ask follow-up questions based on the structured solution.
    """
)
st.sidebar.markdown(f"**Math Model:** {math_model_name}")
st.sidebar.markdown("**Transformation & Follow-Up Model:** gpt-4o-mini")
st.sidebar.markdown("**Max Tokens:** Math: 1000, Transform: 150, Follow-up: 1000")

#############################################
# Utility functions
#############################################
def process_text(text: str) -> str:
    r"""Replace LaTeX delimiters dynamically:
       Converts \(...\) to $...$ and \[...\] to $$...$$.
    """
    return (text.replace(r"\(", "$")
                .replace(r"\)", "$")
                .replace(r"\[", "$$")
                .replace(r"\]", "$$"))

def get_math_response(query, chat_history):
    """Return a streaming generator of tokens for the math solution in markdown format."""
    template = r"""
    Solve the following math problem with clear, step-by-step explanations in markdown.
    
    Chat history: {chat_history}
    
    Problem: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | math_llm | StrOutputParser()
    return chain.stream({
        "chat_history": chat_history,
        "user_question": query
    })

#############################################
# Pane 1: Math Problem Solver (Markdown Output)
#############################################
st.header("Solve Math Problem")
with st.expander("Enter Math Problem", expanded=True):
    math_query = st.text_input("Enter your math problem", key="math_problem_input", placeholder="e.g. Solve 2x+3=7")
    if st.button("Solve Math Problem"):
        st.session_state.math_chat_history.append(HumanMessage(math_query))
        math_placeholder = st.empty()
        response_text = ""
        token_buffer = ""
        # Stream tokens from the math solution.
        for token in get_math_response(math_query, st.session_state.math_chat_history):
            token_buffer += token
            # Flush buffered tokens when a period is encountered.
            if "." in token_buffer:
                response_text += token_buffer
                processed = process_text(response_text)
                math_placeholder.markdown(processed)
                token_buffer = ""
                time.sleep(0.05)
        if token_buffer:
            response_text += token_buffer
            processed = process_text(response_text)
            math_placeholder.markdown(processed)
        # Save the markdown solution.
        st.session_state.math_solution_markdown = processed
        st.session_state.math_chat_history.append(AIMessage(processed))

#############################################
# Pane 2: Transform Markdown to JSON
#############################################
st.header("Transform Math Solution to JSON")
if not st.session_state.math_solution_markdown:
    st.info("Please solve a math problem first before converting to JSON.")
else:
    st.markdown("**Markdown Solution:**")
    st.markdown(st.session_state.math_solution_markdown)
    if st.button("Convert to JSON"):
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a conversion assistant. Convert the following markdown-formatted math solution into a JSON object by copying the content of each step exactly as it appears, preserving all formatting (including LaTeX delimiters). "
                        "The JSON should have the structure:\n\n"
                        "{\n"
                        '  "steps": {\n'
                        '      "step1": "<exact copy of step1>",\n'
                        '      "step2": "<exact copy of step2>",\n'
                        "      ...\n"
                        "  }\n"
                        "}\n\n"
                        "Do not alter or change any content; simply copy the steps as-is."
                    )
                },   
                {
                    "role": "user",
                    "content": st.session_state.math_solution_markdown
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "math_solution_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "steps": {
                                "description": "Step-by-step explanation",
                                "type": "object",
                                "additionalProperties": {"type": "string"}
                            }
                        },
                        "required": ["steps"],
                        "additionalProperties": False
                    }
                }
            }
        )
        try:
            json_output = response.choices[0].message.content
            parsed = json.loads(json_output)
            final_json = json.dumps(parsed, indent=2)
            st.session_state.math_solution_json = parsed

            # Display each step using st.markdown in separate blocks.
            st.markdown("### Solution Breakdown:")
            for step, explanation in parsed["steps"].items():
                with st.expander(f"{step}", expanded=True):
                    st.markdown(explanation)
        except Exception as e:
            st.error(f"Error converting to JSON: {e}")

#############################################
# Pane 3: Follow-Up Chat with Context (Using gpt-4o-mini)
#############################################
st.header("Follow-up Chat")
if not st.session_state.math_solution_json:
    st.info("Please convert a math solution to JSON first before asking follow-up questions.")
else:
    for message in st.session_state.followup_chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)
        else:
            with st.chat_message("AI"):
                st.markdown(message.content)

    followup_query = st.chat_input("Ask a follow-up question", key="followup_input")
    if followup_query:
        st.session_state.followup_chat_history.append(HumanMessage(followup_query))
        with st.chat_message("Human"):
            st.markdown(followup_query)

        followup_template = r"""
        Based on the following math solution in JSON format:
        {math_solution_json}
        
        And the previous conversation:
        {chat_history}
        
        Answer the following question clearly and with explanations:
        {user_question}
        """
        prompt = ChatPromptTemplate.from_template(followup_template)
        chain = prompt | followup_llm | StrOutputParser()
        context = {
            "math_solution_json": json.dumps(st.session_state.math_solution_json),
            "chat_history": "\n".join([msg.content for msg in st.session_state.followup_chat_history]),
            "user_question": followup_query,
        }

        with st.chat_message("AI"):
            followup_placeholder = st.empty()
            response_text = ""
            token_buffer = ""
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
            st.session_state.followup_chat_history.append(AIMessage(response_text))
