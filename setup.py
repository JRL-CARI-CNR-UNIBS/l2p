# """
# Activate virtual environment: source env/bin/activate

# L2P Checklist

# - [ ] Integrate action-construction architecture into work
#     - [ ] Implement add_predicates
# - [ ] Distribute each component into its separate class, let domain_builder be the coordinating class
# - [ ] Implement auto-feedback checklist
# - [ ] Implement LLM-generated feedback checklist
# - [ ] Implement PDDL generator — parser to assemble everything together

# - The action_construction pipeline consists of:
#     - Action extraction loop
#         - For each action description, construct singular action (parameter, precondition, effects) based on current predicts and put into a list
#         - Update list of new predicates 
#         - Prune unused predicates and types
#     - Once all actions generated, add actions (iteratively) and predicates to PDDLGenerator

# PDDLGenerator is essentially domain_builder / task_builder — CHANGE THINGS AROUND TO PERFORM SAME FUNCTION

# - [ ] Implement add_type — run through 
# - [ ] Implement add_action — run through whole pipeline

# - [ ] Implement task_builder
#     - [ ] extract_object
#     - [ ] extract_initial_state
#     - [ ] extract_goal_state
#     - [ ] Implement get functions
#     - [ ] Implement add functions — pipelines

# - [ ] Implement external planner tool


    # print("\n\n---------------------------------\n\nAdding new type output:\n")

    # user_input = input("Please enter the type you want to add:\n")
    # prompt = "You are to add a new type into the types already listed. Format it the same way in Python dictionary\n\n" + user_input 

    # new_types = domain_builder.add_type(
    #      model=model,
    #      domain_desc=domain_desc,
    #      prompt_template=prompt
    # )
    # domain_builder.set_types(types=new_types)
    # print("New types: ", format_json_output(domain_builder.get_types()))

    # # extract type hierarchy
    # print("\n\n---------------------------------\n\nType hierarchy output:\n")
    # type_hierarchy = domain_builder.extract_type_hierarchy(
    #     model=model, 
    #     domain_desc=domain_desc, 
    #     prompt_template=type_hierarchy_prompt.get_prompt(), 
    #     types=domain_builder.get_types(),
    #     feedback="LLM",
    #     feedback_template=open_file('data/prompt_templates/hierarchy_construction/feedback.txt')
    #     )
    # domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    # print(format_json_output(type_hierarchy))

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements
from pddl import parse_domain, parse_problem
from l2p.utils.pddl_parser import convert_to_dict

domain_file = 'data/domain.pddl'
problem_file = "data/problem.pddl"

domain = parse_domain(domain_file)
pddl_domain = domain_to_string(domain)

problem = parse_problem(problem_file)
pddl_problem = problem_to_string(problem)

print("PDDL domain:\n", pddl_domain)
print("--------------")
print("PDDL problem:\n", pddl_problem)

# Write PDDL domain string to a file
with open(domain_file, "w") as f:
    f.write(pddl_domain)

print(f"PDDL domain written to {domain_file}")

with open(problem_file, "w") as f:
    f.write(pddl_problem)

print(f"PDDL domain written to {problem_file}")