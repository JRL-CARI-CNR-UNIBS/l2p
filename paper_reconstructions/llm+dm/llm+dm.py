

"""
Paper: "Leveraging Pre-trained Large Language Models to Construct and Utilize World Models for Model-based Task Planning" Guan et al. (2023)
Source code: https://github.com/GuanSuns/LLMs-World-Models-for-Planning
Run: python3 -m paper_reconstructions.llm+dm.llm+dm

Assumes the following:
    1. NL descriptions of all the actions
    2. A description of the domain
    3. Information of the object types and hierarchy - fixed set of object types specified in prompt
"""

import os, json
from copy import deepcopy
from l2p import *

def open_txt(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def open_json(file_path):
    with open(file_path, 'r') as file:
        file = json.load(file)
    return file


def construct_action_model(
    domain_desc, 
    prompt_template, 
    action_name, 
    action_desc, 
    predicate_list, 
    max_iterations=3, 
    syntax_validator=None
    ) -> tuple[Action,list[Predicate],str]: 
    
    """
    This function constructs an action model for a single action. Specifically, it runs through syntax validator to refine model in a certain
    set amount of iterations.
    
    Returns:
        - pddl_action (Action): Action model class that contains params, preconditions, effects, and additional info
        - predicate_list (list[Predicate]): list of Predicate classes
        - llm_response (str): raw output from LLM
    """
    
    no_syntax_error = False
    i_iter = 0
    
    # create action model, check for syntax error
    while not no_syntax_error and i_iter < max_iterations:
        i_iter += 1
        
        # generate action model
        pddl_action, new_predicates, llm_response = domain_builder.extract_pddl_action(
            model=openai_llm, 
            domain_desc=domain_desc,
            prompt_template=prompt_template, 
            action_name=action_name,
            action_desc=action_desc,
            predicates=predicate_list,
            types=hierarchy_requirements["hierarchy"]
            )
        
        
        # if syntax validator check is set on
        if syntax_validator is not None:

            syntax_valid = False

            while not syntax_valid:
                    # perform syntax check on action model
                    no_syntax_error, feedback_msg = syntax_validator.validate_usage_predicates(llm_response, predicate_list, hierarchy_requirements["hierarchy"])
                    
                    # if there is syntax error, run through feedback mechanism to retrieve new action model
                    if no_syntax_error is False:
                        # Update the prompt with the feedback
                        prompt_template += "\n\nHere is the PDDL action you outputted:\n" + str(pddl_action)
                        if len(new_predicates) > 0:
                            prompt_template += "\n\nHere are the predicates you created from that action:\n" + format_predicates(new_predicates)
                        prompt_template += "\n\nHere is the feedback you outputted:\n" + feedback_msg

                        # Generate a new PDDL action model based on the feedback
                        pddl_action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                            model=openai_llm, 
                            domain_desc=domain_desc,
                            prompt_template=prompt_template, 
                            action_name=action_name,
                            action_desc=action_desc,
                            predicates=predicate_list,
                            types=hierarchy_requirements["hierarchy"]
                        )
                    else:
                        syntax_valid = True
        
    new_predicates = parse_new_predicates(llm_response)
    predicate_list.extend(new_predicates)

    return pddl_action, predicate_list, llm_response


if __name__ == "__main__":    
    
    # setup prompt templates
    action_model = open_json('paper_reconstructions/llm+dm/prompts/action_model.json')
    domain_desc = open_txt('paper_reconstructions/llm+dm/prompts/domain_desc.txt')
    hierarchy_requirements = open_json('paper_reconstructions/llm+dm/prompts/hierarchy_requirements.json')
    prompt_template = open_txt('paper_reconstructions/llm+dm/prompts/pddl_prompt.txt')

    # setup LLM engine
    engine = "gpt-4o-mini"
    api_key = os.environ.get('OPENAI_API_KEY')
    openai_llm = OPENAI(model=engine, api_key=api_key)

    # setup L2P libraries
    domain_builder = DomainBuilder()
    syntax_validator = SyntaxValidator()

    domain = 'logistics' # using logistics domain for this example
    
    max_iterations = 2
    max_feedback = 1
        
    actions = list(action_model.keys())
    predicate_list = list()
    
    """
    Action-by-action algorithm: iteratively generates an action model (parameters, precondition, effects) one at a time. At the same time,
        it is generating new predicates if needed and is added to a dynamic list. At the end of the iterations, it is ran again once more to
        create the action models agains, but with using the new predicate list. This algorithm can iterative as many times as needed until no
        new predicates are added to the list. This is an action model refinement algorithm, that refines itself by a growing predicate list.
    """
    
    # iterate however many times
    for i_iter in range(max_iterations):
        prev_predicate_list = deepcopy(predicate_list)
        
        action_list = []
        
        # iterate through each action
        for i_action, action in enumerate(actions):
            
            # replace prompt with dynamic predicate list
            if len(predicate_list) == 0:
                # if no predicates in list
                prompt_template = prompt_template.replace('{predicates}', '\nNo predicate has been defined yet')
            else:
                # replace with current predicates
                readable_results = ""
                for i, p in enumerate(predicate_list):
                    readable_results += f'\n{i + 1}. {p["raw"]}'
                    
                prompt_template = prompt_template.replace('{predicates}', readable_results)
            
            # construct action model
            pddl_action, predicate_list, llm_output = construct_action_model(
                domain_desc, 
                prompt_template, 
                action, 
                action_model[action]['desc'], 
                predicate_list, 
                max_iterations=max_feedback,
                syntax_validator=syntax_validator
                )
            action_list.append(pddl_action)
            
    # at the end of the action-by-action algorithm, clean predicates, types, and build parse PDDL domain
    predicate_list = prune_predicates(predicates=predicate_list, actions=action_list)
    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicate_list])
    
    # prune types if not found in action interfaces
    types = {name: description for name, description in hierarchy_requirements["hierarchy"].items() if name}
    types_str = "\n".join(types)
            
    # generate domain
    pddl_domain = domain_builder.generate_domain(
        domain=domain, 
        requirements=hierarchy_requirements["requirements"],
        types=types_str,
        predicates=predicate_str,
        actions=action_list
        )
    
    domain_file = "paper_reconstructions/llm+dm/results/domain.pddl"
    
    # save domain file
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
            