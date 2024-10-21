"""
Paper: "PROC2PDDL: Open-Domain Planning Representations from Texts" Zhang et al. (2024)
Source code: https://github.com/zharry29/proc2pddl
Run: python3 -m paper_reconstructions.proc2pddl.proc2pddl
"""

import os, json
from l2p import *
from tests.planner import FastDownward
from tests.setup import check_parse_domain

def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

engine = "gpt-4o-mini"
api_key = os.environ.get('OPENAI_API_KEY')
openai_llm = OPENAI(model=engine, api_key=api_key)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()
prompt_builder = PromptBuilder()
planner = FastDownward()

# annotated original domain header
types = load_json('paper_reconstructions/proc2pddl/prompts/types.json')
predicates = load_json('paper_reconstructions/proc2pddl/prompts/predicates.json')
nl_actions = load_json('paper_reconstructions/proc2pddl/prompts/nl_actions.json')

if __name__ == "__main__":
    
    unsupported_keywords = ['object', 'pddl', 'lisp']
    
    # retrieve wikihow text
    domain_desc = load_file('paper_reconstructions/proc2pddl/prompts/wikihow.txt')

    # ZPD prompt
    role = load_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/role.txt')
    technique = load_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/technique.txt')
    example = load_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/example.txt')
    task = "here are the actions I want:\n" + (str(nl_actions)) + "\n\nhere are the types I have:\n" + format_dict(types) \
        + "\n\nhere are the predicates I have:\n" + format_predicates(predicates)
    ZPD_prompt = PromptBuilder(role=role, technique=technique, examples=[example], task=task)

    # (1) query LLM for ZPD information
    action_descriptions = openai_llm.query(prompt=ZPD_prompt.generate_prompt())
    
    # PDDL extraction prompt
    role = load_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/role.txt')
    example = load_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/example.txt')
    task = load_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/task.txt')
    task += "\n\nhere are the action descriptions to use:\n" + action_descriptions
    pddl_extract_prompt = PromptBuilder(role=role, examples=[example], task=task)
    
    # (2) extract PDDL requirements
    actions, _, llm_response = domain_builder.extract_pddl_actions(
        model=openai_llm,
        domain_desc=domain_desc,
        prompt_template=pddl_extract_prompt.generate_prompt(),
        nl_actions=nl_actions,
        predicates=predicates,
        types=types
        )

    types = format_types(types) # retrieve types
    pruned_types = {name: description for name, description in types.items() if name not in unsupported_keywords} # remove unsupported words
    
    # format strings
    predicate_str = "\n".join([pred["clean"] for pred in predicates])
    types_str = "\n".join(pruned_types)

    requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

    # generate domain
    pddl_domain = domain_builder.generate_domain(
        domain="survive_deserted_island", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )

    domain_file = "paper_reconstructions/proc2pddl/results/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
        
    # parse PDDL files
    pddl_domain = check_parse_domain(domain_file)
    with open(domain_file, "w") as f:
        f.write(pddl_domain)

    print("PDDL domain:\n", pddl_domain)
    
    problem_file = load_file("paper_reconstructions/proc2pddl/results/problems/problem-catch_cook_fish.pddl")
    
    # run planner
    planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    