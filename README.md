# l2p : LLM-driven PDDL library kit

This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models.

## Usage
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
technique = """Your technique is..."""
examples = ["example_1", "example_2", "..."]

prompt = PromptBuilder(role=role, technique=tech, examples=examples, task=task)
domain = DomainBuilder()
task = TaskBuilder()
feedback = FeedbackBuilder()


types, response = domain.extract_type(model, domain_description, prompt.generate_prompt())
domain.set_types(types=types)

type_hierarchy, response = domain_builder.extract_type_hierarchy(model, domain_desc, prompt.generate_prompt(), domain.get_types())    
domain.set_type_hierarchy(type_hierarchy=type_hierarchy)

.
.
.

requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

pddl_domain = domain_builder.generate_domain(
    domain="test_domain", 
    requirements=requirements,
    types=types_str,
    predicates=predicate_str,
    actions=actions
    )

print(f"PDDL domain written to {pddl_domain}")
```

## Installation and Setup

## Running Experiments

## Current Works
- [x] `NL2Plan`
- [x] `LLM+DM`
- [x] `LLM+P`
- [ ] `LLM+DP`
- [ ] `LLM+EW`