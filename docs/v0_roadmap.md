## Project Roadmap and Task List

### **Phase 1: Design and Planning**

- [ ] **Requirement Gathering:**
    - [x] Define detailed functional requirements (e.g., solution generation, concept mapping, user interactions).
    - [ ] Gather non-functional requirements (scalability, response times, maintainability).

- [ ] **System Design:**
    - [x] Create high-level architecture diagrams.
    - [ ] Define API endpoints (for problem submission, solution retrieval, KG management, etc.).
    - [ ] Decide on technology stack for each component (e.g., Neo4j for KG, FastAPI for API, LangChain for the engine, React/Streamlit for UI).

- [ ] **Data Modeling:**
    - [ ] Design the schema for your knowledge graph (concept nodes, prerequisite relationships, problem nodes, solution nodes, and step nodes).
    - [ ] Create sample YAML files for concepts, problems, and solutions.

### **Phase 2: Prototype Development**

- [ ] **Set Up KG:**
    - [ ] Deploy Neo4j locally (or in Docker) using your YAML files to initialize the graph.
    - [ ] Develop scripts to load and update the KG.

- [ ] **Build the Engine:**
    - [ ] Integrate LangChain (or another framework) with your fine-tuned LLM to generate step-by-step solutions.
    - [ ] Develop the mapping mechanism to link solution steps with KG concepts.
    - [ ] Create endpoints for the Engine (e.g., a `/solve` API).

- [ ] **Develop the API Gateway:**
    - [ ] Build API endpoints (using FastAPI or similar) that expose the Engine, KG, and admin functionalities.

- [ ] **Build a Basic UI:**
    - [ ] Develop a simple web interface for users to input problems and view solutions.
    - [ ] Create an admin interface for managing the KG and problem/solution data.

### **Phase 3: Testing and Refinement**

- [ ] **Integration Testing:**
    - [ ] Test interactions between the Engine, API, KG, and UI.
    - [ ] Verify that each solution step is correctly annotated with KG concepts.
    - [ ] Validate error handling (e.g., when a concept link fails).

- [ ] **Performance Testing:**
    - [ ] Ensure the LLM inference, KG queries, and overall response time meet your requirements.
    - [ ] Optimize bottlenecks (e.g., use quantization, caching, or batching if necessary).

- [ ] **User Feedback:**
    - [ ] Run a pilot test with students or educators.
    - [ ] Gather feedback on clarity, usability, and educational value.
    - [ ] Iterate on the design based on user feedback.

### **Phase 4: Deployment**

- [ ] **Deployment Setup:**
    - [ ] For initial low usage, a cloud-based, pay-as-you-go setup (e.g., using Hugging Face Inference API, a small Neo4j instance, and cloud hosting for your API) may suffice.
    - [ ] Plan for scalability as user numbers grow.

- [ ] **Monitoring and Maintenance:**
    - [ ] Set up logging and monitoring for all services.
    - [ ] Schedule regular updates and maintenance for the KG and the engine.

---

## **Summary of Requirements per Component**

- [ ] **Knowledge Graph (Neo4j):**
    - [ ] Data Model: Concepts, problems, solutions, steps, prerequisite relationships.
    - [ ] API: Endpoints for reading, adding, updating, and deleting nodes and relationships.
    - [ ] Deployment: Local (Docker) or cloud (Neo4j Aura Free) initially.

- [ ] **Engine (LLM + LangChain):**
    - [ ] Model: Fine-tuned math model (e.g., Qwen2.5-Math-7B-bnb-4bit).
    - [ ] Functionality: Generate step-by-step solutions and annotate with KG concepts.
    - [ ] Integration: API to send problem text and receive annotated solution.

- [ ] **User Interface:**
    - [ ] Front-End: Web application (e.g., React, Streamlit) for problem input and solution display.
    - [ ] User Experience: Clear display of each step with linked concepts, interactive exploration of the KG.

- [ ] **Administration Interface:**
    - [ ] Functionality: Tools to modify the KG, add/update problems and solutions.
    - [ ] Integration: Uses API endpoints to manage the underlying data in Neo4j.

- [ ] **API Gateway:**
    - [ ] Framework: FastAPI (or similar) to provide RESTful endpoints.
    - [ ] Responsibilities: Routing requests between UI, Engine, and KG; managing authentication, rate limiting, and logging.
