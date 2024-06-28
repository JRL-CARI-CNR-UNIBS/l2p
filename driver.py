from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import Domain_Builder
from l2p.llm_builder import get_llm
from l2p.utils.pddl_types import Predicate
from l2p.utils.pddl_output_utils import prune_predicates, prune_types, extract_types
import json
import os

if __name__ == "__main__":

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

    model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")

    domain_desc = open_file('data/domains/logistics.txt')
    domain_builder = Domain_Builder(types=None,type_hierarchy=None,predicates=None,nl_actions=None,pddl_actions=None)

    role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/type_extraction/examples/')
    task_desc = open_file('data/prompt_templates/type_extraction/task.txt')

    type_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/hierarchy_construction/examples/')
    task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')

    type_hierarchy_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_extraction/examples/')
    task_desc = open_file('data/prompt_templates/action_extraction/task.txt')

    nl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/action_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/task.txt')

    pddl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    print("Extracted types output:\n")

    domain_builder.extract_type(model=model, domain_desc=domain_desc, prompt_template=type_extraction_prompt.get_prompt())
    types = domain_builder.get_types()
    print("Types: ", format_json_output(types))

    print("\n\n---------------------------------\n\n")
    print("Type hierarchy output:\n")

    domain_builder.extract_type_hierarchy(model=model, domain_desc=domain_desc, prompt_template=type_hierarchy_prompt.get_prompt(), types=types)
    type_hierarchy = domain_builder.get_type_hierarchy()
    print(format_json_output(type_hierarchy))

    print("\n\n---------------------------------\n\n")
    print("Natural language action output:\n")

    domain_builder.extract_nl_actions(model=model, domain_desc=domain_desc, prompt_template=nl_action_extraction_prompt.get_prompt(), type_hierarchy=type_hierarchy)
    nl_actions = domain_builder.get_nl_actions()
    print(nl_actions)

    print("\n\n---------------------------------\n\n")
    print("PDDL action output:\n")

    max_iters = 1

    predicates = []
    for i in range(max_iters):
        actions = []
        curr_preds = len(predicates)
        for action_name, action_desc in nl_actions.items():
            action, new_predicates = domain_builder.extract_pddl_action(
                model=model, 
                prompt_template=pddl_action_extraction_prompt.get_prompt(), 
                action_name=action_name, 
                action_desc=action_desc, 
                predicates=[Predicate]
            )
            
            actions.append(action)
            predicates.extend(new_predicates)

        if len (predicates) == curr_preds:
            print("No new predicates created. Stopping action construction.")
            break
    else: 
        print("Reached maximum iterations. Stopping action construction.")

    predicates = prune_predicates(predicates=predicates, actions=actions)
    types = extract_types(type_hierarchy)
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions)

    print("Constructed actions:\n", "\n\n".join([str(action) for action in actions]))
    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    print(f"PREDICATES: {predicate_str}")

    # print("\n\nACTION", action)
    # print("\n\nPREDICATES:", new_predicates)
    # print("\n")

