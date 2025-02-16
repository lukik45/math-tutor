


Flow:
1. User input
	1. text
	2. photo
2. solve the problem using LLM
3. Annotation (Mapping module)
	1. annotate the step with required math concepts
4. structured output (yaml)
	2. human readable explanation
	3. mathematical transformation
	4. associated math concepts


## Handling missing concepts
- omit
- fall back to a broader category
- generate and log (the administrators can review the proposition of adding this concept to the KG)



## How to enable the NLP model to see the knowledge graph

Solution 1 - an access to the KG

Solution 2 - a mapping schema

## Dynamic linking
- Knowledge graph serves as the authoritative source for math concepts. The solution engine uses it to ensure each solution step is linked with the correct, deep-level concept