"""
This file contains collection of functions for PDDL domain generation purposes
"""

from collections import OrderedDict
from .utils.pddl_parser import parse_params, parse_new_predicates, parse_action, convert_to_dict, format_dict, format_predicates
from .utils.pddl_types import Predicate, Action
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder
import re, time

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

    """Extract functions"""
    def extract_type(
        self, 
        model: LLM_Chat, 
        domain_desc: str, 
        prompt_template: str,
        types: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[dict[str,str], str]:
        """
        Extracts types with domain given

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            types (dict[str,str]): current types in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            type_dict (dict[str,str]): dictionary of types with (name:description) pair
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:
                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template) # prompt model

                # extract respective types from response
                types = convert_to_dict(llm_response=llm_response)
                
                return types, llm_response

            except Exception as e:
                print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract types.")
    
    def extract_type_hierarchy(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        types: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[dict[str,str], str]:
        """
        Extracts type hierarchy from types list and domain given

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            types (dict[str,str]): current types in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            type_hierarchy (dict[str,str]): dictionary of type hierarchy
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:

                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template)

                # extract respective types from response
                type_hierarchy = convert_to_dict(llm_response=llm_response)
                
                return type_hierarchy, llm_response
            
            except Exception as e:
                print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract type hierarchy.")
            
    def extract_nl_actions(
        self, 
        model: LLM_Chat,
        domain_desc: str, 
        prompt_template: str, 
        types: dict[str,str]=None,
        nl_actions: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[dict[str,str], str]:
        """
        Extract actions in natural language given domain description using LLM.

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            types (dict[str,str]): current types in model
            nl_actions (dict[str, str]): NL actions currently in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            nl_actions (dict[str, str]): a dictionary of extracted actions {action name: action description}
            llm_response (str): the raw string LLM response
        """
        
        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        nl_actions_str = "\n".join(f"{name}: {desc}" for name, desc in nl_actions.items()) if nl_actions else "No actions provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{nl_actions}', nl_actions_str)

        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:

                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template) # get LLM llm_response
                
                # extract respective types from response
                nl_actions = convert_to_dict(llm_response=llm_response)
                
                return nl_actions, llm_response
            
            except Exception as e:
                print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract NL actions.")
    
    def extract_pddl_action(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        action_name: str,
        action_desc: str=None,
        action_list: dict[str,str]=None,
        predicates: list[Predicate]=None,
        types: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[Action, list[Predicate], str]:
        """
        Extract an action and predicates from a given action description using LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): action construction prompt
            action_name (str): action name
            action_desc (str): action description
            action_list (dict[str,str]): dictionary of other actions to be translated
            predicates (list[Predicate]): list of predicates in current model
            types (dict[str,str]): current types in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            action (Action): constructed action class
            new_predicates (list[Predicate]): a list of new predicates
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        predicates_str = format_predicates(predicates) if predicates else "No predicates provided."
        action_list_str = str(action_list) if action_list else "No other actions provided"
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_list}', action_list_str)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc if action_desc else "No description available.")
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicates_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:

                model.reset_tokens()
                
                llm_response = model.get_output(prompt=prompt_template)

                # extract respective types from response
                action = parse_action(llm_response=llm_response, action_name=action_name)
                new_predicates = parse_new_predicates(llm_response)

                return action, new_predicates, llm_response
            
            except Exception as e:
                print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract PDDL action.")
 
    def extract_pddl_actions(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        nl_actions: dict[str,str]=None,
        predicates: list[Predicate]=None,
        types: dict[str,str]=None
        ) -> tuple[list[Action], list[Predicate], str]:
        """
        Extract all actions from a given action description using LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): action construction prompt
            nl_actions (dict[str, str]): NL actions currently in model
            predicates (list[Predicate]): list of predicates
            types (dict[str,str]): current types in model

        Returns:
            action (Action): constructed action class
            new_predicates (list[Predicate]): a list of new predicates
            llm_response (str): the raw string LLM response
        """
        
        model.reset_tokens()
        
        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        predicates_str = format_predicates(predicates) if predicates else "No predicates provided."
        nl_actions_str = format_dict(nl_actions) if nl_actions else "No actions provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicates_str)
        prompt_template = prompt_template.replace('{nl_actions}', nl_actions_str)

        llm_response = model.get_output(prompt=prompt_template)
        
        # extract respective types from response
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
            
        # if user queries predicate creation via LLM
        try:
            new_predicates = parse_new_predicates(llm_response)
            
            if predicates:
                new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates
        except Exception as e:
            # Log or print the exception if needed
            print(f"No new predicates: {e}")
            new_predicates = None

        return actions, new_predicates, llm_response 
        
    def extract_parameters(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        action_name: str, 
        action_desc: str, 
        types: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[OrderedDict, list, str]:
        """
        Extracts parameters from single action description via LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            action_name (str): action name
            action_desc (str): action description
            types (dict[str,str]): current types in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            param (OrderedDict): ordered list of parameters
            param_raw (list()): list of raw parameters
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:
                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template) # get LLM response
                
                # extract respective types from response
                param, param_raw = parse_params(llm_output=llm_response)

                return param, param_raw, llm_response
            
            except Exception as e:
                print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract parameters.")
    
    def extract_preconditions(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        action_name: str, 
        action_desc: str, 
        params: list[str]=None, 
        predicates: list[Predicate]=None,
        max_retries: int=3
        ) -> tuple[str, list[Predicate], str]:
        """
        Extracts preconditions from single action description via LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            action_name (str): action name
            action_desc (str): action description
            params (list[str]): list of parameters from action
            predicates (list[Predicate]): list of current predicates in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            preconditions (str): PDDL format of preconditions
            new_predicates (list[Predicate]): a list of new predicates
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        predicates_str = format_predicates(predicates) if predicates else "No predicates provided."
        params_str = "\n".join(params) if params else "No parameters provided."

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{parameters}', params_str)
        prompt_template = prompt_template.replace('{predicates}', predicates_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:
                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template) # get LLM response
                
                # extract respective types from response
                preconditions = llm_response.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
                new_predicates = parse_new_predicates(llm_output=llm_response)

                return preconditions, new_predicates, llm_response
            
            except Exception as e:
                    print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract preconditions.")

    def extract_effects(
        self, 
        model: LLM_Chat, 
        domain_desc: str,
        prompt_template: str, 
        action_name: str, 
        action_desc: str, 
        params: list[str]=None, 
        precondition: str=None,
        predicates: list[Predicate]=None,
        max_retries: int=3
        ) -> tuple[str, list[Predicate], str]:
        """
        Extracts effects from single action description via LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            action_name (str): action name
            action_desc (str): action description
            params (list[str]): list of parameters from action
            precondition (str): PDDL format of preconditions
            predicates (list[Predicate]): list of current predicates in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            effects (str): PDDL format of effects
            new_predicates (list[Predicate]): a list of new predicates
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        predicates_str = format_predicates(predicates) if predicates else "No predicates provided."
        params_str = "\n".join(params) if params else "No parameters provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{parameters}', params_str)
        prompt_template = prompt_template.replace('{preconditions}', precondition)
        prompt_template = prompt_template.replace('{predicates}', predicates_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:
                model.reset_tokens()

                llm_response = model.get_output(prompt=prompt_template) # get LLM response
                
                # extract respective types from response
                effects = llm_response.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
                new_predicates = parse_new_predicates(llm_output=llm_response)

                return effects, new_predicates, llm_response
            
            except Exception as e:
                    print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract effects.")
        
    def extract_predicates(
        self, 
        model: LLM_Chat,
        domain_desc: str,
        prompt_template: str, 
        types: dict[str,str]=None,
        predicates: list[Predicate]=None,
        nl_actions: dict[str,str]=None,
        max_retries: int=3
        ) -> tuple[list[Predicate], str]: 
        """
        Extracts predicates via LLM

        Args:
            model (LLM_Chat): LLM
            domain_desc (str): domain description
            prompt_template (str): prompt template
            types (dict[str,str]): current types in model
            predicates (list[Predicate]): list of current predicates in model
            nl_actions (dict[str, str]): NL actions currently in model
            max_retries (int): max # of retries if failure occurs

        Returns:
            new_predicates (list[Predicate]): a list of new predicates
            llm_response (str): the raw string LLM response
        """

        # replace prompt placeholders
        types_str = format_dict(types) if types else "No types provided."
        predicates_str = format_predicates(predicates) if predicates else "No predicates provided."
        nl_actions_str = "\n".join(f"{name}: {desc}" for name, desc in nl_actions.items()) if nl_actions else "No actions provided."
        
        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicates_str)
        prompt_template = prompt_template.replace('{nl_actions}', nl_actions_str)
        
        # iterate through attempts in case of extraction failure
        for attempt in range(max_retries):
            try:
                model.reset_tokens()
                
                llm_response = model.get_output(prompt=prompt_template) # prompt model
                
                # extract respective types from response
                new_predicates = parse_new_predicates(llm_output=llm_response)
                
                return new_predicates, llm_response
            
            except Exception as e:
                    print(f"Error encountered: {e}. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(1) # add a delay before retrying
                
        raise RuntimeError("Max retries exceeded. Failed to extract predicates.")


    """Delete functions"""
    def delete_type(self, name: str):
        """Deletes specific type from current model"""
        if self.types is not None:
            self.types = {type_: desc for type_, desc in self.types.items() if type_ != name}

    def delete_nl_action(self, name: str):
        """Deletes specific NL action from current model"""
        if self.nl_actions is not None:
            self.nl_actions = {action_name: action_desc for action_name, action_desc in self.nl_actions.items() if action_name != name}

    def delete_pddl_action(self, name: str):
        """Deletes specific PDDL action from current model"""
        if self.pddl_actions is not None:
            self.pddl_actions = [action for action in self.pddl_actions if action['name'] != name]

    def delete_predicates(self, name: str):
        """Deletes specific predicate from current model"""
        if self.predicates is not None:
            self.predicates = [predicate for predicate in self.predicates if predicate['name'] != name]


    """Set functions"""
    def set_types(self, types: dict[str,str]):
        """Sets types for current model"""
        self.types=types

    def set_type_hierarchy(self, type_hierarchy: dict[str,str]):
        """Sets type hierarchy for current model"""
        self.type_hierarchy=type_hierarchy

    def set_nl_actions(self, nl_actions: dict[str,str]):
        """Sets NL actions for current model"""
        self.nl_actions=nl_actions

    def set_pddl_action(self, pddl_action: Action):
        """Appends a PDDL action for current model"""
        self.pddl_actions.append(pddl_action)

    def set_predicate(self, predicate: Predicate):
        """Appends a predicate for current model"""
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
        desc += f"(:requirements\n  {' '.join(requirements)}\n)\n"
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

    def format_predicates(self, predicates: list[Predicate]) -> str:
        return "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])

if __name__ == "__main__":
    pass