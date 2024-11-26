import os
from l2p import *

builder = DomainBuilder() # create domain build class

def run_aba_alg(model: LLM, action_model, domain_desc, 
                hierarchy, prompt, max_iter: int=2
        ) -> tuple[list[Predicate], list[Action]]:
    
    actions = list(action_model.keys())
    pred_list = []
    
    for _ in range(max_iter):
        action_list = []
        # iterate each action spec. + new predicates
        for _, action in enumerate(actions):
            if len(pred_list) == 0:
                prompt = prompt.replace('{predicates}', 
                '\nNo predicate has been defined yet')
            else:
                res = ""
                for i, p in enumerate(pred_list):
                    res += f'\n{i + 1}. {p["raw"]}'    
                    prompt = prompt.replace('{predicates}', res)
            # extract pddl action and predicates
            pddl_action, new_preds, response = (
                builder.extract_pddl_action(
                    model=model, 
                    domain_desc=domain_desc,
                    prompt_template=prompt, 
                    action_name=action,
                    action_desc=action_model[action]['desc'],
                    action_list=action_list,
                    predicates=pred_list,
                    types=hierarchy["hierarchy"]
                )
            )
            # format + add extracted actions and predicates
            new_preds = parse_new_predicates(response)
            pred_list.extend(new_preds)
            action_list.append(pddl_action)
        pred_list = prune_predicates(pred_list, action_list)

    return pred_list, action_list

def run_aba():
    
    # retrieve prompt information
    base_path='paper_reconstructions/llm+dm/prompts/'
    action_model=load_file(f'{base_path}action_model.json')
    domain_desc=load_file(f'{base_path}domain_desc.txt')
    hier=load_file(
        f'{base_path}hierarchy_requirements.json')
    prompt=load_file(f'{base_path}pddl_prompt.txt')

    # initialise LLM engine (OpenAI in this case)
    api_key = os.environ.get('OPENAI_API_KEY')
    llm = OPENAI(model="gpt-4o-mini", api_key=api_key)

    # run "action-by-action" algorithm
    pred, action = run_aba_alg(
        model=llm, 
        action_model=action_model,
        domain_desc=domain_desc,
        hierarchy=hier,
        prompt=prompt)

def run_predicates():
    
    api_key = os.environ.get('OPENAI_API_KEY')
    llm = OPENAI(model="gpt-4o-mini", api_key=api_key)
    
    # retrieve prompt information
    base_path='tests/usage/prompts/domain/'
    domain_desc = load_file(f'{base_path}blocksworld_domain.txt')
    extract_predicates_prompt = load_file(f'{base_path}extract_predicates.txt')
    types = load_file(f'{base_path}types.json')
    action = load_file(f'{base_path}action.json')
    
    # extract predicates via LLM
    predicates, llm_output = domain_builder.extract_predicates(
        model=llm,
        domain_desc=domain_desc,
        prompt_template=extract_predicates_prompt,
        types=types,
        nl_actions={action['action_name']: action['action_desc']}
        )
    
    print(predicates)
    
    # format key info into PDDL strings
    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    
    print(f"PDDL domain predicates:\n{predicate_str}")
    
    return predicates
    
def run_task():
    
    task_builder = TaskBuilder()
    
    api_key = os.environ.get('OPENAI_API_KEY')
    llm = OPENAI(model="gpt-4o-mini", api_key=api_key)
    
    # load in assumptions
    problem_desc = load_file(r'tests/usage/prompts/problem/blocksworld_problem.txt')
    extract_task_prompt = load_file(r'tests/usage/prompts/problem/extract_task.txt')
    types = load_file(r'tests/usage/prompts/domain/types.json')
    predicates_json = load_file(r'tests/usage/prompts/domain/predicates.json')
    predicates: List[Predicate] = [Predicate(**item) for item in predicates_json]
    
    # extract PDDL task specifications via LLM
    objects, initial_states, goal_states, llm_response = task_builder.extract_task(
        model=llm,
        problem_desc=problem_desc,
        prompt_template=extract_task_prompt,
        types=types,
        predicates=predicates
        )
    
    # format key info into PDDL strings
    objects_str = task_builder.format_objects(objects)
    initial_str = task_builder.format_initial(initial_states)
    goal_str = task_builder.format_goal(goal_states)
    
    # generate task file
    pddl_problem = task_builder.generate_task(
        domain="blocksworld", 
        problem="blocksworld_problem", 
        objects=objects_str, 
        initial=initial_str, 
        goal=goal_str)
    
    print(f"### LLM OUTPUT:\n {pddl_problem}")
    
    print(llm_response)
    
def run_feedback():
    
    feedback_builder = FeedbackBuilder()
    
    api_key = os.environ.get('OPENAI_API_KEY')
    llm = OPENAI(model="gpt-4o-mini", api_key=api_key)
    
    problem_desc = load_file(r'tests/usage/prompts/problem/blocksworld_problem.txt')
    types = load_file(r'tests/usage/prompts/domain/types.json')
    feedback_template = load_file(r'tests/usage/prompts/problem/feedback.txt')
    predicates_json = load_file(r'tests/usage/prompts/domain/predicates.json')
    predicates: List[Predicate] = [Predicate(**item) for item in predicates_json]
    llm_response = load_file(r'tests/usage/prompts/domain/llm_output_task.txt')
    
    objects, initial, goal, feedback_response = feedback_builder.task_feedback(
        model=llm, 
        problem_desc=problem_desc, 
        feedback_template=feedback_template, 
        feedback_type="llm", 
        predicates=predicates,
        types=types, 
        llm_response=llm_response)

    print("FEEDBACK:\n", feedback_response)

if __name__ == "__main__":
    
    # run_aba()
    # run_predicates()
    # run_task()
    run_feedback()
    