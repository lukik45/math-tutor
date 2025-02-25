

## **Core Features for MVP** (v0)

### **📌 Problem Input & Processing**

✅ User types (or uploads) a math problem.  
✅ The system first checks the Knowledge Graph to see if a solution already exists.  
✅ If the problem is new, the **Solution Engine** interprets and solves it.  
✅ If the problem exists in the database, the system retrieves the **precomputed step-by-step solution** and prerequisite concepts without additional computation.

---

### **📌 Solution Engine & Breakdown**

✅ The **Solution Engine** solves the problem step-by-step if it is not found in the Knowledge Graph.  
✅ Breaks the solution into prerequisite skills, mapping them to **"building blocks"** from the Knowledge Graph.  
✅ Uses **Natural Language Processing (NLP)** to interpret complex word problems and extract mathematical models.  
✅ Generates a structured response, where each step:

- Explains **what to do in the step**
- Shows the **mathematical transformation**
- Links to a **foundational concept ("building block")**

---

### **📌 Knowledge Graph Implementation**

✅ Maps relationships between mathematical concepts (e.g., equations, derivatives, optimization).  
✅ Stores solutions & their step breakdowns for future retrieval.  
✅ If a problem is already in the database, it returns the precomputed solution instead of calling the **Solution Engine**.  
✅ If the **Solution Engine** generates a new solution, it is stored in the Knowledge Graph for future use.

---

### **📌 Guided Learning & Redirection**

✅ Directs users to **explanations, exercises, and tools** needed for solving the problem.  
✅ If a user struggles with a prerequisite skill, the system recommends **focused exercises** to strengthen that concept.  
✅ Users can explore the **Knowledge Graph interactively** to understand how math concepts connect.

---

## **Sequence Diagram**

```
User → API Gateway: Enter Math Problem  

API Gateway → Knowledge Graph: Check if solution exists  

Knowledge Graph → API Gateway: Solution exists?  

[If solution exists]  
    API Gateway → User: Return Precomputed Step-by-Step Solution  

[If solution does NOT exist]  
    API Gateway → Solution Engine: Analyze and Solve Problem  
    Solution Engine → Knowledge Graph: Identify Prerequisite Concepts  
    Knowledge Graph → Solution Engine: Return Required Concepts  
    Solution Engine → Knowledge Graph: Store New Solution & Steps  
    Solution Engine → API Gateway: Return Structured Solution  
    API Gateway → User: Show Step-by-Step Solution  

API Gateway → Exercise Module: Recommend Exercises  
Exercise Module → User: Provide Learning Resources  
```

---

## **System Architecture Diagram**

```
+------------------------+
|   Frontend UI (React/Streamlit) |
+------------------------+
          |
          v
+------------------------+
|   API Gateway (FastAPI) |
+------------------------+
          |
          |-------------------------|
          v                         v
+------------------------+      +------------------------+
|   Solution Engine      |      |   User Service (PostgreSQL)  |
|   (Retrieval + AI)     |      |   (User Data Management)    |
+------------------------+      +------------------------+
          |
          v
+------------------------+
|   Knowledge Graph (Neo4j) |
|   (Math Concept Dependencies) |
+------------------------+
          |
          v
+------------------------+
|   Exercise Module (Recommendations) |
+------------------------+
```

---

## **Use Cases**

### **Use Case 1: Problem Solving & Breakdown**

#### **Actors**

👩‍🎓 **User (Student)**  
⚙️ **Solution Engine**

- Retrieves **precomputed solutions** or
- Solves problems **step-by-step** if no solution exists
- Breaks solutions into **fundamental math concepts ("building blocks")**

#### **User Story**

**As a Student:**

- I want to enter a math problem so the **Solution Engine** can explain how to solve it.
- I want to see which **foundational skills ("building blocks")** I need to improve.
- If the problem already exists, I want **instant retrieval** without unnecessary computation.
- If it's new, I want **step-by-step generated solutions**.
- If I struggle with a concept (building block), I want **related exercises** to strengthen my skills.

**As the Solution Engine:**

- I want to **first check the Knowledge Graph** for an existing solution before computing.
- If the problem is new, I want to **solve it step-by-step** and **break it down into prerequisite skills**.
- I want to **store new solutions** in the Knowledge Graph for future use.
- I want to **suggest related exercises** based on missing skills.

---

## **Key Features**

✅ **Solution Engine integrates AI and retrieval-based solutions**

- Supports both **stored solutions & AI-generated problem-solving**
- Ensures efficiency by **avoiding unnecessary computations**

✅ **Handles Complex Math Problems**

- Parses and solves **advanced word problems & optimizations**
- Links solutions to **fundamental math concepts** dynamically

✅ **Connection Between Solution Engine & Knowledge Graph**

