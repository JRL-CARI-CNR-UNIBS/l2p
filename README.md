# l2p : LLM-driven PDDL library kit

This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models. This library is an expansion from the survey paper **Leveraging Large Language Models for Automated Planning and Model Construction: A Survey** which can be found [here](https://puginarug.com) (currently under work)

L2P is an offline, NL to PDDL system that supports domain-agnostic planning. It does this via creating an intermediate [PDDL](https://planning.wiki/guide/whatis/pddl) representation of the domain and task, which can then be solved by a classical planner. 

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

domain_desc = """BlocksWorld is a planning domain in artificial intelligence. A mechanical robot arm that can pick and place the blocks..."""
role = """Your role is to..."""
technique = """Your technique is... CoT"""
examples = ["example_1", "example_2", "..."]

prompt = PromptBuilder(role=role, technique=technique, examples=examples, task=task)
domain = DomainBuilder()
task = TaskBuilder()
feedback = FeedbackBuilder()


types, response = domain.extract_type(model, domain_desc, prompt.generate_prompt())
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

problem_desc= """Your task is to rearrange the blocks..."""

objects, initial_states, goal_states, llm_response = task.extract_task(
    model=model,
    problem_desc=problem_desc,
    domain_desc=domain_desc,
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
Currently, this repo has been tested for Python 3.12.2.

You can set up a Python environment using either [Conda](https://conda.io) or [venv](https://docs.python.org/3/library/venv.html) and install the dependencies via the following steps.

**Conda**
```
conda create -n L2P python=3.12.2
conda activate L2P
pip install -r requirements.txt
```

**venv**
```
python3.12.2 -m venv env
source env/bin/activate
pip install -r requirements.txt
``` 

These environments can then be exited with `conda deactivate` and `deactivate` respectively. The instructions below assume that a suitable environemnt is active. 

**API keys**
L2P requires access to an LLM. Currently, it only supports OpenAI's GPT-series models. To configure these, provide the necessary API-key in an environment variable.

**OpenAI**
```
export OPENAI_API_KEY='YOUR-KEY' # e.g. OPENAI_API_KEY='sk-123456'
```

Refer to [here](https://platform.openai.com/docs/quickstart) for more information.

## Current Works Reconstructed Using L2P
The following are papers that have been reconstructed so far. This list will be updated in the future.

- [x] `NL2Plan`
- [x] `LLM+DM` 
- [x] `LLM+P`
- [x] `PROC2PDDL`
- [ ] `LLM+EW`
- [ ] `LLM+consistency`

## Current Model Construction Works
This section provides a taxonomy of research within Model Construction. For more detailed overview, visit our [paper](https://puginarug.com).

**Model Generation**
- **""** et al. (year) [paper]() [code]()

**Model Editing**
- **""** et al. (year) [paper]() [code]()

**Other NL-PDDL Translation Tasks**
- **""** et al. (year) [paper]() [code]()

## Contact
Please contact `20mt1@queensu.ca` for questions, comments, or feedback about the L2P library.
