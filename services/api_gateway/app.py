from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from kg import get_solution_from_kg, get_all_concepts, get_all_problems, close_driver
# Optionally, import store_solution_in_kg if you plan to use it later.

app = FastAPI(title="Math Tutor API", version="0.1")

# Dummy URL for the solution engine service (update as needed)
SOLUTION_ENGINE_URL = os.getenv("SOLUTION_ENGINE_URL", "http://solution_engine:8000/solve")

# Pydantic model for problem submission
class ProblemRequest(BaseModel):
    problem: str

@app.post("/solve")
def solve_problem(req: ProblemRequest):
    """
    Endpoint to solve a math problem.
    First, it queries the KG for a precomputed solution.
    If no solution is found, it calls the solution engine to generate one.
    """
    # Attempt to retrieve a solution from the KG using the problem text.
    solution = get_solution_from_kg(req.problem)
    if solution:
        return {"solution": solution}
    
    # If no solution is found in the KG, call the solution engine.
    try:
        engine_response = requests.post(SOLUTION_ENGINE_URL, json={"problem": req.problem})
        if engine_response.status_code != 200:
            raise HTTPException(status_code=engine_response.status_code, detail="Solution engine error")
        solution_data = engine_response.json()
        # Optionally, store the new solution in the KG.
        # store_solution_in_kg(problem_data, solution_data)
        return {"solution": solution_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/concepts")
def list_concepts():
    """
    Endpoint to retrieve all math concepts from the knowledge graph.
    """
    try:
        concepts = get_all_concepts()
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/problems")
def list_problems():
    """
    Endpoint to retrieve all math problems from the knowledge graph.
    """
    try:
        problems = get_all_problems()
        return {"problems": problems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """
    Root endpoint to confirm that the API is running.
    """
    return {"message": "Math Tutor API is running."}

@app.on_event("shutdown")
def shutdown_event():
    close_driver()
