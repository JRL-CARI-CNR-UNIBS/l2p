"""
Paper: "NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions" Gestrin et al (2024)
Source code: https://github.com/mrlab-ai/NL2Plan
Run: python3 -m tests.paper_reconstructions.nl2plan
"""

import os, json
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.utils.pddl_parser import prune_predicates, prune_types, extract_types


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

# open and create type extraction prompt builder class
role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
task_desc = open_file('data/prompt_templates/type_extraction/task.txt')
type_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create type hierarchy prompt builder class
role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')
type_hierarchy_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create NL action prompt builder class      
role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
task_desc = open_file('data/prompt_templates/action_extraction/task.txt')
nl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create PDDL action prompt builder class
role_desc = open_file('data/prompt_templates/action_construction/extract_action/role.txt')
tech_desc = open_file('data/prompt_templates/action_construction/extract_action/technique.txt')
task_desc = open_file('data/prompt_templates/action_construction/extract_action/task.txt')
pddl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create compact action prompt builder class
role_desc = open_file('data/prompt_templates/task_extraction/extract_task/role.txt')
tech_desc = open_file('data/prompt_templates/task_extraction/extract_task/technique.txt')
task_desc = open_file('data/prompt_templates/task_extraction/extract_task/task.txt')
task_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()







if __name__ == "__main__":
    
    unsupported_keywords = ['object', 'pddl', 'lisp']
    
    # STEP ONE: type extraction
    types, response = domain_builder.extract_type(model, domain_desc, type_extraction_prompt.generate_prompt())
    domain_builder.set_types(types)

    feedback_template = open_file('data/prompt_templates/type_extraction/feedback.txt')
    new_types, feedback_response = feedback_builder.type_feedback(model, domain_desc, feedback_template, "llm", types, response)
    if new_types != None: 
        domain_builder.set_types(new_types)
        
    print("Types:", format_json_output(domain_builder.get_types()))


    # STEP TWO: type hierarchy extraction
    type_hierarchy, response = domain_builder.extract_type_hierarchy(model, domain_desc, type_hierarchy_prompt.generate_prompt(), domain_builder.get_types())
    domain_builder.set_type_hierarchy(type_hierarchy)

    feedback_template = open_file('data/prompt_templates/hierarchy_construction/feedback.txt')
    new_type_hierarchy, feedback_response = feedback_builder.type_hierarchy_feedback(model, domain_desc, feedback_template, "llm", type_hierarchy, response)
    if new_type_hierarchy != None: 
        domain_builder.set_type_hierarchy(new_type_hierarchy)
        
    print("Type Hierarchy", format_json_output(domain_builder.get_type_hierarchy()))


    # STEP THREE: action extraction
    nl_actions, response = domain_builder.extract_nl_actions(model, domain_desc, nl_action_extraction_prompt.generate_prompt(), domain_builder.get_type_hierarchy())
    domain_builder.set_nl_actions(nl_actions)

    feedback_template = open_file('data/prompt_templates/action_extraction/feedback.txt')
    new_nl_actions, feedback_response = feedback_builder.nl_action_feedback(model, domain_desc, feedback_template, "llm", nl_actions, response)
    if new_nl_actions != None:
        domain_builder.set_nl_actions(new_nl_actions)

    print("Natural Language Actions")    
    for i in nl_actions: print(i)


    # STEP FOUR: action construction
    feedback_template = open_file('data/prompt_templates/action_construction/extract_action/feedback.txt')

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
                predicates
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
    # pddl_domain = domain_builder.generate_domain("test_domain", requirements, types_str, predicate_str, actions)
    
    pddl_domain = domain_builder.generate_domain(
        domain="test_domain", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )

    domain_file = "data/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)


    # STEP FIVE: task extraction
    feedback_template = open_file('data/prompt_templates/task_extraction/extract_task/feedback.txt')

    objects, initial, goal, llm_response = task_builder.extract_task(
        model,
        problem_desc,
        domain_desc,
        task_extraction_prompt.generate_prompt(),
        types,
        predicates,
        actions
        )

    for _ in range(2):
        feedback_objects, feedback_initial, feedback_goal, llm_feedback_response = feedback_builder.task_feedback(
            model, 
            problem_desc, 
            feedback_template,
            "llm",
            predicates,
            types,
            objects,
            initial,
            goal,
            llm_response
            )

        if feedback_objects != None:
                objects=feedback_objects
                initial=feedback_initial
                goal=feedback_goal
        else:
            break

    objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
    pddl_problem = task_builder.generate_task("test_domain", objects, initial, goal)

    problem_file = "data/problem.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)