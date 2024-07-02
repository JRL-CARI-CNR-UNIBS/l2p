from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import Domain_Builder
from l2p.llm_builder import get_llm
from l2p.utils.pddl_output_utils import prune_predicates, prune_types, extract_types
import os, json

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

    model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")

    domain_desc = open_file('data/domains/blocksworld.txt')
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

    types = domain_builder.extract_type(model=model, domain_desc=domain_desc, prompt_template=type_extraction_prompt.get_prompt())
    domain_builder.set_types(types=types)
    print("Types: ", format_json_output(domain_builder.get_types()))

    print("\n\n---------------------------------\n\n")
    print("Type hierarchy output:\n")

    type_hierarchy = domain_builder.extract_type_hierarchy(model=model, domain_desc=domain_desc, prompt_template=type_hierarchy_prompt.get_prompt(), types=domain_builder.get_types())
    domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    print(format_json_output(type_hierarchy))

    print("\n\n---------------------------------\n\n")
    print("Natural language action output:\n")

    nl_actions = domain_builder.extract_nl_actions(model=model, domain_desc=domain_desc, prompt_template=nl_action_extraction_prompt.get_prompt(), type_hierarchy=type_hierarchy)
    domain_builder.set_nl_actions(nl_actions)
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
                predicates=predicates
            )
            actions.append(action)
            predicates.extend(new_predicates)

        if len (predicates) == curr_preds:
            print("No new predicates created. Stopping action construction.")
            break
    else: 
        print("Reached maximum iterations. Stopping action construction.")

    print("PREDICATES RAW:")
    for i in predicates:
        print(i, "\n")

    predicates = prune_predicates(predicates=predicates, actions=actions)
    types = extract_types(type_hierarchy)
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions)

    predicates = [pred["clean"].split(":")[0].strip() for pred in predicates]

    formatted_types = ""
    for i in pruned_types:
        formatted_types += f"{i}\n"

    formatted_predicates = ""
    for i in predicates:
        formatted_predicates += f"{i}\n"

    print("[DOMAIN]\n")
    print(domain_builder.generate_domain(domain="test_domain", types=formatted_types, predicates=formatted_predicates, actions=actions))








    # print("Constructed actions:\n", "\n\n".join([str(action) for action in actions]))


    # action_list = []
    
    # predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])

    # lines = predicate_str.strip().split('\n')
    # predicates = set()

    # for line in lines:
    #     predicate = line.split(";")[0].strip()
    #     predicates.add(predicate)

    # for i in predicates:
    #     print(f"PREDICATES: {i}")

    # print(f"PRUNED TYPES: {str(pruned_types)}")

    # pddl_pred_list = []
    # for i in predicates:
    #     pddl_pred_list.append(parse_predicate(i))

    


    # requirements = [Requirements.STRIPS, Requirements.TYPING]
    # domain = Domain(
    #     "test_domain",
    #     requirements=requirements,
    #     types=pruned_types,
    #     #constants=[a, b, c],
    #     predicates=pddl_pred_list,
    #     actions=action_list
    # )

    # print(domain_to_string(domain))

# [(has_loading_area ?l - location), (connected ?l1 - location ?l2 - location), (at ?o - object ?l - location), (loaded ?package - object ?truck - vehicle)]

    # print("\n\n---------------------------------\n\n")
    # print("Adding new type:\n")

    # types = domain_builder.add_type(model=model, domain_desc=domain_desc, prompt_template=type_extraction_prompt.get_prompt())
    # domain_builder.set_types(types=types)
    # print("New types: ", format_json_output(domain_builder.get_types()))

    # print("\n\n---------------------------------\n\n")
    # print("New type hierarchy output:\n")

    # type_hierarchy = domain_builder.extract_type_hierarchy(model=model, domain_desc=domain_desc, prompt_template=type_hierarchy_prompt.get_prompt(), types=domain_builder.get_types())
    # domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    # print(format_json_output(type_hierarchy))

    # print("Types:\n", types)
    # print("\n----------\n")

    # print("Pruned Types:\n", pruned_types)
    # print("\n----------\n")

    # # print("PDDL Types:\n", convert_to_pddl_types(type_hierarchy))
    # # print("\n----------\n")
    
    # print("Predicates\n", str(predicates))
    # print("\n----------\n")

    # print("Actions\n")
    # for action in actions:

    #     print(
    #         action["name"]
    #     )
    #     print(
    #         action["parameters"]
    #     )
    #     print(
    #         action["preconditions"]
    #     )
    #     print(
    #         action["effects"]
    #     )
    #     print("---------\n")