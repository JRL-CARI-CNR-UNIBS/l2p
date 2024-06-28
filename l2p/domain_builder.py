"""
This file contains collection of functions for PDDL generation purposes
"""

import re, ast
from .utils.pddl_output_utils import parse_new_predicates, parse_action, combine_blocks
from .utils.pddl_types import Predicate, Action
from .utils.pddl_syntax_validator import PDDL_Syntax_Validator
from .utils.logger import Logger
from .llm_builder import LLM_Chat, get_llm
from .prompt_builder import PromptBuilder

# COMMMENT: Pass in only the required parameters. Everything else (i.e. types, hierarchy, nl_action list etc., are to be used within the class, not passed through)

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
            prompt_template: PromptBuilder
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

        model.reset_token_usage()

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)

        llm_response = model.get_response(prompt=prompt_template)
        
        if "## Types" in llm_response:
            header = llm_response.split("## Types")[1].split("## ")[0]
        else:
            header = llm_response
        dot_list = combine_blocks(header)
        if len(dot_list) == 0:
            dot_list = "\n".join([l for l in header.split("\n") if l.strip().startswith("-")])
        if dot_list.count("-") == 0: # No types
            return {}
        types = dot_list.split('\n')
        types = [t.strip("- \n") for t in types if t.strip("- \n")] # Remove empty strings and dashes

        type_dict = {
                t.split(":")[0].strip().replace(" ", "_"): 
                t.split(":")[1].strip()
            for t in types
        }

        # self.set_types(type_dict)

        return type_dict

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

        model.reset_token_usage()

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_list}', str(types))

        # feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        # feedback_template = feedback_template.replace('{type_list}', str(types))

        response = model.get_response(prompt=prompt_template)

        dict_pattern = re.compile(r'{.*}', re.DOTALL) # regular expression to find the JSON-like dictionary structure
        match = dict_pattern.search(response) # search for the pattern in the response
        
        if match:
            dict_str = match.group(0)
            
            # safely evaluate the string to convert it into a Python dictionary
            try:
                type_hierarchy = ast.literal_eval(dict_str)
                # self.type_hierarchy = type_hierarchy
                return type_hierarchy
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return None
        else:
            print("No dictionary found in the response.")
            return None
        
    def extract_nl_actions(
            self, 
            model: LLM_Chat,
            domain_desc: str, 
            prompt_template: PromptBuilder, 
            type_hierarchy: dict[str,str], 
            feedback: bool=False, 
            feedback_template: str=None
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

        model.reset_token_usage()

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(type_hierarchy))

        # feedback_template = feedback_template.replace('{domain_desc}', domain)
        # feedback_template = feedback_template.replace('{type_hierarchy}', str(type_hierarchy))

        llm_response = model.get_response(prompt=prompt_template) # get LLM response

        # extract list of actions section
        splits = llm_response.split("```")
        action_outputs = [splits[i].strip() for i in range(1, len(splits), 2)] # Every other split *should* be an action

        # parse actions into dict[str, str]
        nl_actions = {}
        for action in action_outputs:
            name = action.split("\n")[0].strip()
            desc = action.split("\n", maxsplit=1)[1].strip() # Works even if there is no blank line
            nl_actions[name] = desc

        """ SECTION TO ADD FEEDBACK MECHANISM
        if feedback is not None:
            if feedback.lower() == "human":
                action_strs = "\n".join([f"- {name}: {desc}" for name, desc in actions.items()])
                feedback_msg = human_feedback(f"\n\nThe actions extracted are:\n{action_strs}\n")
            else:
                feedback_msg = get_llm_feedback(llm_conn, actions, feedback_template)
            if feedback_msg is not None:
                messages = [
                    {'role': 'user', 'content': act_extr_prompt},
                    {'role': 'assistant', 'content': llm_response},
                    {'role': 'user', 'content': feedback_msg}
                ]
                llm_response = llm_conn.get_response(messages=messages)
                Logger.print("LLM Response:\n", llm_response)
                actions = parse_actions(llm_response)
        """

        # action_strs = [f"{name}: {desc}" for name, desc in actions.items()]
        # print(f"Extracted {len(actions)} actions: \n - ", "\n - ".join(action_strs))

        # self.nl_actions=nl_actions

        return nl_actions

    def extract_pddl_action(
            self, 
            model: LLM_Chat, 
            prompt_template: str, 
            action_name: str,
            action_desc: str,
            predicates: list[Predicate], 
            max_iters: int=0, 
            feedback: bool=False, 
            feedback_template: str=None
            ) -> tuple[Action, list[Predicate]]:
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

        # replace action name/description and predicates in prompt template
        prompt_template = prompt_template.replace('{action_name}', action_name)
        prompt_template = prompt_template.replace('{action_desc}', action_desc)

        if len(predicates) == 0:
            predicate_str = "No predicate has been defined yet."
        else:
            predicate_str = ""
            for i, pred in enumerate(predicates): predicate_str += f"{i+1}. {pred['name']}: {pred['desc']}\n"  
        
        prompt_template = prompt_template.replace('{predicate_list}', predicate_str)

        # replace action name and description in feedback template
        if feedback_template is not None:
            feedback_template = feedback_template.replace('{action_name}', action_name)
            feedback_template = feedback_template.replace('{action_desc}', action_desc)
        elif feedback:
            raise ValueError("Feedback template is required when feedback is enabled.")
        
        messages = [{'role': 'user', 'content': prompt_template}]

        # iteration phase to construct action 
        recieved_feedback_at = None
        for i in range(1, max_iters + 1 + (feedback is not None)):
            print(f'Generating PDDL of action: `{action_name}` | # of messages: {len(messages)}')

            llm_response = model.get_response(prompt=None, messages=messages)
            messages.append({'role': 'assistant', 'content': llm_response})
            # print("LLM Output:\n", llm_response)

            new_predicates = parse_new_predicates(llm_response)

            ## SECTION TO ADD FEEDBACK MECHANISM

        else:
            print(f"Reached maximum iterations. Stopping action construction for {action_name}.")

        action = parse_action(llm_response=llm_response, action_name=action_name)
        new_predicates = parse_new_predicates(llm_response)

        # remove re-defined predicates
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]]

        # self.pddl_actions.append(action)
        # self.predicates.extend(new_predicates)

        return action, new_predicates


    """Add functions"""
    def add_type(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            prompt_template: PromptBuilder
            ) -> dict[str,str]:
        """
        User inputs prompt to add a type to the domain, LLM takes current domain info and dynamically modifies file to integrate new type
        
        Args:
        Returns:
        """
        user_input = input("Please describe the type you would like to add to the domain file: ")

        # REPLACE WITH TEMPLATE REPLACEMENT CODE
        types = self.extract_type(model=model, domain_desc=domain_desc, prompt_template=prompt_template + "\n" + user_input + " Here are the original types. Do not change them: \n" + str(self.types))

        return types

    def add_action(self):
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

    def set_pddl_action(self, pddl_action: tuple[Action, list[Predicate]]):
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


if __name__ == "__main__":
    pass