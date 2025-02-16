from neo4j import GraphDatabase
import yaml
import json
import os

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Configure the data directory (adjust path as needed)
DATA_SUBDIR = "knowledge_graph"  # Your directory containing the YAML files
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", DATA_SUBDIR)

# Load YAML data safely
def load_yaml(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as file:
        return yaml.safe_load(file)

# Load the datasets:
# Concepts are split into two files: arithmetic.yaml and algebra.yaml.
data_arithmetic = load_yaml("concepts/arithmetic.yaml")
data_algebra = load_yaml("concepts/algebra.yaml")
# Merge the concept lists from both files.
data_concepts = data_arithmetic["concepts"] + data_algebra["concepts"]

data_problems = load_yaml("problems.yaml")
data_solutions = load_yaml("solutions.yaml")

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """Deletes all nodes and relationships from the Neo4j database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Previous data erased from Neo4j.")

    def create_constraints(self):
        """Defines uniqueness constraints for better performance."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Problem) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Solution) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (st:Step) REQUIRE st.id IS UNIQUE"
        ]
        with self.driver.session() as session:
            for query in queries:
                session.run(query)

    def insert_data(self):
        """Inserts concepts, problems, solutions, and steps into Neo4j."""
        with self.driver.session() as session:
            # Insert Concepts (using name as the unique key)
            for concept in data_concepts:
                session.run(
                    """
                    MERGE (c:Concept {name: $name})
                    SET c.description = $description, c.example = $example
                    """,
                    name=concept["name"],
                    description=concept.get("description", ""),
                    example=concept.get("example", "")
                )
                # Link Prerequisites (each prereq is referenced by its name)
                for prereq in concept.get("requires", []):
                    # Check if the prerequisite exists
                    result = session.run(
                        "MATCH (pr:Concept {name: $prereq_name}) RETURN pr",
                        prereq_name=prereq
                    )
                    if result.single() is None:
                        print(f"Warning: Prerequisite concept '{prereq}' required by '{concept['name']}' not found.")
                    else:
                        session.run(
                            """
                            MATCH (c:Concept {name: $concept_name}), (pr:Concept {name: $prereq_name})
                            MERGE (c)-[:REQUIRES]->(pr)
                            """,
                            concept_name=concept["name"],
                            prereq_name=prereq
                        )

            # Insert Problems (assuming problems.yaml contains an "id" field)
            for problem in data_problems.get("problems", []):
                session.run(
                    """
                    MERGE (p:Problem {id: $id})
                    SET p.text = $text, p.difficulty = $difficulty
                    """,
                    id=problem["id"],
                    text=problem["text"],
                    difficulty=problem["difficulty"]
                )

            # Insert Solutions & Steps
            for solution in data_solutions.get("solutions", []):
                session.run(
                    """
                    MERGE (s:Solution {id: $id})
                    SET s.source = $source, s.date = $date
                    """,
                    id=solution["id"],
                    source=solution["source"],
                    date=solution["date"]
                )
                # Link Solution to Problem
                session.run(
                    """
                    MATCH (p:Problem {id: $problem_id}), (s:Solution {id: $solution_id})
                    MERGE (p)-[:HAS_SOLUTION]->(s)
                    """,
                    problem_id=solution["problem_id"],
                    solution_id=solution["id"]
                )
                # Insert Steps and Link them
                for step in solution.get("steps", []):
                    session.run(
                        """
                        MERGE (st:Step {id: $id})
                        SET st.step_explanation = $step_explanation, 
                            st.math_transformation = $math_transformation, 
                            st.related_concept = $related_concept, 
                            st.step_number = $step_number
                        """,
                        id=step["id"],
                        step_explanation=step["step_explanation"],
                        math_transformation=step["math_transformation"],
                        related_concept=json.dumps(step["related_concept"]),
                        step_number=step["step_number"]
                    )
                    # Link Steps to Solutions
                    session.run(
                        """
                        MATCH (s:Solution {id: $solution_id}), (st:Step {id: $step_id})
                        MERGE (s)-[:HAS_STEP]->(st)
                        """,
                        solution_id=solution["id"],
                        step_id=step["id"]
                    )
                    # Link Steps to Concepts (using concept names)
                    for concept_name in step.get("related_concept", []):
                        result = session.run(
                            "MATCH (c:Concept {name: $concept_name}) RETURN c",
                            concept_name=concept_name
                        )
                        if result.single() is None:
                            print(f"Warning: Related concept '{concept_name}' in step '{step['id']}' not found.")
                        else:
                            session.run(
                                """
                                MATCH (st:Step {id: $step_id}), (c:Concept {name: $concept_name})
                                MERGE (st)-[:APPLIES_CONCEPT]->(c)
                                """,
                                step_id=step["id"],
                                concept_name=concept_name
                            )

    def get_entire_graph(self):
        """Fetches and returns all nodes and relationships from the graph."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                """
            )
            graph_data = []
            for record in result:
                node1 = dict(record["n"]) if record["n"] else None
                rel = record["r"].type if record["r"] else None
                node2 = dict(record["m"]) if record["m"] else None
                graph_data.append({"node1": node1, "relationship": rel, "node2": node2})
            return graph_data

# Run the script
kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
kg.clear_database()  # Clear previous data before inserting new data
kg.create_constraints()
kg.insert_data()
print("🚀 Knowledge Graph initialized with fresh data!")

# Optionally, fetch and display the entire graph
graph = kg.get_entire_graph()
#print(json.dumps(graph, indent=2))

kg.close()
