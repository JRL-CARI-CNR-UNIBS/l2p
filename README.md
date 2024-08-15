# l2p : LLM-driven PDDL library kit

This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models. This library is an expansion from the survey paper **Leveraging Large Language Models for Automated Planning and Model Construction: A Survey** which can be found [here](https://puginarug.com) (currently under work)

L2P is an offline, NL to PDDL system that supports domain-agnostic planning. It does this via creating an intermediate [PDDL](https://planning.wiki/guide/whatis/pddl) representation of the domain and task, which can then be solved by a classical planner. 

## Usage

This is the general setup to build a domain:
```python
import os
from openai import OpenAI
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.llm_builder import GPT_Chat
from l2p.utils.pddl_parser import prune_predicates, format_types

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None)) # REPLACE WITH YOUR OWN OPENAI API KEY 
model = GPT_Chat(client=client, engine="gpt-4o-mini") # LLM to prompt to

# assumptions
domain_desc = open_file("tests\usage\prompts\blocksworld_domain.txt")
extract_predicates_prompt = open_file("tests\usage\prompts\extract_predicates.txt")
extract_parameters_prompt = open_file("tests\usage\prompts\extract_parameters.txt")
extract_preconditions_prompt = open_file("tests\usage\prompts\extract_preconditions.txt")
extract_effects_prompt = open_file("tests\usage\prompts\extract_effects.txt")

types = {
    "object": "Object is always root, everything is an object",
    "children": [
        {"arm": "mechanical arm that picks up and stacks blocks on other blocks or table.", "children": []},
        {"block": "colored block that can be stacked or stacked on other blocks or table.", "children": []},
        {"table": "surface where the blocks can be placed on top of.", "children": []}
    ]
}

action_name = "stack"
action_desc = "allows the arm to stack a block on top of another block if the arm is holding the top \
    block and the bottom block is clear. After the stack action, the arm will be empty, the top block \
    will be on top of the bottom block, and the bottom block will no longer be clear."

unsupported_keywords = ['object', 'pddl', 'lisp']


# extract predicates
predicates, llm_output = domain_builder.extract_predicates(
    model=model,
    domain_desc=domain_desc,
    prompt_template=extract_predicates_prompt,
    types=types,
    nl_actions={action_name:action_desc}
    )

# extract parameters
params, llm_output = domain_builder.extract_parameters(
    model=model,
    domain_desc=domain_desc,
    prompt_template=extract_parameters_prompt,
    action_name=action_name,
    action_desc=action_desc,
    types=types
    )

# extract preconditions
preconditions, new_predicates, llm_output = domain_builder.extract_preconditions(
    model=model,
    domain_desc=domain_desc,
    prompt_template=extract_preconditions_prompt,
    action_name=action_name,
    action_desc=action_desc,
    params=params,
    predicates=predicates
    )

predicates.extend(new_predicates) # add new predicates

# extract preconditions
effects, new_predicates, llm_output = domain_builder.extract_effects(
    model=model,
    domain_desc=domain_desc,
    prompt_template=extract_effects_prompt,
    action_name=action_name,
    action_desc=action_desc,
    params=params,
    precondition=preconditions,
    predicates=predicates
    )

predicates.extend(new_predicates) # add new predicates

# assemble action model
action = {
    "name": action_name, 
    "parameters": params, 
    "preconditions": preconditions, 
    "effects": effects
    }

# discard predicates not found in action models + duplicates
predicates = prune_predicates(predicates=predicates, actions=[action])

# format types and remove unsupported words
types = format_types(types)
types = {name: description for name, description in types.items() if name not in unsupported_keywords}

# format key info into strings
predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
types_str = "\n".join(types)

# generate PDDL domain
pddl_domain = domain_builder.generate_domain(
    domain="blocksworld_domain", 
    requirements=[':strips',':typing',':equality',':negative-preconditions',
                  ':disjunctive-preconditions',':universal-preconditions',':conditional-effects'],
    types=types_str,
    predicates=predicate_str,
    actions=[action]
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

print(f"PDDL problem: {pddl_problem}")
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
