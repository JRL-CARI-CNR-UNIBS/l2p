

"""
Paper: "Leveraging Pre-trained Large Language Models to Construct and Utilize World Models for Model-based Task Planning" Guan et al. (2023)
Source code: https://github.com/GuanSuns/LLMs-World-Models-for-Planning
Run: python3 -m tests.paper_reconstructions.llm+dm.llm+dm

Assumes the following:
    1. NL descriptions of all the actions
    2. A description of the domain
    3. Information of the object types and hierarchy - fixed set of object types specified in prompt
"""

import os, json
from copy import deepcopy
from addict import Dict
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.domain_builder import DomainBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.utils.pddl_validator import SyntaxValidator
from l2p.utils.pddl_parser import parse_new_predicates, prune_predicates, prune_types, extract_types
from tests.setup import check_parse_domain

def open_txt(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def open_json(file_path):
    with open(file_path, 'r') as file:
        file = json.load(file)
    return file


def construct_action_model(domain_desc, action_predicate_prompt, action_name, action_desc, predicate_list, max_iterations=3, syntax_validator=None): 
    
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
            model=model, 
            domain_desc=domain_desc,
            prompt_template=action_predicate_prompt, 
            action_name=action_name,
            action_desc=action_desc,
            predicates=predicate_list,
            types=hierarchy_requirements["hierarchy"]
            )
        
        # if syntax validator check is set on
        if syntax_validator is not None:

            # perform syntax check on action model
            no_syntax_error, feedback_msg = syntax_validator.validate_usage_predicates(llm_response, predicate_list, hierarchy_requirements["hierarchy"])
        
            # if there is syntax error, run through feedback mechanism to retrieve new action model
            if no_syntax_error == False:
                
                # run feedback mechanic (set on 'validator' mode)
                feedback_action, feedback_predicates, llm_feedback_response = feedback_builder.pddl_action_feedback(
                    model, 
                    domain_desc, 
                    feedback_msg, 
                    "validator", 
                    pddl_action, 
                    predicate_list, 
                    hierarchy_requirements["hierarchy"], 
                    llm_response
                    )
            
                if feedback_action != None:
                    pddl_action=feedback_action
                    new_predicates=feedback_predicates
        
    new_predicates = parse_new_predicates(llm_response)
    predicate_list.extend(new_predicates)

    return pddl_action, predicate_list, llm_response


if __name__ == "__main__":    
    
    # setup prompt templates
    action_model = open_json('tests/paper_reconstructions/llm+dm/prompts/action_model.json')
    domain_desc = open_txt('tests/paper_reconstructions/llm+dm/prompts/domain_desc.txt')
    hierarchy_requirements = open_json('tests/paper_reconstructions/llm+dm/prompts/hierarchy_requirements.json')
    prompt_template = open_txt('tests/paper_reconstructions/llm+dm/prompts/pddl_prompt.txt')

    # setup LLM engine
    engine = "gpt-4o-mini"
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
    model = GPT_Chat(client=client, engine=engine)

    # setup L2P libraries
    domain_builder = DomainBuilder()
    feedback_builder = FeedbackBuilder()
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
    
    action_predicate_prompt = ""
    
    # iterate however many times
    for i_iter in range(max_iterations):
        prev_predicate_list = deepcopy(predicate_list)
        
        action_list = []
        
        # iterate through each action
        for i_action, action in enumerate(actions):
            
            action_desc_prompt = action_model[action]['desc']
            action_prompt = str(prompt_template)
            
            action_predicate_prompt = f'{action_prompt}'
            
            # replace prompt with dynamic predicate list
            if len(predicate_list) == 0:
                # if no predicates in list
                action_predicate_prompt = action_predicate_prompt.replace('{predicates}', '\nNo predicate has been defined yet')
            else:
                # replace with current predicates
                readable_results = ""
                for i, p in enumerate(predicate_list):
                    readable_results += f'\n{i + 1}. {p["raw"]}'
                    
                action_predicate_prompt = action_predicate_prompt.replace('{predicates}', readable_results)
            
            # construct action model
            pddl_action, predicate_list, llm_output = construct_action_model(
                domain_desc, 
                action_predicate_prompt, 
                action, 
                action_model[action]['desc'], 
                predicate_list, 
                max_iterations=max_feedback,
                syntax_validator=syntax_validator
                )
            action_list.append(pddl_action)
            predicate_list = prune_predicates(predicates=predicate_list, actions=action_list)
            
            
    # at the end of the action-by-action algorithm, clean predicates, types, and build parse PDDL domain
    # predicates = prune_predicates(predicates=predicate_list, actions=action_list)
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
    
    domain_file = "tests/paper_reconstructions/llm+dm/results/domain.pddl"
    
    # save domain file
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
        
    # parse domain file    
    pddl_domain = check_parse_domain(domain_file)
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
            