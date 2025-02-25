import os
import json
from neo4j import GraphDatabase

# Configure Neo4j connection parameters from environment variables (or default values)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Create a Neo4j driver instance
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_solution_from_kg(problem_text: str):
    """
    Query the KG for a solution corresponding to a given problem text.
    """
    with driver.session() as session:
        query = """
            MATCH (p:Problem {text: $text})-[:HAS_SOLUTION]->(s:Solution)
            RETURN s
        """
        result = session.run(query, text=problem_text)
        record = result.single()
        if record:
            return record["s"]
    return None

def get_all_concepts():
    """
    Retrieve all concept nodes from the KG, along with a list of names of nodes
    that require (depend on) each concept.
    """
    with driver.session() as session:
        query = """
            MATCH (c:Concept)
            OPTIONAL MATCH (d)-[:REQUIRES]->(c)
            RETURN c, collect(d.name) as dependents
        """
        result = session.run(query)
        concepts = []
        for record in result:
            concept_node = record["c"]
            # Convert the Node to a dictionary of properties.
            concept_data = dict(concept_node)
            # Add the list of dependent concept names.
            concept_data["dependents"] = record["dependents"]
            concepts.append(concept_data)
    return concepts


def get_all_problems():
    """
    Retrieve all problem nodes from the KG.
    """
    with driver.session() as session:
        result = session.run("MATCH (p:Problem) RETURN p")
        problems = [record["p"] for record in result]
    return problems

def store_solution_in_kg(problem_data: dict, solution_data: dict):
    """
    Store a new solution (and its steps) into the KG and link it to the associated problem.
    This is a stub implementation for later expansion.
    """
    with driver.session() as session:
        # Merge the problem node
        session.run(
            """
            MERGE (p:Problem {id: $id})
            SET p.text = $text, p.difficulty = $difficulty
            """,
            id=problem_data["id"],
            text=problem_data["text"],
            difficulty=problem_data["difficulty"]
        )
        # Merge the solution node
        session.run(
            """
            MERGE (s:Solution {id: $id})
            SET s.problem_id = $problem_id, s.source = $source, s.date = $date
            """,
            id=solution_data["id"],
            problem_id=solution_data["problem_id"],
            source=solution_data["source"],
            date=solution_data["date"]
        )
        # Create relationship between Problem and Solution
        session.run(
            """
            MATCH (p:Problem {id: $problem_id}), (s:Solution {id: $solution_id})
            MERGE (p)-[:HAS_SOLUTION]->(s)
            """,
            problem_id=solution_data["problem_id"],
            solution_id=solution_data["id"]
        )
        # Insert steps and create relationships
        for step in solution_data.get("steps", []):
            step_id = step.get("id") or f"{solution_data['id']}_step_{step['step_number']}"
            session.run(
                """
                MERGE (st:Step {id: $id})
                SET st.step_explanation = $step_explanation,
                    st.math_transformation = $math_transformation,
                    st.related_concept = $related_concept,
                    st.step_number = $step_number
                """,
                id=step_id,
                step_explanation=step["step_explanation"],
                math_transformation=step["math_transformation"],
                related_concept=json.dumps(step["related_concepts"]),
                step_number=step["step_number"]
            )
            session.run(
                """
                MATCH (s:Solution {id: $solution_id}), (st:Step {id: $step_id})
                MERGE (s)-[:HAS_STEP]->(st)
                """,
                solution_id=solution_data["id"],
                step_id=step_id
            )
            for concept_name in step.get("related_concepts", []):
                session.run(
                    """
                    MATCH (st:Step {id: $step_id}), (c:Concept {name: $concept_name})
                    MERGE (st)-[:APPLIES_CONCEPT]->(c)
                    """,
                    step_id=step_id,
                    concept_name=concept_name
                )

def close_driver():
    """
    Closes the Neo4j driver.
    """
    driver.close()
