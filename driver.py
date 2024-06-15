from pddl_builder.prompt_builder import PromptBuilder
from pddl_builder.builder import extract_type

def open_file(file_path):
    with open(file_path, 'r') as file:
        role = file.read().strip()
    return role

if __name__ == "__main__":

    role_file_path = 'data/templates/task_extraction/role.txt'
    role_description = open_file(role_file_path)

    domain_file_path = 'data/templates/domains/blocksworld.txt'
    domain_description = open_file(domain_file_path)

    cot_file_path = 'data/templates/task_extraction/example.txt'
    cot_description = open_file(cot_file_path)

    task_file_path = 'data/templates/task_extraction/task.txt'
    task_description = open_file(task_file_path)

    prompt_gen = PromptBuilder()

    prompt_gen.set_role(role_description)
    prompt_gen.set_domain_description(domain_description)
    prompt_gen.set_COT_example(cot_description)
    prompt_gen.set_task(task_description)

    final_prompt = prompt_gen.generate_prompt()

    print(final_prompt)
    print("\n\n---------------------------------\n\n")
    print("Extracted types output:\n")

    extract_type(final_prompt)