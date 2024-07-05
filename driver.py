from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import Domain_Builder
from l2p.task_builder import Task_Builder
from l2p.llm_builder import get_llm
from l2p.utils.pddl_output_utils import prune_predicates, prune_types, extract_types
import os, json

# micro-functions
def format_json_output(data):
        return json.dumps(data, indent=4)

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def open_examples(examples_dir):
    example_files = [f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))]
    examples = [open_file(os.path.join(examples_dir, f)) for f in example_files]
    return examples

if __name__ == "__main__":

    # THIS IS IMPORTANT TO LOOK INTO
    unsupported_keywords = ['object']

    model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")

    # instantiate domain builder class
    domain_desc = open_file('data/domains/blocksworld.txt')
    domain_builder = Domain_Builder(types=None,type_hierarchy=None,predicates=None,nl_actions=None,pddl_actions=None)

    # open and create type extraction prompt builder class
    role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/type_extraction/examples/')
    task_desc = open_file('data/prompt_templates/type_extraction/task.txt')
    type_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create type hierarchy prompt builder class
    role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/hierarchy_construction/examples/')
    task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')
    type_hierarchy_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create NL action prompt builder class      
    role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_extraction/examples/')
    task_desc = open_file('data/prompt_templates/action_extraction/task.txt')
    nl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create PDDL action prompt builder class
    role_desc = open_file('data/prompt_templates/action_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/task.txt')
    pddl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)


    # extract types
    print("Extracted types output:\n")
    types = domain_builder.extract_type(
        model=model, 
        domain_desc=domain_desc, 
        prompt_template=type_extraction_prompt.get_prompt(),
        feedback="LLM",
        feedback_template=open_file('data/prompt_templates/type_extraction/feedback.txt')
        )
    domain_builder.set_types(types=types)
    print("Types: ", format_json_output(domain_builder.get_types()))
    
    # extract type hierarchy
    print("\n\n---------------------------------\n\nType hierarchy output:\n")
    type_hierarchy = domain_builder.extract_type_hierarchy(
        model=model, 
        domain_desc=domain_desc, 
        prompt_template=type_hierarchy_prompt.get_prompt(), 
        types=domain_builder.get_types(),
        feedback="LLM",
        feedback_template=open_file('data/prompt_templates/hierarchy_construction/feedback.txt')
        )
    domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    print(format_json_output(type_hierarchy))

    
    # extract NL action descriptions
    print("\n\n---------------------------------\n\nNatural language action output:\n")
    nl_actions = domain_builder.extract_nl_actions(
        model=model, 
        domain_desc=domain_desc, 
        prompt_template=nl_action_extraction_prompt.get_prompt(), 
        type_hierarchy=type_hierarchy)
    domain_builder.set_nl_actions(nl_actions)

    for i in nl_actions:
        print(i)
    
    # extract PDDL formatted actions
    print("\n\n---------------------------------\n\nPDDL action output:\n")
    # action-by-action method used in Guan et al. (2023): https://arxiv.org/abs/2305.14909
    max_iters = 1
    predicates = []
    for i in range(max_iters):
        actions = []
        curr_preds = len(predicates)

        # iterate through each action, dynamically create new predicates
        for action_name, action_desc in nl_actions.items():
            action, new_predicates = domain_builder.extract_pddl_action(
                model=model,
                prompt_template=pddl_action_extraction_prompt.get_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                predicates=predicates
            )

            actions.append(action)
            predicates.extend(new_predicates)
            predicates = prune_predicates(predicates=predicates, actions=actions)

        if len (predicates) == curr_preds:
            print("No new predicates created. Stopping action construction.")
            break
    else: 
        print("Reached maximum iterations. Stopping action construction.")

    predicates = prune_predicates(predicates=predicates, actions=actions) # discard predicates not found in action models + duplicates
    types = extract_types(type_hierarchy) # retrieve types
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions) # discard types not in predicates / actions + duplicates

    # remove unsupported words (IMPLEMENT THIS AS A HELPER FUNCTION)
    pruned_types = {name: description for name, description in pruned_types.items() if name not in unsupported_keywords}

    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    types_str = "\n".join(pruned_types)

    print("[DOMAIN]\n") 
    pddl_domain = domain_builder.generate_domain(domain="test_domain", types=types_str, predicates=predicate_str, actions=actions)
    print(pddl_domain)

    # Define the domain file path
    domain_file = "data/domain.pddl"

    # Write PDDL domain string to a file
    with open(domain_file, "w") as f:
        f.write(pddl_domain)

    print(f"PDDL domain written to {domain_file}")







    # task_builder = Task_Builder(types=None,type_hierarchy=None,predicates=None,nl_actions=None,pddl_actions=None)

