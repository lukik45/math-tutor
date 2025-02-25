in v0, no docker is used if not necessary. everything runs on local, except LLMs

# 
- Generates step-by-step solutions for math problems using an LLM.
- Annotates each solution step with relevant math concepts from a knowledge graph.
- Allows users to explore and modify the knowledge graph.
- Enables administrators to add or update problems and solutions in the KG.


# System Architecture
![[Pasted image 20250220133200.png]]



- `api_gateway`
	- A central API layer (built with FastAPI or similar) that connects the front-end, engine, and KG, ensuring modularity and scalability.
- `solution_engine`
- The core processing unit (likely using LangChain) that:
	- Interprets user queries.
	- Generates step-by-step solutions via the LLM. `math_inference_module`
	- Maps each solution step to relevant KG concepts. `annotation_module`
- `math_inference_module`
- `annotation_module`
- `knowledge_graph`
	- A Neo4j database that stores math concepts (organized hierarchically), problems, and precomputed solutions.
- `administration_module`
	A management tool that allows administrators to:
	- Modify and update KG concepts.
	- Add or update problems and solutions.

- `user_interface`
	A front-end (e.g., a web app) where students:
	- Enter math problems.
	- View detailed, annotated solutions.
	- Explore underlying concepts.

# Functional Requirements
### Knowledge Graph (Neo4j)

**Concept Storage & Retrieval:**

- **F1.1:** Store math concept nodes with fields: name, description, example.
- **F1.2:** Define prerequisite relationships between concepts.
- **F1.3:** Provide query endpoints for retrieving concepts by name or relationships.

**Problem and Solution Storage:**

- **F1.4:** Store problem nodes with a unique id, text, and difficulty.
- **F1.5:** Store solution nodes with unique ids and fields such as problem_id, source, date.
- **F1.6:** Store step nodes with step_number, explanation, mathematical transformation, and related concept references.
- **F1.7:** Create relationships: Problem → HAS_SOLUTION, Solution → HAS_STEP, Step → APPLIES_CONCEPT.

**Administration and Editing:**

- **F1.8:** Allow CRUD operations on concepts, problems, and solutions via an API or admin interface.
- **F1.9:** Ensure dependency links (prerequisites) are automatically retried if initially missing.

### Engine (LLM + LangChain Pipeline)

**Problem Parsing and Classification:**

- **F2.1:** Accept a math problem in natural language and determine its type (e.g., algebra, arithmetic).
- **F2.2:** Parse the problem text and extract relevant parameters.

**Solution Generation:**

- **F2.3:** Generate a detailed step-by-step solution using a fine-tuned LLM.
- **F2.4:** Break down the solution into individual steps with clear explanations and mathematical transformations.
- **F2.5:** Annotate each step with one or more math concept names based on the solution content.

**Knowledge Graph Integration:**

- **F2.6:** Query the KG to retrieve detailed information (e.g., descriptions, examples) for each linked concept.
- **F2.7:** Store newly generated solutions and steps in the KG for future retrieval.

**API Exposure:**

- **F2.8:** Expose an endpoint (e.g., `/solve`) that accepts a math problem and returns a structured, annotated solution.

### User Interface (Front-End)

**User Interaction:**

- **F3.1:** Provide a text input for users to enter math problems.
- **F3.2:** Validate input and provide helpful error messages for invalid entries.

**Solution Display:**

- **F3.3:** Display the generated solution step-by-step with clear formatting.
- **F3.4:** Link each step to its associated math concept(s), with interactive elements (e.g., tooltips, clickable links) to show additional details.
- **F3.5:** Offer supplementary learning resources based on the identified concepts.

### Administration Interface (Admin UI)

**Content Management:**

- **F4.1:** Provide a dashboard for educators to view, add, modify, or delete math concepts.
- **F4.2:** Allow management of problem and solution data (e.g., editing solution steps, verifying annotations).
- **F4.3:** Enable batch upload or modification of concepts from YAML or other files.
- **F4.4:** Display dependency graphs to help administrators understand concept relationships.

### API Gateway / Backend API

**Routing and Orchestration:**

- **F5.1:** Expose REST API endpoints for problem submission, solution retrieval, and KG management.
- **F5.2:** Secure the endpoints using authentication (e.g., JWT) and authorization mechanisms.
- **F5.3:** Log all API requests and responses for monitoring and debugging.

**Data Aggregation:**

- **F5.4:** Format responses that aggregate data from the Engine and KG into a unified JSON structure.
- **F5.5:** Provide endpoints for retrieving a full view of the KG (for administrative or visualization purposes).


# API endpoints

### 1. Problem & Solution Endpoints

#### **1.1 Submit Problem & Generate Solution**

- **Endpoint:** `POST /solve`
- **Description:** Accepts a math problem (in natural language) from the user, processes it using the LLM and concept annotation engine, and returns a step-by-step solution with concept links.
- **Request Body (JSON):**
    
    ```json
    {
      "problem": "How many three-digit numbers have a digit sum equal to 4, and is the total sum divisible by 9?"
    }
    ```
    
