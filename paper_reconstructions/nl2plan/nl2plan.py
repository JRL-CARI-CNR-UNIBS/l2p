"""
Paper: "NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions" Gestrin et al (2024)
Source code: https://github.com/mrlab-ai/NL2Plan
Run: python3 -m paper_reconstructions.nl2plan.nl2plan
"""

import os, json
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.utils.pddl_parser import prune_predicates, prune_types, format_types
from tests.planner import FastDownward
from tests.setup import check_parse_domain, check_parse_problem


def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def format_json_output(data):
        return json.dumps(data, indent=4)

# engine = "gpt-4o"
# engine = "gpt-3.5-turbo-0125"
engine = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
model = GPT_Chat(client=client, engine=engine)

domain_desc = open_file('data/domains/blocksworld.txt')
problem_desc = open_file("data/problems/blocksworld_p1.txt")

# open and create type extraction prompt builder class
role_desc = open_file('paper_reconstructions/nl2plan/prompts/type_extraction/role.txt')
tech_desc = open_file('paper_reconstructions/nl2plan/prompts/type_extraction/technique.txt')
task_desc = open_file('paper_reconstructions/nl2plan/prompts/type_extraction/task.txt')
type_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create type hierarchy prompt builder class
role_desc = open_file('paper_reconstructions/nl2plan/prompts/hierarchy_construction/role.txt')
tech_desc = open_file('paper_reconstructions/nl2plan/prompts/hierarchy_construction/technique.txt')
task_desc = open_file('paper_reconstructions/nl2plan/prompts/hierarchy_construction/task.txt')
type_hierarchy_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create NL action prompt builder class      
role_desc = open_file('paper_reconstructions/nl2plan/prompts/action_extraction/role.txt')
tech_desc = open_file('paper_reconstructions/nl2plan/prompts/action_extraction/technique.txt')
task_desc = open_file('paper_reconstructions/nl2plan/prompts/action_extraction/task.txt')
nl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create PDDL action prompt builder class
role_desc = open_file('paper_reconstructions/nl2plan/prompts/action_construction/role.txt')
tech_desc = open_file('paper_reconstructions/nl2plan/prompts/action_construction/technique.txt')
task_desc = open_file('paper_reconstructions/nl2plan/prompts/action_construction/task.txt')
pddl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create compact action prompt builder class
role_desc = open_file('paper_reconstructions/nl2plan/prompts/task_extraction/role.txt')
tech_desc = open_file('paper_reconstructions/nl2plan/prompts/task_extraction/technique.txt')
task_desc = open_file('paper_reconstructions/nl2plan/prompts/task_extraction/task.txt')
task_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()
planner = FastDownward()



if __name__ == "__main__":
    
    unsupported_keywords = ['object', 'pddl', 'lisp']
    
    # STEP ONE: type extraction
    types, response = domain_builder.extract_type(model, domain_desc, type_extraction_prompt.generate_prompt())

    feedback_template = open_file('paper_reconstructions/nl2plan/prompts/type_extraction/feedback.txt')
    types, feedback_response = feedback_builder.type_feedback(
        model=model, 
        domain_desc=domain_desc, 
        feedback_template=feedback_template, 
        feedback_type="llm", 
        types=types, 
        llm_response=response)

    domain_builder.set_types(types)
        
    print("Types:", format_json_output(domain_builder.get_types()))


    # STEP TWO: type hierarchy extraction
    type_hierarchy, response = domain_builder.extract_type_hierarchy(
         model, 
         domain_desc, 
         type_hierarchy_prompt.generate_prompt(), 
         domain_builder.get_types())

    feedback_template = open_file('paper_reconstructions/nl2plan/prompts/hierarchy_construction/feedback.txt')
    type_hierarchy, feedback_response = feedback_builder.type_hierarchy_feedback(
         model, 
         domain_desc, 
         feedback_template, 
         "llm", 
         type_hierarchy, 
         response)
        
    domain_builder.set_type_hierarchy(type_hierarchy)
        
    print("Type Hierarchy", format_json_output(domain_builder.get_type_hierarchy()))


    # STEP THREE: action extraction
    nl_actions, response = domain_builder.extract_nl_actions(model, domain_desc, nl_action_extraction_prompt.generate_prompt(), domain_builder.get_type_hierarchy())

    feedback_template = open_file('paper_reconstructions/nl2plan/prompts/action_extraction/feedback.txt')
    nl_actions, feedback_response = feedback_builder.nl_action_feedback(
        model, 
        domain_desc, 
        feedback_template, 
        "llm", 
        nl_actions, 
        response, 
        domain_builder.get_type_hierarchy())
        
    domain_builder.set_nl_actions(nl_actions)

    print("Natural Language Actions")    
    for i in nl_actions: print(i)


    # STEP FOUR: action construction
    feedback_template = open_file('paper_reconstructions/nl2plan/prompts/action_construction/feedback.txt')

    predicates = []
    max_iters = 1
    for _ in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():
            
            # retrieve rest of list
            action_list = {a_name: a_desc for a_name, a_desc in nl_actions.items() if a_name != action_name}
            
            action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                model,
                domain_desc,
                pddl_action_extraction_prompt.generate_prompt(),
                action_name,
                action_desc,
                action_list,
                predicates,
                type_hierarchy
            )

            # RUN FEEDBACK
            action, new_predicates, llm_feedback_response = feedback_builder.pddl_action_feedback(
                model, 
                domain_desc, 
                feedback_template, 
                "llm",
                action, 
                predicates, 
                types, 
                llm_response
                )

            actions.append(action)
            predicates.extend(new_predicates)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    predicates = prune_predicates(predicates=predicates, actions=actions) # discard predicates not found in action models + duplicates
    types = format_types(type_hierarchy) # retrieve types
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

    domain_file = "paper_reconstructions/nl2plan/results/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)


    # # STEP FIVE: task extraction
    # feedback_template = open_file('paper_reconstructions/nl2plan/prompts/task_extraction/feedback.txt')

    # objects, initial, goal, llm_response = task_builder.extract_task(
    #     model=model,
    #     problem_desc=problem_desc,
    #     prompt_template=task_extraction_prompt.generate_prompt(),
    #     types=types,
    #     predicates=predicates,
    #     actions=actions
    #     )

    # objects = task_builder.format_objects(objects)
    # initial = task_builder.format_initial(initial)
    # goal = task_builder.format_goal(goal)
    
    # pddl_problem = task_builder.generate_task("test_domain", objects, initial, goal)

    # problem_file = "paper_reconstructions/nl2plan/results/problem.pddl"
    # with open(problem_file, "w") as f:
    #     f.write(pddl_problem)
        
    # # parse PDDL files
    # pddl_domain = check_parse_domain(domain_file)
    # with open(domain_file, "w") as f:
    #     f.write(pddl_domain)

    # pddl_problem = check_parse_problem(problem_file)
    # with open(problem_file, "w") as f:
    #     f.write(pddl_problem)
        
    # # run planner
    # planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)