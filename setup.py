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
    # prompt = "\nYou are to add a new type into the types already listed. Format it the same way in Python dictionary\n\n" + user_input 

    # new_types = domain_builder.add_type(
    #      model=model,
    #      domain_desc=domain_desc,
    #      prompt_template=type_extraction_prompt.generate_prompt() + prompt
    # )
    # domain_builder.set_types(types=new_types)
    # print("New types: ", format_json_output(domain_builder.get_types()))

    # # extract type hierarchy
    # print("\n\n---------------------------------\n\nType hierarchy output:\n")
    # type_hierarchy = domain_builder.extract_type_hierarchy(model, domain_desc, type_hierarchy_prompt.generate_prompt(), domain_builder.get_types())
    # domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    # print(format_json_output(type_hierarchy))

# user_input = input("\nPlease enter the action(s) in natural language you want to add:\n")
# prompt = "\nYou are to add a new action into the actions already listed. Format it the same way in Python dictionary\n\n" + user_input 
# new_nl_actions = domain_builder.add_nl_action(
#     model, 
#     domain_desc, 
#     prompt_template=nl_action_extraction_prompt.generate_prompt() + prompt,
#     type_hierarchy=type_hierarchy
#     )

# add_predicate_prompt = open_file('data/prompt_templates/add_functions/add_predicates.txt')

#     user_input = input("\nPlease enter the predicate(s) in natural language you want to add:\n")
#     prompt = "\nYou are to add a new predicate into the predicates already listed. Format it the same way in Python dictionary\n\n" + user_input 

#     new_predicates = domain_builder.add_predicates(
#         model=model, 
#         domain_desc=domain_desc, 
#         prompt_template=add_predicate_prompt + prompt,
#         type_hierarchy=pruned_types,
#         predicates=predicates
#         )
    
#     print("NEW PREDICATES OUTPUT:\n", new_predicates)


from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem
import sys


def check_parse_domain(file_path):
    try:
        domain = parse_domain(file_path)
        pddl_domain = domain_to_string(domain)
        return pddl_domain
    except Exception as e:
        print("------------------")
        print(f"Error parsing domain: {e}", file=sys.stderr)
        print("------------------")
        sys.exit(1)

def check_parse_problem(file_path):
    try:
        problem = parse_problem(file_path)
        pddl_problem = problem_to_string(problem)
        return pddl_problem
    except Exception as e:
        print("------------------")
        print(f"Error parsing domain: {e}", file=sys.stderr)
        print("------------------")
        sys.exit(1)

if __name__ == "__main__":
    domain_file_path = 'data/domain.pddl'
    pddl_domain = check_parse_domain(domain_file_path)
    print("PDDL domain:\n", pddl_domain)

    print("------------------")

    problem_file_path = 'data/problem_1.pddl'
    pddl_problem = check_parse_problem(problem_file_path)
    print("PDDL Problem:\n", pddl_problem)

    with open(domain_file_path, "w") as f:
        f.write(pddl_domain)

    with open(problem_file_path, "w") as f:
        f.write(pddl_problem)