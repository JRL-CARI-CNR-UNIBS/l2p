# l2p : LLM-driven PDDL library kit

This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models.

## Usage

This is the general setup:
```python
import os
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None)) # REPLACE WITH YOUR OWN OPENAI API KEY 
model = GPT_Chat(client=client, engine="gpt-4o-mini")

domain_description = """BlocksWorld is a planning domain in artificial intelligence. A mechanical robot arm that can pick and place the blocks..."""
role = """Your role is to..."""
technique = """Your technique is... CoT"""
examples = ["example_1", "example_2", "..."]

prompt = PromptBuilder(role=role, technique=technique, examples=examples, task=task)
domain = DomainBuilder()
task = TaskBuilder()
feedback = FeedbackBuilder()


types, response = domain.extract_type(model, domain_description, prompt.generate_prompt())
domain.set_types(types=types)

type_hierarchy, response = domain.extract_type_hierarchy(model, domain_desc, prompt.generate_prompt(), domain.get_types())    
domain.set_type_hierarchy(type_hierarchy=type_hierarchy)

.
.
.

# generate domain
requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

pddl_domain = domain.generate_domain(
    domain="test_domain", 
    requirements=requirements,
    types=types_str,
    predicates=predicate_str,
    actions=actions
    )

print(f"PDDL domain: {pddl_domain}")
```

Here is how you would setup a PDDL problem:
```python

problem_description = """Your task is to rearrange the blocks..."""

objects, initial, goal, llm_response = task.extract_task(
    model=model,
    problem_desc=problem_description,
    domain_desc=domain_description,
    prompt_template=prompt.generate_prompt(),
    types=types,
    predicates=predicates,
    actions=actions
    )

pddl_problem = task.generate_task(domain="test_domain", objects=objects, initial=initial_states, goal=goal_states)

print(f"PDDL domain: {pddl_problem}")
```

Here is how you would setup a Feedback Mechanism:
```python
feedback_template = """Here is the checklist I want you to perform..."""

new_types, feedback_response = feedback.type_feedback(
    model=model, 
    domain_desc=domain_description, 
    feedback_template=feedback_template, 
    feedback_type="llm", 
    types=types, 
    llm_response=response)

print("FEEDBACK:\n", feedback_response)
```


## Installation and Setup

## Running Experiments

## Current Works Reconstructed Using L2P
- [x] `NL2Plan`
- [x] `LLM+DM` 
- [x] `LLM+P`
- [ ] `PROC2PDDL`
- [ ] `LLM+EW`

## Current Model Construction Works
