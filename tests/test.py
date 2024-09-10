import os, json
from openai import OpenAI
from l2p import *

def load_file(file_path):
    _, ext = os.path.splitext(file_path)
    with open(file_path, 'r') as file:
        if ext == '.json': return json.load(file)
        else: return file.read().strip()

domain_builder = DomainBuilder()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None)) # REPLACE WITH YOUR OWN OPENAI API KEY 
model = get_llm(engine="gpt", model="gpt-4o-mini", client=client)

# load in assumptions
domain_desc = load_file(r'tests/usage/prompts/domain/blocksworld_domain.txt')
extract_predicates_prompt = load_file(r'tests/usage/prompts/domain/extract_predicates.txt')
types = load_file(r'tests/usage/prompts/domain/types.json')
action = load_file(r'tests/usage/prompts/domain/action.json')

# extract predicates via LLM
predicates, llm_output = domain_builder.extract_predicates(
    model=model,
    domain_desc=domain_desc,
    prompt_template=extract_predicates_prompt,
    types=types,
    nl_actions={action['action_name']: action['action_desc']}
    )

# format key info into PDDL strings
predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])

print(f"PDDL domain predicates:\n{predicate_str}")

task_builder = TaskBuilder()

# load in assumptions
problem_desc= load_file(r'tests/usage/prompts/problem/blocksworld_problem.txt')
extract_task_prompt = load_file(r'tests/usage/prompts/problem/extract_task.txt')

# extract PDDL task specifications via LLM
objects, initial_states, goal_states, llm_response = task_builder.extract_task(
    model=model,
    problem_desc=problem_desc,
    prompt_template=extract_task_prompt,
    types=types,
    predicates=predicates
    )

# format key info into PDDL strings
objects_str = task_builder.format_objects(objects)
initial_str = task_builder.format_initial(initial_states)
goal_str = task_builder.format_goal(goal_states)

# generate task file
pddl_problem = task_builder.generate_task("blocksworld_problem", objects_str, initial_str, goal_str)

print(f"PDDL problem: {pddl_problem}")

feedback_builder = FeedbackBuilder()

feedback_template = load_file(r'tests/usage/prompts/problem/feedback.txt')

objects, initial, goal, feedback_response = feedback_builder.task_feedback(
    model=model, 
    problem_desc=problem_desc, 
    feedback_template=feedback_template, 
    feedback_type="llm", 
    predicates=predicates,
    types=types, 
    llm_response=llm_response)

print("FEEDBACK:\n", feedback_response)