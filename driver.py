from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import Domain_Builder
from l2p.llm_builder import get_llm

import json
import os

if __name__ == "__main__":

    def format_json_output(data):
        return json.dumps(data, indent=4)

    def open_file(file_path):
        with open(file_path, 'r') as file:
            role = file.read().strip()
        return role
    
    def open_examples(examples_dir):
        example_files = [f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))]
        examples = [open_file(os.path.join(examples_dir, f)) for f in example_files]
        return examples

    model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")

    domain_desc = open_file('data/domains/blocksworld.txt')
    domain_builder = Domain_Builder(domain=domain_desc, types=None,type_hierarchy=None,predicates=None,nl_actions=None,pddl_actions=None)

    role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/type_extraction/examples/')
    task_desc = open_file('data/prompt_templates/type_extraction/task.txt')

    type_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc, domain_desc)

    role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/hierarchy_construction/examples/')
    task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')

    type_hierarchy_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc, domain_desc)

    role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_extraction/examples/')
    task_desc = open_file('data/prompt_templates/action_extraction/task.txt')

    nl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc, domain_desc)

    role_desc = open_file('data/prompt_templates/action_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/task.txt')

    pddl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc, domain_desc)

    print("Extracted types output:\n")

    domain_builder.extract_type(model=model, prompt=type_extraction_prompt.get_prompt())
    types = domain_builder.get_types()
    print("Types: ", format_json_output(types))

    print("\n\n---------------------------------\n\n")
    print("Type hierarchy output:\n")

    domain_builder.extract_type_hierarchy(model=model, prompt=type_hierarchy_prompt.get_prompt(),type_list=types)
    type_hierarchy = domain_builder.get_type_hierarchy()
    print(format_json_output(type_hierarchy))

    print("\n\n---------------------------------\n\n")
    print("Natural language action output:\n")

    domain_builder.extract_NL_actions(model=model, prompt=nl_action_extraction_prompt.get_prompt())
    nl_actions = domain_builder.get_nl_actions()
    print(nl_actions)

    print("\n\n---------------------------------\n\n")
    print("PDDL action output:\n")

    domain_builder.extract_pddl_actions(model=model, prompt=pddl_action_extraction_prompt.get_prompt())
    pddl_actions = domain_builder.get_pddl_actions()
    print(str(pddl_actions))

    print("\n\n---------------------------------\n\n")
    print("PDDL domain output:\n")

    domain_builder.generate_domain(model=model, prompt="With the given information, construct the PDDL domain file.")


# I want to add a new type called "car" that transports packages, as well as "bike" that does the same

    # print("\n\n---------------------------------\n\n")
    # print("Adding new type output:\n")

    # cot_file_path = 'data/prompt_templates/type_extraction/example.txt'
    # cot_desc = open_file(cot_file_path)

    # add_type = "Your task is to add an additional type to the given current types in the domain. Here is a CoT example to follow original:\n" + cot_desc

    # response, types = domain_builder.add_type(model=model, prompt=add_type)

    # print("\n\n---------------------------------\n\n")
    # print("Type hierarchy output:\n")

    # response, type_hierarchy = domain_builder.extract_type_hierarchy(model=model, prompt=type_hierarchy_prompt,type_list=types)
    # type_hierarchy = format_json_output(type_hierarchy)
    # print(type_hierarchy)