- **Response (JSON):**
    
    ```json
    {
      "solution": [
        {
          "step": 1,
          "step_explanation": "Count the three-digit numbers whose digits sum to 4.",
          "math_transformation": "Case breakdown based on the hundreds digit: 4 + 3 + 2 + 1 = 10.",
          "related_concepts": ["Natural Numbers", "Addition"]
        },
        {
          "step": 2,
          "step_explanation": "Calculate the total sum of these numbers.",
          "math_transformation": "Sum = 2110.",
          "related_concepts": ["Addition"]
        },
        {
          "step": 3,
          "step_explanation": "Check if 2110 is divisible by 9.",
          "math_transformation": "Digit sum = 2+1+1+0 = 4 → not divisible by 9.",
          "related_concepts": ["Divisibility by 9"]
        }
      ],
      "final_answer": {
        "count": 10,
        "sum": 2110,
        "divisible_by_9": false
      }
    }
    ```
    

#### **1.2 Retrieve Precomputed Solution**

- **Endpoint:** `GET /solutions/{problem_id}`
- **Description:** Retrieves a precomputed solution for the given problem ID (if available) from the knowledge graph.
- **Path Parameter:**
    - `problem_id`: The unique identifier for the problem.
- **Response (JSON):**
    
    ```json
    {
      "problem_id": "P1",
      "solution": {
        "source": "chat_manual",
        "date": "2024-02-15",
        "steps": [
          {
            "step": 1,
            "step_explanation": "Count the three-digit numbers whose digits sum to 4.",
            "math_transformation": "Case breakdown: 4 + 3 + 2 + 1 = 10.",
            "related_concepts": ["Natural Numbers", "Addition"]
          },
          // Additional steps...
        ],
        "final_answer": {
          "count": 10,
          "sum": 2110,
          "divisible_by_9": false
        }
      }
    }
    ```
    

#### **1.3 Create/Update Problem & Solution (Administration)**

- **Endpoint:** `POST /admin/problem`
- **Description:** Creates or updates a problem and its solution in the knowledge graph. (This endpoint is secured and only accessible to administrators.)
- **Request Body (JSON):**
    
    ```json
    {
      "problem": {
        "id": "P1",
        "text": "How many three-digit numbers have a digit sum equal to 4, and is the total sum divisible by 9?",
        "difficulty": "medium"
      },
      "solution": {
        "source": "chat_manual",
        "date": "2024-02-15",
        "steps": [
          {
            "step_number": 1,
            "step_explanation": "Count the three-digit numbers...",
            "math_transformation": "Detailed breakdown...",
            "related_concepts": ["Natural Numbers", "Addition"]
          }
          // Additional steps...
        ]
      }
    }
    ```
    
- **Response:**  
    A success message along with the created/updated IDs.

---

### 2. Knowledge Graph (Concept) Endpoints

#### **2.1 Retrieve All Concepts**

- **Endpoint:** `GET /concepts`
- **Description:** Returns a list of all math concepts in the knowledge graph.
- **Response (JSON):**
    
    ```json
    {
      "concepts": [
        {
          "name": "Arithmetic",
          "description": "Arithmetic is the branch of mathematics that deals with numbers and basic operations.",
          "example": "3 + 4, 5 × 2, etc."
        },
        {
          "name": "Divisibility by 9",
          "description": "A number is divisible by 9 if the sum of its digits is divisible by 9.",
          "example": "729 is divisible by 9 because 7+2+9 = 18, and 18 is divisible by 9."
        }
        // More concepts...
      ]
    }
    ```
    

#### **2.2 Retrieve Concept Details**

- **Endpoint:** `GET /concepts/{name}`
- **Description:** Returns detailed information about a specific math concept.
- **Path Parameter:**
    - `name`: The name of the concept.
- **Response (JSON):**
    
    ```json
    {
      "name": "Divisibility by 9",
      "description": "A number is divisible by 9 if the sum of its digits is divisible by 9.",
      "example": "729 is divisible by 9 because 7+2+9 = 18, and 18 is divisible by 9."
    }
    ```
    

#### **2.3 Update Concept (Administration)**

- **Endpoint:** `PUT /admin/concepts/{name}`
- **Description:** Updates the details of a specific concept (only accessible to administrators).
- **Path Parameter:**
    - `name`: The name of the concept to update.
- **Request Body (JSON):**
    
    ```json
    {
      "description": "Updated description...",
      "example": "Updated example...",
      "requires": ["Another Concept"]
    }
    ```
    
- **Response:**  
    Confirmation that the concept has been updated.

---

### 3. Administration Endpoints

#### **3.1 Manage Problems and Solutions**

- **Endpoint:** `POST /admin/problem`  
    (See Endpoint 1.3 for creating/updating problems and solutions.)

#### **3.2 Manage User Accounts (Optional)**

- **Endpoint:** `GET /admin/users`
    - **Description:** Retrieve user data for progress tracking.
- **Endpoint:** `PUT /admin/users/{user_id}`
    - **Description:** Update user data (e.g., learning progress).

---

### 4. Authentication & Security

- **Secure Endpoints:**  
    Administration endpoints (e.g., `/admin/concepts`, `/admin/problem`, `/admin/users`) should be secured with proper authentication (e.g., JWT tokens) and authorization mechanisms.
- **Public Endpoints:**  
    Endpoints such as `/solve`, `/problems`, and `/concepts` should be publicly accessible, but you might enforce rate limiting.

---

## Summary

This API specification provides a clear structure for:

- **Problem & Solution Management:** Endpoints for submitting, retrieving, and managing math problems and step-by-step solutions.
- **Knowledge Graph Access:** Endpoints to retrieve and update math concept information.
- **Administration:** Secure endpoints for educators to manage content.
- **Integration:** An API Gateway to connect the front-end UI, the Engine, and the Knowledge Graph.



# usage

api_gateway

Locally - development phase
```
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000

```