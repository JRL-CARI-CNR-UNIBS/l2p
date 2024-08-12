"""
This file contains collection of functions for PDDL domain generation purposes
"""

from collections import OrderedDict
from .utils.pddl_parser import parse_params, parse_new_predicates, parse_action, convert_to_dict, format_dict, format_predicates
from .utils.pddl_types import Predicate, Action
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder
import re

class DomainBuilder:
    def __init__(
            self, 
            types: dict[str,str]=None, 
            type_hierarchy: dict[str,str]=None, 
            predicates: list[Predicate]=None, 
            nl_actions: dict[str,str]=None, 
            pddl_actions: list[Action]=None
            ):
        """
        Initializes a domain builder object

        Args:
            types (dict[str,str]): types dictionary with name: description key-value pair
            type_hierarchy (dict[str,str]): type hierarchy dictionary
            predicates (list[Predicate]): list of Predicate objects
            nl_actions (dict[str,str]): dictionary of extracted actions, where the keys are action names and values are action descriptions
            pddl_actions (list[Action]): list of Action objects
        """
        self.types = types
        self.type_hierarchy = type_hierarchy
        self.predicates = predicates
        self.nl_actions = nl_actions
        self.pddl_actions = pddl_actions


    def extract_type(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            prompt_template: PromptBuilder,
            types: dict[str,str]=None
            ) -> tuple[dict[str,str], str]:
        """
        Extracts types with domain given

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (PromptBuilder): prompt template class

        Returns:
            type_dict (dict[str,str]): dictionary of types with (name:description) pair
        """

        model.reset_tokens() # reset tokens
    
        prompt_template += "\n\n## Domain\n" + domain_desc
        if types:
            prompt_template += "\n\n## Available Types\n" + format_dict(types)

        llm_response = model.get_output(prompt=prompt_template) # prompt model

        types = convert_to_dict(llm_response=llm_response)
        return types, llm_response
    
    def extract_type_hierarchy(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            types: dict[str,str]=None
            ) -> tuple[dict[str,str], str]:
        """
        Extracts type hierarchy from types list and domain given

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (PromptBuilder): prompt template class
            types (dict[str,str]): dictionary of types with (name:description) pair

        Returns:
            type_hierarchy (dict[str,str]): dictionary of type hierarchy
        """

        model.reset_tokens()

        prompt_template += "\n\n## Domain\n" + domain_desc
        if types:
            prompt_template += "\n\n## Available types:\n" + format_dict(types)

        llm_response = model.get_output(prompt=prompt_template)

        type_hierarchy = convert_to_dict(llm_response=llm_response)
        return type_hierarchy, llm_response
    
    def extract_nl_actions(
            self, 
            model: LLM_Chat,
            domain_desc: str, 
            prompt_template: PromptBuilder, 
            types: dict[str,str]=None,
            nl_actions: dict[str,str]=None
            ) -> tuple[dict[str,str], str]:
        
        """
        Extract actions in natural language given domain description using LLM.

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (PromptBuilder): prompt template class
            type_hierarchy (dict[str,str]): type hierarchy
            feedback (bool): whether to request feedback from LM - default True
            feedback_template (str): feedback template. Has to be specified if feedback is used - defaults None

        Returns:
            nl_actions (dict[str, str]): a dictionary of extracted actions, where the keys are action names and values are action descriptions
        """

        model.reset_tokens()
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        if types:
            prompt_template += "\n\n## Available types:\n" + format_dict(types)
        if nl_actions:
            prompt_template += "\n\n## Available actions:\n" + format_dict(nl_actions)

        llm_response = model.get_output(prompt=prompt_template) # get LLM llm_response

        nl_actions = convert_to_dict(llm_response=llm_response)
        return nl_actions, llm_response
    
    def extract_pddl_action(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str,
            action_desc: str,
            predicates: list[Predicate]=None,
            types: dict[str,str]=None
            ) -> tuple[Action, list[Predicate], str]:
        """
        Construct an action from a given action description using LLM

        Args:
            model (LLM_Chat): LLM
            prompt_template (str): action construction prompt
            action_name (str): action name
            action_desc (str): action description
            predicates (list[Predicate]): list of predicates
            max_iters (int): max # of iterations to construct action
            feedback (bool): whether to request feedback from LM - default True
            feedback_template (str): feedback template. Has to be specified if feedback is used - defaults None

        Returns:
            Action: constructed action class
            new_predicates list[Predicate]: a list of new predicates

        """

        model.reset_tokens()
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        
        prompt_template += "\n\n## Action name:\n" + action_name
        prompt_template += "\n\n## Action description:\n" + action_desc
        if types:
            prompt_template += "\n\n## Available types:\n" + format_dict(types)
        if predicates:
            prompt_template += "\n\n## Available Predicates:\n" + format_predicates(predicates)

        llm_response = model.get_output(prompt=prompt_template)

        action = parse_action(llm_response=llm_response, action_name=action_name)
        new_predicates = parse_new_predicates(llm_response)
        
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates

        return action, new_predicates, llm_response
 
    def extract_pddl_actions(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: PromptBuilder, 
        nl_actions: list[str]=None,
        predicates: list[Predicate]=None,
        types: dict[str,str]=None
        ) -> tuple[list[Action], list[Predicate], str]:
        
        model.reset_tokens()
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        if types:
            prompt_template += "\n\n## Available Types\n" + format_dict(types)
        if predicates:
            prompt_template += "\n\n## Available predicates:\n" + format_predicates(predicates)
        if nl_actions:
            prompt_template += "\n\n## Available actions:\n" + format_dict(nl_actions)

        llm_response = model.get_output(prompt=prompt_template)
        raw_actions = llm_response.split('## NEXT ACTION')
        
        actions = []
        for i in raw_actions:
            # define the regex patterns
            action_pattern = re.compile(r'\[([^\]]+)\]')
            rest_of_string_pattern = re.compile(r'\[([^\]]+)\](.*)', re.DOTALL)
            
            # search for the action name
            action_match = action_pattern.search(i)
            action_name = action_match.group(1) if action_match else None
            
            # extract the rest of the string
            rest_match = rest_of_string_pattern.search(i)
            rest_of_string = rest_match.group(2).strip() if rest_match else None
            
            actions.append(parse_action(llm_response=rest_of_string, action_name=action_name))
        
        new_predicates = parse_new_predicates(llm_response)
        
        if predicates:
            new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates

        return actions, new_predicates, llm_response 
        
    def extract_parameters(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            types: dict[str,str]=None
            ) -> tuple[OrderedDict, str]:
        """
        Constructs parameters for singular action.
        Returns: 
            params (str): string of parameters
        """
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        prompt_template += "\n\n## Action name:\n" + action_name
        prompt_template += "\n\n## Action description:\n" + action_desc
        if types:
            prompt_template += "\n\n## Available Types\n" + format_dict(types)
            
        print("PROMPT TEMPLATE", prompt_template)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response

        param, param_raw = parse_params(llm_output=llm_response)

        return param, param_raw, llm_response
    
    def extract_preconditions(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            params: list[str], 
            predicates: list[Predicate]=None
            ) -> tuple[str, list[Predicate], str]:
        """
        Constructs preconditions for singular action.
        Returns: 
            precond (str): string containing PDDL preconditions
            preds (list[Predicate]): list of Predicate instances
        """

        model.reset_tokens()

        prompt_template += "\n\n## Domain\n" + domain_desc
        prompt_template += "\n\n## Action name:\n" + action_name
        prompt_template += "\n\n## Action description:\n" + action_desc
        prompt_template += "\n\n## Parameters:\n" + "\n".join(params)
        if predicates:
            prompt_template += "\n\n## Available predicates:\n" + format_predicates(predicates)
            
        print("PROMPT TEMPLATE", prompt_template)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response

        preconditions = llm_response.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        
        new_predicates = parse_new_predicates(llm_output=llm_response)

        return preconditions, new_predicates, llm_response

    def extract_effects(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            params: list[str], 
            precondition: str=None,
            predicates: list[Predicate]=None
            ) -> tuple[str, list[Predicate], str]:
        """
        Constructs effects for singular action.
        Returns: 
            effects (str): string containing PDDL effects
            preds (list[Predicate]): list of Predicate instances
        """
        model.reset_tokens()
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        
        prompt_template += "\n\n## Action name:\n" + action_name
        prompt_template += "\n\n## Action description:\n" + action_desc
        prompt_template += "\n\n## Parameters:\n" + "\n".join(params)
        prompt_template += "\n\n## Preconditions:\n" + precondition
        if predicates:
            prompt_template += "\n\n## Available predicates:\n" + format_predicates(predicates)
            
        print("PROMPT TEMPLATE", prompt_template)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response

        effects = llm_response.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        new_predicates = parse_new_predicates(llm_output=llm_response)

        return effects, new_predicates, llm_response
        
    def extract_predicates(
        self, 
        model: LLM_Chat,
        domain_desc: str,
        prompt_template: str=PromptBuilder, 
        types: dict[str,str]=None,
        predicates: list[Predicate]=None,
        nl_actions: dict[str,str]=None
        ) -> tuple[list[Predicate], str]: 
        
        model.reset_tokens() # reset tokens
        
        prompt_template += "\n\n## Domain\n" + domain_desc
        if types:
            prompt_template += "\n\n## Available Types\n" + format_dict(types)
        if predicates:
            prompt_template += "\n\n## Available predicates:\n" + format_predicates(predicates)
        if nl_actions:
            prompt_template += "\n\n## Available actions:\n" + "\n".join(f"{name}: {desc}" for name, desc in nl_actions.items())
        
        llm_response = model.get_output(prompt=prompt_template) # prompt model
        
        new_predicates = parse_new_predicates(llm_output=llm_response)
        
        return new_predicates, llm_response


    """Delete functions"""
    def delete_type(self, name: str):
        self.types = {type_: desc for type_, desc in self.types.items() if type_ != name}

    def delete_nl_action(self, name: str):
        self.nl_actions = {action_name: action_desc for action_name, action_desc in self.nl_actions.items() if action_name != name}

    def delete_pddl_action(self, name: str):
        self.pddl_actions = [action for action in self.pddl_actions if action['name'] != name]

    def delete_predicates(self, name: str):
        self.predicates = [predicate for predicate in self.predicates if predicate['name'] != name]


    """Set functions"""
    def set_types(self, types: dict[str,str]):
        self.types=types

    def set_type_hierarchy(self, type_hierarchy: dict[str,str]):
        self.type_hierarchy=type_hierarchy

    def set_nl_actions(self, nl_actions: dict[str,str]):
        self.nl_actions=nl_actions

    def set_pddl_action(self, pddl_action: Action):
        self.pddl_actions.append(pddl_action)

    def set_predicate(self, predicate: Predicate):
        self.predicates.append(predicate)

    """Get functions"""
    def get_types(self):
        return self.types

    def get_type_hierarchy(self):
        return self.type_hierarchy

    def get_nl_actions(self):
        return self.nl_actions

    def get_pddl_actions(self):
        return self.pddl_actions

    def generate_domain(
            self, 
            domain: str, 
            types: str, 
            predicates: str, 
            actions: list[Action],
            requirements: list[str],
            ) -> str:

        # Main function to generate the domain description
        desc = ""
        desc += f"(define (domain {domain})\n"
        desc += f"(:requirements\n  {" ".join(requirements)}\n)\n"
        desc += f"   (:types \n{types}\n   )\n\n"
        desc += f"   (:predicates \n{predicates}\n   )"
        desc += self.action_descs(actions)
        desc += "\n)"
        desc = desc.replace("AND", "and").replace("OR", "or")  # The python PDDL package can't handle capital AND and OR
        return desc
    
    # Helper function to format individual action descriptions
    def action_desc(self, action: Action) -> str:
        param_str = "\n".join([f"{name} - {type}" for name, type in action['parameters'].items()])  # name includes ?
        desc = f"(:action {action['name']}\n"
        desc += f"   :parameters (\n{param_str}\n   )\n"
        desc += f"   :precondition\n{action['preconditions']}\n"
        desc += f"   :effect\n{action['effects']}\n"
        desc += ")"
        return desc

    # Helper function to combine all action descriptions
    def action_descs(self, actions) -> str:
        desc = ""
        for action in actions:
            desc += "\n\n" + self.action_desc(action)
        return desc

if __name__ == "__main__":
    pass