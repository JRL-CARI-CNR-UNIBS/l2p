from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import Domain_Builder
from l2p.llm_builder import get_llm

import json

def format_json_output(data):
    return json.dumps(data, indent=4)

def open_file(file_path):
    with open(file_path, 'r') as file:
        role = file.read().strip()
    return role

if __name__ == "__main__":

    model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")
    domain_builder = Domain_Builder(types=None,type_hierarchy=None,predicates=None,actions=None)

    role_file_path = 'data/templates/type_extraction/role.txt'
    role_description = open_file(role_file_path)
    domain_file_path = 'data/templates/domains/logistics.txt'
    domain_description = open_file(domain_file_path)
    cot_file_path = 'data/templates/type_extraction/example.txt'
    cot_description = open_file(cot_file_path)
    task_file_path = 'data/templates/type_extraction/task.txt'
    task_description = open_file(task_file_path)

    type_extraction_prompt = PromptBuilder()
    type_extraction_prompt.set_role(role_description)
    type_extraction_prompt.set_domain_description(domain_description)
    type_extraction_prompt.set_COT_example(cot_description)
    type_extraction_prompt.set_task(task_description)
    type_extraction_prompt = type_extraction_prompt.generate_prompt()

    role_file_path = 'data/templates/hierarchy_construction/role.txt'
    role_description = open_file(role_file_path)
    domain_file_path = 'data/templates/domains/logistics.txt'
    domain_description = open_file(domain_file_path)
    cot_file_path = 'data/templates/hierarchy_construction/example.txt'
    cot_description = open_file(cot_file_path)
    task_file_path = 'data/templates/hierarchy_construction/task.txt'
    task_description = open_file(task_file_path)

    type_hierarchy_prompt = PromptBuilder()
    type_hierarchy_prompt.set_role(role_description)
    type_hierarchy_prompt.set_domain_description(domain_description)
    type_hierarchy_prompt.set_COT_example(cot_description)
    type_hierarchy_prompt.set_task(task_description)
    type_hierarchy_prompt = type_hierarchy_prompt.generate_prompt()

    print("Extracted types output:\n")

    response, types = (domain_builder.extract_type(model=model, prompt=type_extraction_prompt))
    print("Types: ", types)

    print("\n\n---------------------------------\n\n")
    print("Type hierarchy output:\n")

    response, type_hierarchy = (domain_builder.extract_type_hierarchy(model=model, prompt=type_hierarchy_prompt,type_list=types))
    type_hierarchy = format_json_output(type_hierarchy)
    print(type_hierarchy)

