import os, json
from openai import OpenAI
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.llm_builder import GPT_Chat
from l2p.utils.pddl_parser import prune_predicates, format_types
from tests.setup import check_parse_domain

def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()

# engine = "gpt-4o"
# engine = "gpt-3.5-turbo-0125"
engine = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None)) # REPLACE WITH YOUR OWN OPENAI API KEY 
model = GPT_Chat(client=client, engine=engine) # LLM to prompt to

# load in assumptions
domain_desc = load_file('tests/usage/prompts/blocksworld_domain.txt')
extract_predicates_prompt = load_file('tests/usage/prompts/extract_predicates.txt')
extract_parameters_prompt = load_file('tests/usage/prompts/extract_parameters.txt')
extract_preconditions_prompt = load_file('tests/usage/prompts/extract_preconditions.txt')
extract_effects_prompt = load_file('tests/usage/prompts/extract_effects.txt')
types = load_json('tests/usage/prompts/types.json')
action = load_json('tests/usage/prompts/action.json')
action_name = action['action_name']
action_desc = action['action_desc']

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
params, params_raw, llm_output = domain_builder.extract_parameters(
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
    params=params_raw,
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
    params=params_raw,
    precondition=preconditions,
    predicates=predicates
    )

predicates.extend(new_predicates) # add new predicates

# assemble action model
action = {
    'name': action_name, 
    'parameters': params, 
    'preconditions': preconditions, 
    'effects': effects
    }

# discard predicates not found in action models + duplicates
predicates = prune_predicates(predicates=predicates, actions=[action])

# format types and remove unsupported words
types = format_types(types)
types = {name: description for name, description in types.items() if name not in unsupported_keywords}

# format key info into strings
predicate_str = '\n'.join([pred['clean'].replace(':', ' ; ') for pred in predicates])
types_str = '\n'.join(types)

# generate PDDL domain
pddl_domain = domain_builder.generate_domain(
    domain='blocksworld_domain', 
    requirements=[':strips',':typing',':equality',':negative-preconditions',
                  ':disjunctive-preconditions',':universal-preconditions',':conditional-effects'],
    types=types_str,
    predicates=predicate_str,
    actions=[action]
    )

domain_file_path = 'tests/usage/results/domain.pddl'

with open(domain_file_path, "w") as f:
        f.write(pddl_domain)

pddl_domain = check_parse_domain(domain_file_path)
print("PDDL domain:\n", pddl_domain)

with open(domain_file_path, "w") as f:
    f.write(pddl_domain)