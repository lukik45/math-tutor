from neo4j import GraphDatabase
import yaml
import json
import os

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Configure the data directory (adjust path as needed)
DATA_SUBDIR = "knowledge_graph"  # Main directory containing YAML files
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", DATA_SUBDIR)

def load_yaml(filepath):
    """Load a YAML file and return its contents."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as file:
        return yaml.safe_load(file)

# --- Load Concepts from BASE_DIR/concepts in alphabetical order ---
concepts_dir = os.path.join(BASE_DIR, "concepts")
data_concepts = []
if os.path.isdir(concepts_dir):
    for filename in sorted(os.listdir(concepts_dir)):  # Process files in alphabetical order
        if filename.endswith(".yaml"):
            filepath = os.path.join(concepts_dir, filename)
            data = load_yaml(filepath)
            if "concepts" in data:
                data_concepts.extend(data["concepts"])
else:
    print("Warning: Concepts directory not found.")

# --- Load Problems and Solutions from BASE_DIR ---
data_problems = load_yaml(os.path.join(BASE_DIR, "problems.yaml"))
data_solutions = load_yaml(os.path.join(BASE_DIR, "solutions.yaml"))

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
            pending_links = []  # List of (concept_name, prereq_name) that failed initially
            
            # --- Insert Concepts ---
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
                # Process prerequisites
                for prereq in concept.get("requires", []):
                    result = session.run(
                        "MATCH (pr:Concept {name: $prereq_name}) RETURN pr",
                        prereq_name=prereq
                    )
                    if result.single() is None:
                        # Memorize this link for later
                        pending_links.append((concept["name"], prereq))
                    else:
                        session.run(
                            """
                            MATCH (c:Concept {name: $concept_name}), (pr:Concept {name: $prereq_name})
                            MERGE (c)-[:REQUIRES]->(pr)
                            """,
                            concept_name=concept["name"],
                            prereq_name=prereq
                        )
            # --- Reattempt pending prerequisite links ---
            changed = True
            while pending_links and changed:
                new_pending = []
                changed = False
                for concept_name, prereq_name in pending_links:
                    result = session.run(
                        "MATCH (pr:Concept {name: $prereq_name}) RETURN pr",
                        prereq_name=prereq_name
                    )
                    if result.single() is None:
                        new_pending.append((concept_name, prereq_name))
                    else:
                        session.run(
                            """
                            MATCH (c:Concept {name: $concept_name}), (pr:Concept {name: $prereq_name})
                            MERGE (c)-[:REQUIRES]->(pr)
                            """,
                            concept_name=concept_name,
                            prereq_name=prereq_name
                        )
                        changed = True
                if len(new_pending) == len(pending_links):
                    # No progress made in this pass; break out.
                    break
                pending_links = new_pending
            if pending_links:
                print("Warning: Some prerequisite links could not be added:", pending_links)
            
            # --- Insert Problems ---
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
            
            # --- Insert Solutions & Their Steps ---
            for solution in data_solutions.get("solutions", []):
                # Generate solution id based on problem_id, source, and date if not provided.
                sol_id = solution.get("id")
                if not sol_id:
                    sol_id = f"{solution['problem_id']}_{solution['source'].replace(' ', '_')}_{solution['date']}"
                session.run(
                    """
                    MERGE (s:Solution {id: $id})
                    SET s.problem_id = $problem_id, s.source = $source, s.date = $date
                    """,
                    id=sol_id,
                    problem_id=solution["problem_id"],
                    source=solution["source"],
                    date=solution["date"]
                )
                # Link solution to its problem
                session.run(
                    """
                    MATCH (p:Problem {id: $problem_id}), (s:Solution {id: $solution_id})
                    MERGE (p)-[:HAS_SOLUTION]->(s)
                    """,
                    problem_id=solution["problem_id"],
                    solution_id=sol_id
                )
                # Process each step
                for step in solution.get("steps", []):
                    step_id = step.get("id")
                    if not step_id:
                        step_id = sol_id + "_step_" + str(step["step_number"])
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
                    # Link step to its solution
                    session.run(
                        """
                        MATCH (s:Solution {id: $solution_id}), (st:Step {id: $step_id})
                        MERGE (s)-[:HAS_STEP]->(st)
                        """,
                        solution_id=sol_id,
                        step_id=step_id
                    )
                    # Link step to each related concept
                    for concept_name in step.get("related_concepts", []):
                        result = session.run(
                            "MATCH (c:Concept {name: $concept_name}) RETURN c",
                            concept_name=concept_name
                        )
                        if result.single() is None:
                            print(f"Warning: Related concept '{concept_name}' in step '{step_id}' not found.")
                        else:
                            session.run(
                                """
                                MATCH (st:Step {id: $step_id}), (c:Concept {name: $concept_name})
                                MERGE (st)-[:APPLIES_CONCEPT]->(c)
                                """,
                                step_id=step_id,
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

# --- Main Execution ---
kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
kg.clear_database()         # Clear previous data
kg.create_constraints()
kg.insert_data()              # Insert all data from YAML files
print("🚀 Knowledge Graph initialized with fresh data!")

# Optionally, fetch and display the entire graph
graph = kg.get_entire_graph()
#print(json.dumps(graph, indent=2))

kg.close()
