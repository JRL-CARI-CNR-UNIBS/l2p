# IntelliPDDL : LLM-driven PDDL library kit

This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models.

## Usage
```python
from NLtoPDDL import NLtoPDDLModel

# initialize model
model = NLtoPDDLModel(model='gpt-2') # utilizes huggingface API

# prompt from: https://github.com/GuanSuns/LLMs-World-Models-for-Planning/blob/main/prompts/common/action_description_prompt.txt
domain_prompt = """
You are defining the domain (i.e. preconditions and effects) represented in PDDL format of an AI agent's actions...

Domain information:
BlocksWorld is a planning domain in artificial intelligence. The AI agent here is a mechanical robot arm that 
can pick and place the blocks...

Here is an example from the classical BlocksWorld domain for demonstrating the output format: [EXAMPLE]
[INSERT OTHER PROMPT TECHNIQUES (CoT, Self-reflection, naming conventions, etc.)]
"""

domain_prompts = ["Problem description:", "Domain description:", ["Example 1:", "Example 2:"], "Additional Instructions:"]
problem_prompt = """Here is the task..."""

# convert prompt to PDDL
pddl_domain = model.convert(domain_prompt) # single conversation
pddl_problem = model.convert(problem_prompt)
pddl_domain2, pddl_problem2 = model.convert_both(domain_prompt, problem_prompt) # combines both
model.print_pddl_file(pddl_domain) # output PDDL domain

# other library functions
model.convert_batch(domain_prompts) # multiple conversations

verified, feedback = model.verify(pddl_domain, verifier='VAL') # returns boolean + string w/ feedback via external verifier
model.refine(pddl_domain, feedback) # returns refined PDDL domain file (either human-in-loop or external verifier feedback)
validated, response = model.validate_plan(pddl_domain, pddl_problem)

model.get_fluents(pddl_domain) # extract predicates from generated PDDL domain file
actions = model.get_actions(pddl_domain) # extract actions in a list from generated PDDL domain file
model.get_preconditions(actions[0]) # extract preconditions from specific action in generated PDDL domain file
model.get_effects(actions[0]) # extract effects from generated PDDL domain file

model.get_objects(pddl_problem)
model.get_initial_state(pddl_problem)
model.get_goal_state(pddl_problem)

model.save_pddl_file(pddl_domain, "path/blocksworld_experiment.pddl")
pddl_domain = model.load_pddl_file("path/blocksworld_experiment.pddl")
model.swap_model(model='meta-llama/Llama-2-7b-hf')
model.get_llm()
```

## Installation and Setup

## Running Experiments
