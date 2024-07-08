"""
This file contains collection of functions for PDDL generation purposes
"""

from collections import OrderedDict
from .utils.pddl_parser import parse_params, parse_new_predicates, parse_action, convert_to_dict
from .utils.pddl_types import Predicate, Action
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder

class Domain_Builder:
    def __init__(
            self, 
            types: dict[str,str], 
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate], 
            nl_actions: dict[str,str], 
            pddl_actions: list[Action]
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
            ) -> dict[str,str]:
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

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc) # replace template holders

        if types != None:
            prompt_template = prompt_template.replace('{type_hierarchy}', str(types))
        else:
            prompt_template = prompt_template.replace('{type_hierarchy}', "No types available.")

        # print("TYPE PROMPT:\n", prompt_template)

        llm_response = model.get_output(prompt=prompt_template) # prompt model
        
        # print("RAW LLM RESPONSE FOR PDDL ACTION GENERATION:\n", llm_response)

        types = convert_to_dict(llm_response=llm_response)
        return types
    
    def extract_type_hierarchy(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            types: dict[str,str]
            ) -> dict[str,str]:
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

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_list}', str(types))

        llm_response = model.get_output(prompt=prompt_template)

        try:
            type_hierarchy = convert_to_dict(llm_response=llm_response)
            return type_hierarchy
        except Exception as e:
            print(f"An error occurred: {e}\n")
            print("RAW LLM RESPONSE FOR PDDL ACTION GENERATION:\n", llm_response)

    def extract_nl_actions(
            self, 
            model: LLM_Chat,
            domain_desc: str, 
            prompt_template: PromptBuilder, 
            type_hierarchy: dict[str,str],
            nl_actions: dict[str,str]=None
            ) -> dict[str,str]:
        
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

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(type_hierarchy))

        if nl_actions != None:
            prompt_template = prompt_template.replace('{actions}', str(nl_actions))
        else:
            prompt_template = prompt_template.replace('{actions}', "No actions available.")

        llm_response = model.get_output(prompt=prompt_template) # get LLM llm_response

        nl_actions = convert_to_dict(llm_response=llm_response)
        return nl_actions
    
    def extract_pddl_action(
            self, 
            model: LLM_Chat, 
            prompt_template: str, 
            action_name: str,
            action_desc: str,
            predicates: list[Predicate]
            ) -> tuple[Action, list[Predicate]]:
        
        # FIX PROMPT TEMPLATE AND CODE TO ACCOMODATE MORE UNIVERSAL PROMPT INPUTS

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

        predicate_str = (
            "No predicate has been defined yet."
            if len(predicates) == 0
            else "\n".join(f"{i + 1}. {pred['name']}: {pred['desc']}" for i, pred in enumerate(predicates))
        )

        # replace action name/description and predicates in prompt template
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{predicate_list}', predicate_str)
        llm_response = model.get_output(prompt=prompt_template)

        # extract actions and predicates - EVENTUALLY SWAP THESE FUNCTIONS
        action = parse_action(llm_response=llm_response, action_name=action_name)
        new_predicates = parse_new_predicates(llm_response)
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates

        return action, new_predicates

    def extract_parameters(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            types: dict[str,str]
            ) -> OrderedDict:
        """
        Constructs parameters for singular action.
        Returns: 
            params (str): string of parameters
        """

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(types))
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response
        parameter = parse_params(llm_output=llm_response)

        return parameter
    
    def extract_preconditions(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            params: list[str], 
            predicates: list[Predicate]
            ) -> tuple[str, list[Predicate]]:
        """
        Constructs preconditions for singular action.
        Returns: 
            precond (str): string containing PDDL preconditions
            preds (list[Predicate]): list of Predicate instances
        """

        model.reset_tokens()

        predicate_str = (
            "No predicate has been defined yet."
            if len(predicates) == 0
            else "\n".join(f"{i + 1}. {pred['name']}: {pred['desc']}" for i, pred in enumerate(predicates))
        )

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{parameters}', str(params))
        prompt_template = prompt_template.replace('{predicate_list}', predicate_str)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response

        preconditions = llm_response.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        new_predicates = parse_new_predicates(llm_output=llm_response)

        return preconditions, new_predicates

    def extract_effects(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            prompt_template: PromptBuilder, 
            action_name: str, 
            action_desc: str, 
            params: list[str], 
            precondition: str,
            predicates: list[Predicate]
            ) -> tuple[str, list[Predicate]]:
        """
        Constructs effects for singular action.
        Returns: 
            effects (str): string containing PDDL effects
            preds (list[Predicate]): list of Predicate instances
        """
        model.reset_tokens()

        predicate_str = (
            "No predicate has been defined yet."
            if len(predicates) == 0
            else "\n".join(f"{i + 1}. {pred['name']}: {pred['desc']}" for i, pred in enumerate(predicates))
        )

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)
        prompt_template = prompt_template.replace('{parameters}', str(params))
        prompt_template = prompt_template.replace('{precondition}', precondition)
        prompt_template = prompt_template.replace('{predicate_list}', predicate_str)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response

        # print("LLM RESPONSE EFFECTS\n", llm_response)

        effects = llm_response.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        new_predicates = parse_new_predicates(llm_output=llm_response)

        return effects, new_predicates



    """Add functions"""
    def add_type(self, model: LLM_Chat, domain_desc: str, prompt_template: PromptBuilder) -> dict[str,str]:
        """
        User inputs prompt to add a type to the domain, LLM takes current domain info and dynamically modifies file to integrate new type
        Args:
        Returns:
        """
        types = self.extract_type(model=model, domain_desc=domain_desc, prompt_template=prompt_template, types=self.types)
        return types
    
    def add_nl_action(self, model: LLM_Chat, domain_desc: str, prompt_template: PromptBuilder, type_hierarchy: dict[str,str]=None) -> dict[str,str]:
        nl_actions = self.extract_nl_actions(
            model, 
            domain_desc, 
            prompt_template, 
            type_hierarchy,
            nl_actions=self.nl_actions
            )

        return nl_actions

    def add_pddl_action(self):
        # user inputs prompt to add an action to the domain, LLM takes current domain info and dynamically modifies file to integrate new action
        pass

    def add_predicates(self):
        pass


    """Delete functions"""
    def delete_type(self):
        # DELETE BY NAME, NOT INDEX
        pass

    def delete_action(self):
        pass

    def delete_predicates(self):
        pass


    """Set functions"""
    def set_types(self, types: dict[str,str]):
        self.types=types

    def set_type_hierarchy(self, type_hierarchy: dict[str,str]):
        self.type_hierarchy=type_hierarchy

    def set_nl_actions(self, nl_actions: dict[str,str]):
        self.nl_actions=nl_actions

    def set_pddl_action(self, pddl_action: Action):
        self.pddl_actions.append(pddl_action)


    """Get functions"""
    def get_types(self):
        return self.types

    def get_type_hierarchy(self):
        return self.type_hierarchy

    def get_nl_actions(self):
        return self.nl_actions

    def get_pddl_actions(self):
        return self.pddl_actions

    def get_type_checklist():
        pass

    def get_hierarchy_checklist():
        pass

    def get_action_checklist():
        pass


    def generate_domain(self, domain: str, types: str, predicates: str, actions: list[Action]) -> str:
        # Helper function to format individual action descriptions
        def action_desc(action: Action) -> str:
            param_str = "\n".join([f"{name} - {type}" for name, type in action['parameters'].items()])  # name includes ?
            desc = f"(:action {action['name']}\n"
            desc += f"   :parameters (\n{param_str}\n   )\n"
            desc += f"   :precondition\n{action['preconditions']}\n"
            desc += f"   :effect\n{action['effects']}\n"
            desc += ")"
            return desc

        # Helper function to combine all action descriptions
        def action_descs(actions) -> str:
            desc = ""
            for action in actions:
                desc += "\n\n" + action_desc(action)
            return desc

        # Main function to generate the domain description
        desc = ""
        desc += f"(define (domain {domain})\n"
        desc += f"(:requirements\n   :strips :typing :equality :negative-preconditions :disjunctive-preconditions\n   :universal-preconditions :conditional-effects\n)\n"
        desc += f"   (:types \n{types}\n   )\n\n"
        desc += f"   (:predicates \n{predicates}\n   )"
        desc += action_descs(actions)
        desc += "\n)"
        desc = desc.replace("AND", "and").replace("OR", "or")  # The python PDDL package can't handle capital AND and OR
        return desc

if __name__ == "__main__":
    pass