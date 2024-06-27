"""
This file contains collection of functions for PDDL generation purposes
"""

## I want to implement a LLM-critic (LLM-driven feedback list) for soft-constraints

import re, ast, os, itertools, copy
from .utils.pddl_output_utils import parse_new_predicates, parse_params, combine_blocks
from .utils.pddl_types import Predicate, Action
from .utils.logger import Logger
from .utils.pddl_generator import PddlGenerator
from .pddl_syntax_validator import PDDL_Syntax_Validator
from .llm_builder import LLM_Chat, get_llm
from .prompt_builder import PromptBuilder
from .utils.pddl_types import Predicate, Action

class Domain_Builder:
    def __init__(self, domain, types, type_hierarchy, predicates, nl_actions, pddl_actions):
        self.domain=domain
        self.types=types
        self.type_hierarchy=type_hierarchy
        self.predicates=predicates
        self.nl_actions=nl_actions
        self.pddl_actions=pddl_actions


    def extract_type(self, model, prompt):
        """Requires prompt"""

        model.reset_token_usage()

        response = model.get_response(prompt)
        
        if "## Types" in response:
            header = response.split("## Types")[1].split("## ")[0]
        else:
            header = response
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

        self.types=type_dict
    

    def extract_type_hierarchy(self, model, prompt, type_list):
        """Requires list of types"""

        model.reset_token_usage()

        response = model.get_response(prompt + "\n" + str(type_list))

        dict_pattern = re.compile(r'{.*}', re.DOTALL) # regular expression to find the JSON-like dictionary structure
        match = dict_pattern.search(response) # search for the pattern in the response
        
        if match:
            dict_str = match.group(0)
            
            # safely evaluate the string to convert it into a Python dictionary
            try:
                type_hierarchy = ast.literal_eval(dict_str)
                self.type_hierarchy=type_hierarchy
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return None
        else:
            print("No dictionary found in the response.")
            return None
        

    def extract_NL_actions(
            self, 
            model: LLM_Chat,
            domain: str, 
            prompt_template: PromptBuilder, 
            type_hierarchy: dict, 
            feedback: bool=False, 
            feedback_template: str=None
            ) -> dict[str,str]:
        
        """
        Extract actions in natural language given domain description using LLM.

        Args:
            model (LLM_Chat): LLM
            domain (str): domain description
            prompt_template (PromptBuilder): prompt template class
            type_hierarchy (dict): type hierarchy
            feedback (bool): whether to request feedback from LM - default True
            feedback_template (str): feedback template. Has to be specified if feedback is used - defaults None

        Returns:
            nl_actions (dict[str, str]): a dictionary of extracted actions, where the keys are action names and values are action descriptions
        """

        model.reset_token_usage()

        prompt_template = prompt_template.replace('{domain_desc}', domain)
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
                    {'role': 'assistant', 'content': llm_output},
                    {'role': 'user', 'content': feedback_msg}
                ]
                llm_response = llm_conn.get_response(messages=messages)
                Logger.print("LLM Response:\n", llm_response)
                actions = parse_actions(llm_response)
        """

        # action_strs = [f"{name}: {desc}" for name, desc in actions.items()]
        # print(f"Extracted {len(actions)} actions: \n - ", "\n - ".join(action_strs))

        self.nl_actions=nl_actions

        return nl_actions



    def extract_pddl_action(
            self, 
            model: LLM_Chat, 
            prompt_template: str, 
            action: dict[str, str], 
            predicates: list[Predicate], 
            max_iters: int=8, 
            feedback: bool=False, 
            feedback_template: str=None
            ) -> tuple[Action, list[Predicate]]:
        """
        Construct an action from a given action description using LLM

        Args:
            model (LLM_Chat): LLM
            prompt_template (str): action construction prompt
            action (dict[str,str]): name-description key-value pair
            predicates (list[Predicate]): list of predicates
            max_iters (int): max # of iterations to construct action
            feedback (bool): whether to request feedback from LM - default True
            feedback_template (str): feedback template. Has to be specified if feedback is used - defaults None

        Returns:
            Action: constructed action class
            new_predicates list[Predicate]: a list of new predicates

        """

        action_name, action_desc = action.items()[0] # extract action name and description

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
            print("LLM Output:\n", llm_response)

            new_predicates = parse_new_predicates(llm_response)

            ## SECTION TO ADD FEEDBACK MECHANISM

        else:
            print(f"Reached maximum iterations. Stopping action construction for {action_name}.")

        action = self.parse_action(llm_response, action_name)
        new_predicates = parse_new_predicates(llm_response)

        # remove re-defined predicates
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]]

        self.pddl_actions.append(action)
        self.predicates.extend(new_predicates)

        return action, new_predicates


        # model.reset_token_usage()
        # response = model.get_response(prompt + "\n\n Here is the given type hierarchy and actions list: \n" + str(self.type_hierarchy) + "\n" + str(self.nl_actions))
        # self.pddl_actions = response
    

    def shorten_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Only keep the latest LLM output and correction feedback
        """
        if len(messages) == 1:
            return [messages[0]]
        else:
            short_message = [messages[0]] + messages[-2:]
            assert short_message[1]['role'] == 'assistant'
            assert short_message[2]['role'] == 'user'
            return short_message


    def parse_action(llm_output: str, action_name: str) -> Action:
        """
        Parse an action from a given LLM output.

        Args:
            llm_output (str): The LLM output.
            action_name (str): The name of the action.

        Returns:
            Action: The parsed action.
        """
        #parameters = llm_output.split("Parameters:")[1].split("```")[1].strip()
        parameters = parse_params(llm_output)
        try:
            preconditions = llm_output.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        except:
            raise Exception("Could not find the 'Preconditions' section in the output. Provide the entire response, including all headings even if some are unchanged.")
        try:
            effects = llm_output.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        except:
            raise Exception("Could not find the 'Effects' section in the output. Provide the entire response, including all headings even if some are unchanged.")
        return {"name": action_name, "parameters": parameters, "preconditions": preconditions, "effects": effects}

    def get_llm_feedback(model, feedback_template: str, llm_output: str, predicates: list[Predicate], new_predicates: list[Predicate]) -> str | None:
        all_predicates = predicates + [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]]
        action_params = combine_blocks(llm_output.split("Parameters")[1].split("##")[0])
        action_preconditions = llm_output.split("Preconditions")[1].split("##")[0].split("```")[1].strip(" `\n")
        action_effects = llm_output.split("Effects")[1].split("##")[0].split("```")[-2].strip(" `\n")
        predicate_list = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in all_predicates])

        feedback_prompt = feedback_template.replace('{action_params}', action_params)
        feedback_prompt = feedback_prompt.replace('{action_preconditions}', action_preconditions)
        feedback_prompt = feedback_prompt.replace('{action_effects}', action_effects)
        feedback_prompt = feedback_prompt.replace('{predicate_list}', predicate_list)

        Logger.print("Requesting feedback from LLM", subsection=False)
        Logger.log("Feedback prompt:\n", feedback_prompt)
        feedback = model.get_response(prompt=feedback_prompt).strip()
        Logger.log("Received feedback:\n", feedback)
        if "no feedback" in feedback.lower() or len(feedback.strip()) == 0:
            Logger.print(f"No Received feedback:\n {feedback}")
            return None
        
        return feedback

    def prune_predicates(predicates: list[Predicate], actions: list[Action]) -> list[Predicate]:
        """
        Remove predicates that are not used in any action.

        Args:
            predicates (list[Predicate]): A list of predicates.
            actions (list[Action]): A list of actions.

        Returns:
            list[Predicate]: The pruned list of predicates.
        """
        used_predicates = []
        for pred in predicates:
            for action in actions:
                # Add a space or a ")" to avoid partial matches 
                names = [f"{pred['name']} ", f"{pred['name']})"]
                for name in names:
                    if name in action['preconditions'] or name in action['effects']:
                        used_predicates.append(pred)
                        break
        return used_predicates

    def mirror_action(action: Action, predicates: list[Predicate]):
        """
        Mirror any symmetrical predicates used in the action preconditions. 

        Example:
            Original action:
            (:action drive
                :parameters (
                    ?truck - truck
                    ?from - location
                    ?to - location
                )
                :precondition
                    (and
                        (at ?truck ?from)
                        (connected ?to ?from)
                    )
                :effect
                    (at ?truck ?to )
                )
            )
            
            Mirrored action:
            (:action drive
                :parameters (
                    ?truck - truck
                    ?from - location
                    ?to - location
                )
                :precondition
                    (and
                        (at ?truck ?from)
                        ((connected ?to ?from) or (connected ?from ?to))
                    )
                :effect
                    (at ?truck ?to )
                )
            )
        """
        mirrored = copy.deepcopy(action)
        for pred in predicates:
            if pred["name"] not in action["preconditions"]:
                continue # The predicate is not used in the preconditions
            param_types = list(pred["params"].values())
            for type in set(param_types): 
                # For each type
                if not param_types.count(type) > 1:
                    continue # The type is not repeated
                # The type is repeated
                occs = [i for i, x in enumerate(param_types) if x == type]
                perms = list(itertools.permutations(occs))
                if len(occs) > 2:
                    Logger.print(f"[WARNING] Mirroring predicate with {len(occs)} occurences of {type}.", subsection=False)
                uses = re.findall(f"\({pred['name']}.*\)", action["preconditions"]) # Find all occurrences of the predicate used in the preconditions
                for use in uses:
                    versions = [] # The different versions of the predicate
                    args = [use.strip(" ()").split(" ")[o+1] for o in occs] # The arguments of the predicate
                    template = use
                    for i, arg in enumerate(args): # Replace the arguments with placeholders
                        template = template.replace(arg, f"[MIRARG{i}]", 1)
                    for perm in perms:
                        ver = template
                        for i, p in enumerate(perm):
                            # Replace the placeholders with the arguments in the permutation
                            ver = ver.replace(f"[MIRARG{i}]", args[p])
                        if ver not in versions:
                            versions.append(ver) # In case some permutations are the same (repeated args)
                    combined = "(" + " or ".join(versions) + ")"
                    mirrored["preconditions"] = mirrored["preconditions"].replace(use, combined)
        return mirrored

    def prune_types(types: list[str], predicates: list[Predicate], actions: list[Action]):
        """
        Prune types that are not used in any predicate or action.

        Args:
            types (list[str]): A list of types.
            predicates (list[Predicate]): A list of predicates.
            actions (list[Action]): A list of actions.

        Returns:
            list[str]: The pruned list of types.
        """
        used_types = []
        for type in types:
            for pred in predicates:
                if type in pred['params'].values():
                    used_types.append(type)
                    break
            else:
                for action in actions:
                    if type in action['parameters'].values():
                        used_types.append(type)
                        break
                    if type in action['preconditions'] or type in action['effects']: # If the type is included in a "forall" or "exists" statement
                        used_types.append(type)
                        break
        return used_types



    def add_type(self, model, prompt):
        # user inputs prompt to add a type to the domain, LLM takes current domain info and dynamically modifies file to integrate new type
        user_input = input("Please describe the type you would like to add to the domain file: ")
        self.extract_type(model, prompt + "\n" + user_input + " Here are the original types: \n" + str(self.types))

        # self.extract_NL_actions(model, ) ** WORK ON THIS TO COMPLETE REITERATED PIPELINE


    def add_action():
        # user inputs prompt to add an action to the domain, LLM takes current domain info and dynamically modifies file to integrate new action
        pass


    def delete_type():
        pass


    def delete_action():
        pass


    def extract_NL_action():
        # singular action
        pass


    def extract_action():
        pass


    def generate_domain(self, model, prompt):
        model.reset_token_usage()
        response = model.get_response(prompt + "\n\n Here is the given type hierarchy and actions list: \n" + str(self.type_hierarchy) + "\n" + str(self.nl_actions) + "\n" + str(self.pddl_actions))
        print(response)


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