- If the **problem already exists**, the system **retrieves precomputed solutions**
- The **Solution Engine** is only used if no solution exists in the database
- AI-generated solutions are **stored for future use**, reducing computation

✅ **Building Blocks in Solutions**

- Each step explicitly states:
    - **What mathematical principle is used**
    - **Why it is needed**
    - **How it connects to other concepts**

✅ **Adaptive Learning Approach**

- If a user lacks foundational knowledge, the system provides **interactive learning paths**
- Exercises adapt based on **user weaknesses**, reinforcing skills

---




# Functional Requirements

🔹 **The system generates a structured, step-by-step solution that includes:**

- **Clarifications** (why this step is needed)
- **Mathematical steps**
- **Connections to knowledge graph concepts ("building blocks")**
- **Final structured output that can be used for API responses**

---

## **1. API Gateway (FastAPI)**

### **1.1 Functionality**

✅ Routes requests between the **User, AI Processing Service, and Knowledge Graph**  
✅ **Checks Knowledge Graph first** before calling AI  
✅ Returns the **step-by-step structured solution** including **building blocks**

### **1.2 API Endpoints**

|Endpoint|Method|Description|
|---|---|---|
|`/solve`|`POST`|Checks the Knowledge Graph, then calls AI if needed|
|`/concepts/{problem_id}`|`GET`|Retrieves prerequisite concepts|
|`/user/progress/{user_id}`|`GET`|Fetches user progress|

### **1.3 Inputs & Outputs**

#### **Example Input**

```json
{
  "problem": "For which values of m does the function f(x) = (6m^2 - 12m)x - 5 have no zeroes?"
```
#### Example Output
```json
  "solution": [
    {
      "step": 1,
      "step_explanation": "Identify that the function is a linear function.",
      "math_transformation": "This is a linear function, which follows the formula f(x) = ax + b, where a = (6m^2 - 12m), b = -5.",
      "related_concept": ["Linear Function"]
    },
    {
      "step": 2,
      "step_explanation": "Identify what a zero of a linear function is.",
      "math_transformation": "A zero of a function is the point where it crosses the x-axis.",
      "related_concept": ["Zero of a Linear Function"]
    },
    {
      "step": 3,
      "step_explanation": "For a linear function to have no zeroes, it must be parallel to the x-axis, meaning a = 0 and b ≠ 0.",
      "math_transformation": "For a linear function to have no zeroes, it must be neither increasing nor decreasing. Thus, a = (6m^2 - 12m) = 0 and b = -5 ≠ 0.",
      "related_concept": ["Monotonicity of a Linear Function"]
    },
    {
      "step": 4,
      "step_explanation": "Solve the equation for a.",
      "math_transformation": "We calculate: a = (6m^2 - 12m) = 0, 6m^2 - 12m = 0... Factor out m: 6m(m - 2) = 0.",
      "related_concept": ["Factoring Out"]
    },
    {
      "step": 5,
      "step_explanation": "Solve for m.",
      "math_transformation": "Solving the equation: 6m = 0 or m - 2 = 0.",
      "related_concept": ["Solving Linear Equations"]
    }
  ],
  "final_answer": "m = 0 or m = 2"
}
```

### **1.4 Dependencies**

- **Knowledge Graph Service** (checks for precomputed solutions)
- **AI Processing Service** (parses and solves new problems)
- **User Service** (tracks user progress)

---

## **2. AI Processing Service (Python, SymPy, NLP)**

### **2.1 Functionality**

✅ **Parses complex word problems** using NLP.  
✅ **Generates structured step-by-step solutions** using known problem-solving techniques.  
✅ **Identifies "building blocks"** from the Knowledge Graph.  
✅ **Saves new solutions & decompositions** in the Knowledge Graph for future reuse.

### **2.2 API Endpoints**

|Endpoint|Method|Description|
|---|---|---|
|`/solve`|`POST`|Parses, solves, and structures the solution into steps|
|`/breakdown/{problem_id}`|`GET`|Returns a step-by-step breakdown of the solution|

### **2.3 NLP-Based Problem Understanding**

- **Extract mathematical models from text**
- **Identify the type of problem** (e.g., algebra, optimization, geometry)
- **Determine the solving strategy** (e.g., factoring, differentiation, equation solving)

### **2.4 Dependencies**

- **NLP Engine (spaCy, GPT, SymPy parsing)**
- **Knowledge Graph Service (for prerequisite retrieval)**
- **API Gateway (for handling user requests)**

---

## **3. Knowledge Graph Service (Neo4j)**

### **3.1 Functionality**

✅ Stores **precomputed step-by-step solutions**.  
✅ **Maps each step to a knowledge graph concept ("building blocks").**  
✅ Retrieves **prerequisite concepts** to help users understand the solution better.

### **3.2 API Endpoints**

