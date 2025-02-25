import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import OpenAI  # LangChain's OpenAI wrapper
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

app = FastAPI(title="Solution Engine API using Custom Model via OpenAI with streaming", version="0.1")

# Retrieve configuration from environment variables or set defaults.
openai_api_key = os.getenv("OPENAI_API_KEY",)
base_url = os.getenv("HF_BASE_URL", "https://ta9u2hpk4yo4jiio.us-east-1.aws.endpoints.huggingface.cloud/v1/")
model_name = os.getenv("MODEL_NAME", "mav23/Qwen2.5-Math-7B-Instruct-GGUF")

# Initialize the LLM using LangChain's OpenAI wrapper.
# Here, we pass additional parameters (top_p, temperature, etc.) as desired.
llm = OpenAI(
    model=model_name,
    api_key=openai_api_key,
    base_url=base_url,
    # temperature=None,
    # top_p=None,
    max_tokens=1500,
    stream=True,
    # seed=None,
    # stop=None,
    # frequency_penalty=None,
    # presence_penalty=None
)

# Define a prompt template that instructs the model to generate a step-by-step solution.
prompt_template = PromptTemplate(
    input_variables=["problem"],
    template="Solve with clear and rich explanation for a student, that has a serious backlog. In the form of steps: Step1, Step2... The problem: {problem}"
)

# Create a chain by combining the prompt template with the LLM.
chain = prompt_template | llm

# Pydantic model for input validation.
class ProblemRequest(BaseModel):
    problem: str

# @app.post("/solve")
# def solve_problem(req: ProblemRequest):
#     """
#     Solves a math problem using the custom model hosted at your inference endpoint.
#     It uses LangChain's chain to format the prompt and forward it to the OpenAI client.
#     """
#     try:
#         # Invoke the chain with the provided problem.
#         solution = chain.invoke({"problem": req.problem})
#         return {"solution": solution}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# def read_root():
#     return {"message": "Solution Engine API using Custom Model via OpenAI is running."}

@app.post("/solve")
async def solve_problem(req: ProblemRequest):
    """
    Endpoint to solve a math problem with streaming.
    The endpoint uses LangChain to format the prompt and invoke the OpenAI client in streaming mode.
    The tokens (or text chunks) are streamed back as they are generated.
    """
    try:
        # For streaming, we assume that the chain.invoke() method supports a stream parameter.
        # Depending on your LangChain version, you may need to call llm.invoke() directly.
        # Here, we'll try using chain.invoke with stream=True.
        generator = chain.invoke({"problem": req.problem}, stream=True)

        async def stream_generator():
            # If the generator yields dictionaries with a 'token' or 'text' field, adjust accordingly.
            for chunk in generator:
                # Here, we assume chunk is a string; if it's a dict, extract the content.
                yield chunk

        return StreamingResponse(stream_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# To run the server locally, use:
# uvicorn solution_engine:app --host 0.0.0.0 --port 8000 --reload
