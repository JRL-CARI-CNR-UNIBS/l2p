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

print(pddl_domain)