import os
from openai import OpenAI
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.llm_builder import GPT_Chat
from l2p.utils.pddl_parser import prune_predicates

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None)) # REPLACE WITH YOUR OWN OPENAI API KEY 
model = GPT_Chat(client=client, engine="gpt-4o-mini") # LLM to prompt to


# assumptions
domain_desc = """BlocksWorld is a planning domain ..."""

types = {
    "arm": "mechanical arm that picks up and stacks blocks on other blocks or table.",
    "block": "block that can be stacked or stacked on other blocks or table.",
    "table": "surface where the blocks can be placed on top of."
}

action_name = "stack"
action_desc = "allows the arm to stack a block on top of another block if the arm is holding the top \
    block and the bottom block is clear. After the stack action, the arm will be empty, the top block \
        will be on top of the bottom block, and the bottom block will no longer be clear."
        


# extract predicates
predicates, llm_output = domain_builder.extract_predicates(
    model=model,
    domain_desc=domain_desc,
    prompt_template="Your task is to extract predicates ... ",
    types=types
    )

# extract parameters
params, llm_ouput = domain_builder.extract_parameters(
    model=model,
    domain_desc=domain_desc,
    prompt_template="Your task is to extract parameters ... ",
    action_name=action_name,
    action_desc=action_desc,
    types=types
    )

# extract preconditions
preconditions, new_predicates, llm_output = domain_builder.extract_preconditions(
    model=model,
    domain_desc=domain_desc,
    prompt_template="Your task is to extract preconditions ... ",
    action_name=action_name,
    action_desc=action_desc,
    params=params,
    predicates=predicates
    )

predicates.extend(new_predicates) # add new predicates

# extract preconditions
effects, new_predicates, llm_ouput = domain_builder.extract_effects(
    model=model,
    domain_desc=domain_desc,
    prompt_template="Your task is to extract effects ... ",
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