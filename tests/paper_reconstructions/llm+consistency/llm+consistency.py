"""
Paper: "Generating consistent PDDL domains with Large Language Models" Smirnov et al (2024)
Source code: N/A
Run: python3 -m tests.paper_reconstructions.llm+consistency.llm+consistency
"""

import os, json
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.utils.pddl_validator import SyntaxValidator
from l2p.utils.pddl_parser import prune_predicates, prune_types, extract_types
from planner import FastDownward
from setup import check_parse_domain, check_parse_problem


def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def format_json_output(data):
        return json.dumps(data, indent=4)


# engine = "gpt-3.5-turbo-0125"
engine = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
model = GPT_Chat(client=client, engine=engine)

domain_desc = open_file('data/domains/blocksworld.txt')
problem_desc = open_file("data/problems/blocksworld_p1.txt")

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()
validator = SyntaxValidator()
planner = FastDownward()

extract_task_prompt = ""
nl_conditions_extraction_prompt = ""
nl_actions_extraction_prompt = ""

if __name__ == "__main__":
    
    """Generating textual goal plan (step 1)"""
    
    # extract natural language conditions (initial and goal state)
    nl_conditions = task_builder.extract_nl_conditions(model, problem_desc, domain_desc, nl_conditions_extraction_prompt)
    
    plan_prompt = "I want you to extract a sequence of actions (to appear in a plan) \
        given the initial state, to reach the given goal state. Here is the initial and goal state in CoT format:\n\n" + \
            "NATURAL LANGUAGE CONDITIONS:\n" + nl_conditions
    
    # extract sequence of actions (to appear in a plan)
    seq_actions = model.get_output(prompt=plan_prompt)
    
    # write list of identified actions to extract preconditons and effects
    nl_actions = domain_builder.extract_nl_actions(model, domain_desc, nl_actions_extraction_prompt.set_task(seq_actions))
    
    # extract constraints of the problem
    constraints_prompt = "I want you to identify the constraints of the problem (e.g. connectivity between locations, actor-action \
        relations, object properties or states, ... ) given the natural language description of the initial and goal state, and the \
            actions list:\n\nCONDITIONS:\n" + nl_conditions + "\n\nACTIONS:\n" + nl_actions 
            
    constraints = model.get_output(prompt=constraints_prompt)
    input = nl_conditions + nl_actions + constraints # combine all textual definition
    
    
    """Generating domain markup (step 2) + Initial consistency checks (step 3.1) + Error correction loop (step 3.2)"""
    # extract types
    types, response = domain_builder.extract_type(model, domain_desc, type_extraction_prompt.generate_prompt())
    domain_builder.set_types(types)

    # extract types hierarchy
    type_hierarchy, response = domain_builder.extract_type_hierarchy(model, domain_desc, type_hierarchy_prompt.generate_prompt(), domain_builder.get_types())
    domain_builder.set_type_hierarchy(type_hierarchy)
        
    predicates = []
    max_iters = 3
    for _ in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():
            action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                model,
                pddl_action_extraction_prompt.generate_prompt(),
                action_name,
                action_desc,
                predicates,
                type_hierarchy
            )

            # RUN FEEDBACK
            feedback_action, feedback_predicates, llm_feedback_response = feedback_builder.pddl_action_feedback(
                model, 
                domain_desc, 
                feedback_template, 
                "llm",
                action, 
                predicates, 
                types, 
                llm_response
                )
            
            if feedback_action != None:
                action=feedback_action
                new_predicates=feedback_predicates

            actions.append(action)
            predicates.extend(new_predicates)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    predicates = prune_predicates(predicates=predicates, actions=actions) # discard predicates not found in action models + duplicates
    types = extract_types(type_hierarchy) # retrieve types
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions) # discard types not in predicates / actions + duplicates
    pruned_types = {name: description for name, description in pruned_types.items() if name not in unsupported_keywords} # remove unsupported words
    
    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    types_str = "\n".join(pruned_types)

    requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

    pddl_domain = domain_builder.generate_domain(
        domain="test_domain", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )

    # generate problem markup
    objects, initial, goal, llm_response = task_builder.extract_task(
        model,
        problem_desc,
        domain_desc,
        task_extraction_prompt.generate_prompt(),
        types,
        predicates,
        actions
        )

    objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
    pddl_problem = task_builder.generate_task("test_domain", objects, initial, goal)

    
    # write in files
    problem_file = "tests/paper_reconstructions/llm+consistency/results/problem.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)
        
    domain_file = "tests/paper_reconstructions/llm+consistency/results/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
        
        
    # parse PDDL files
    pddl_domain = check_parse_domain(domain_file)
    with open(domain_file, "w") as f:
        f.write(pddl_domain)

    pddl_problem = check_parse_problem(problem_file)
    with open(problem_file, "w") as f:
        f.write(pddl_problem)
    
    """Reachability analysis (step 4)"""
    # run planner
    plan_success, output = planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    
    if plan_success == False:
        # run reachability analysis
        pass