|Endpoint|Method|Description|
|---|---|---|
|`/concepts/{problem_id}`|`GET`|Fetches prerequisite concepts for a problem|
|`/solution/{problem_id}`|`GET`|Checks if a solution already exists|
|`/store_solution`|`POST`|Stores new solutions in the graph|

### **3.3 Updated Knowledge Graph Structure**

#### **Nodes (Building Blocks)**

- `Function`
    - `Linear Function`
        - `Zero of a Function`
        - `Monotonicity`
- `Algebraic Operations`
    - `Factoring Out`
- `Equations`

#### **Relationships**

```
(Function) → (Linear Function) → (Zero of a Function)
(Function) → (Linear Function) → (Monotonicity)
(Algebraic Operations) → (Factoring Out)
(Equations)
```

### **3.4 Dependencies**

- **AI Service (stores new solutions)**
- **API Gateway (queries for solutions)**

---

## **4. User Service (FastAPI, PostgreSQL)**

### **4.1 Functionality**

✅ Tracks **user learning progress**.  
✅ Stores **solved problems & recommended next topics**.

### **4.2 API Endpoints**

|Endpoint|Method|Description|
|---|---|---|
|`/user/{user_id}`|`GET`|Retrieves user progress|
|`/user/update`|`POST`|Updates learning history|

### **4.3 Dependencies**

- **API Gateway (routes user requests)**

---


---


chatGPT question


okay. I want to create math tutor app. i have found the finetuned and lightweight model https://huggingface.co/unsloth/Qwen2.5-Math-7B-bnb-4bit that solves the math exercises. But i want to create the true tutor, in such a way that the tutor when proposing the solution, associates each step with the math concept or tool that is required to proceed. this way i would allow students to see a bigger picture of math, allow them to polish their math tools and help them acknowledge in which situatians which tools and concepts are used, so that they stop just remembering the solution, but they really grasp the logic behind what they are doing. To do it, i thought i might use the knowledge graph (eg as Neo4j graph) to store all the math concepts needed in primary and high school, organized hierarichically and modeling the dependencies between them. Then, i would like another LLM to assign concepts or tools that were used in each step of the generated solution, from the knowledge graph. How to do it? Is langchain a good framework? please brainstorm with me.










# **✅ Next Steps**

1️⃣ **Would you like me to generate sample API request/response pairs based on this format?**  
2️⃣ **Do you need a Neo4j schema design for storing structured solutions with "building blocks"?**  
3️⃣ **Should I create a `docker-compose.yml` file for setting up the services?**
1️⃣ **Should I generate this format dynamically from an AI model?**  
2️⃣ **Would you like this formatted as a structured JSON output for API responses?**  
3️⃣ **Do you need help structuring the Knowledge Graph in Neo4j to support these building blocks?**
1️⃣ **Would you like me to generate a `docker-compose.yml` file for structuring these services?**  
2️⃣ **Do you need a sample `FastAPI` structure for the Solution Engine?**  
3️⃣ **Would you like a Neo4j schema for storing solutions & concepts?**

Let me know what you'd like to refine next! 🚀



## What is missing

- **User Authentication & Authorization:**
    
    - Implement secure user login, especially for the Administration UI and for tracking user progress.
    - Ensure that only authorized users can modify the knowledge graph or add new problems/solutions.
- **Data Storage and Persistence:**
    
    - Besides Neo4j for the knowledge graph, consider a relational database (e.g., PostgreSQL) for storing user data, progress, and historical records of problem attempts.
    - Define clear data models and schemas for each storage system.
- **Monitoring and Logging:**
    
    - Set up logging for all components (API, Engine, KG operations) to help with debugging and monitoring usage.
    - Consider using a monitoring tool or dashboard to track system performance and error rates.
- **Scalability & Deployment Strategy:**
    
    - Plan for scalability by designing containerized microservices (using Docker) and orchestration (e.g., Kubernetes) when you move beyond prototyping.
    - Consider continuous integration/continuous deployment (CI/CD) pipelines for smoother updates.
- **Testing and Quality Assurance:**
    
    - Develop a suite of automated tests (unit tests, integration tests) for each component to ensure stability as the project grows.
    - Test edge cases in the solution engine (e.g., when a required concept is missing) and validate the KG’s data consistency.
- **User Experience (UX) Design:**
    
    - Design the front-end carefully so that solution steps and linked concepts are presented in an intuitive, interactive way.
    - Consider providing visualizations of the knowledge graph and feedback mechanisms for students to flag confusing steps.
- **Documentation:**
    
    - Create comprehensive documentation for developers and end users (students/teachers). This should include API docs, system architecture diagrams, and user guides.
- **Fallback Mechanisms:**
    
    - Ensure that if the engine cannot map a step to a concept, a fallback explanation or broader concept is provided so the user isn’t left without context.
- **Analytics and Feedback:**
    
    - Implement analytics to track user engagement and identify which concepts or steps are frequently problematic. This can guide future improvements.