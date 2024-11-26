import os
from l2p import *
from copy import deepcopy

builder = DomainBuilder()
action_model = open_json('paper_reconstructions/llm+dm/prompts/action_model.json')
domain_desc = open_txt('paper_reconstructions/llm+dm/prompts/domain_desc.txt')
hierarchy_requirements = open_json('paper_reconstructions/llm+dm/prompts/hierarchy_requirements.json')
prompt_template = open_txt('paper_reconstructions/llm+dm/prompts/pddl_prompt.txt')

api_key = os.environ.get('OPENAI_API_KEY')
openai_llm = OPENAI(model="gpt-4o-mini", api_key=api_key)

def run_algorithm(
    model: LLM, 
    action_model, 
    domain_desc, 
    hierarchy_requirements, 
    prompt_template,
    max_iter: int=2):
    
    actions = list(action_model.keys())
    predicate_list = []
    
    for i_iter in range(max_iter):

        # dynamically add predicates for each action
        prev_predicate_list = deepcopy(predicate_list)
        action_list = []

        # iterate actions to get PDDL specs + predicates
        for i_action, action in enumerate(actions):
            if len(predicate_list) == 0:
                prompt_template = prompt_template.replace('{predicates}', 
                '\nNo predicate has been defined yet')
            else:
                results = ""
                for i, p in enumerate(predicate_list):
                    results += f'\n{i + 1}. {p["raw"]}'    
                    prompt_template = prompt_template.replace('{predicates}', results)

            # extract pddl action and predicates
            pddl_action, new_preds, response = (
                builder.extract_pddl_action(
                    model=model, 
                    domain_desc=domain_desc,
                    prompt_template=prompt_template, 
                    action_name=action,
                    action_desc=action_model[action]['desc'],
                    predicates=predicate_list,
                    types=hierarchy_requirements["hierarchy"]
                )
            )

            # format + add extracted actions and predicates
            new_preds = parse_new_predicates(response)
            predicate_list.extend(new_preds)
            action_list.append(pddl_action)
            predicate_list = prune_predicates(predicate_list, action_list)

    return predicate_list, action_list

pred, action = run_algorithm(
    model=openai_llm, 
    action_model=action_model,
    domain_desc=domain_desc,
    hierarchy_requirements=hierarchy_requirements,
    prompt_template=prompt_template)

print(pred)
print()
print()
print(action)