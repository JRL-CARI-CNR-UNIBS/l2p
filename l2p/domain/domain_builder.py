"""
This file contains collection of functions for PDDL generation purposes
"""

## I want to implement a LLM-critic (LLM-driven feedback list) for soft-constraints

import re, ast, os, itertools, copy
from ..utils.pddl_output_utils import parse_new_predicates, parse_params, combine_blocks
from ..utils.pddl_types import Predicate, Action
from ..utils.logger import Logger
from ..utils.pddl_generator import PddlGenerator
from ..pddl_syntax_validator import PDDL_Syntax_Validator

class Domain_Builder:
    def __init__(self, domain, types, type_hierarchy, predicates, nl_actions, pddl_actions):
        self.domain=domain
        self.types=types
        self.type_hierarchy=type_hierarchy
        self.predicates=predicates
        self.nl_actions=nl_actions
        self.pddl_actions=pddl_actions


    def extract_type(self, model, prompt):

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
        

    def extract_NL_actions(self, model, prompt):

        model.reset_token_usage()

        response = model.get_response(prompt + "\n\n Here are the given types and type hierarchy: \n" + str(self.types) + "\n" + str(self.type_hierarchy))

        splits = response.split("```")
        action_outputs = [splits[i].strip() for i in range(1, len(splits), 2)] # Every other split *should* be an action

        nl_actions = {}
        for action in action_outputs:
            name = action.split("\n")[0].strip()
            desc = action.split("\n", maxsplit=1)[1].strip() # works even if there is no blank line
            nl_actions[name] = desc

        self.nl_actions=nl_actions


    def extract_pddl_actions(self, model, prompt):

        model.reset_token_usage()
        response = model.get_response(prompt + "\n\n Here is the given type hierarchy and actions list: \n" + str(self.type_hierarchy) + "\n" + str(self.nl_actions))
        self.pddl_actions = response



    def action_construction(
        self, 
        model, 
        prompt_dir, 
        unsupported_keywords: list[str] = [],
        feedback: str | None = None,
        max_attempts: int = 8,
        shorten_message: bool = False,
        max_iters: int = 2,
        mirror_symmetry: bool = False
        ):

        model.reset_token_usage()
        
        action_list = "\n".join([f"- {name}: {desc}" for name, desc in self.nl_actions.items()])

        with open(os.path.join(prompt_dir, "main.txt")) as f:
            act_constr_template = f.read().strip()
        act_constr_template = act_constr_template.replace('{domain_desc}', self.domain)
        act_constr_template = act_constr_template.replace('{type_hierarchy}', str(self.type_hierarchy))
        act_constr_template = act_constr_template.replace('{action_list}', action_list)

        with open(os.path.join(prompt_dir, "feedback.txt")) as f:
            feedback_template = f.read().strip()
        feedback_template = feedback_template.replace('{domain_desc}', self.domain)
        feedback_template = feedback_template.replace('{type_hierarchy}', str(self.type_hierarchy))
        feedback_template = feedback_template.replace('{action_list}', action_list)


        syntax_validator = PDDL_Syntax_Validator(self.type_hierarchy, unsupported_keywords=unsupported_keywords)

        predicates = []
        for iter in range(max_iters):
            actions = []
            Logger.print(f"Starting iteration {iter + 1} of action construction", subsection=False)
            current_preds = len(predicates)
            for action_name, action_desc in self.nl_actions.items():
                action, new_predicates = self.construct_action(
                    model, act_constr_template, action_name, action_desc, predicates, syntax_validator, feedback_template, 
                    max_iters=max_attempts, feedback=feedback, shorten_message=shorten_message, mirror_symmetry=mirror_symmetry
                )
                actions.append(action)
                predicates.extend(new_predicates) 
            if len(predicates) == current_preds:
                Logger.print("No new predicates created. Stopping action construction.", subsection=False)
                break
        else:
            Logger.print("Reached maximum iterations. Stopping action construction.", subsection=False)

        predicates = self.prune_predicates(predicates, actions) # Remove predicates that are not used in any action
        types = self.type_hierarchy.types()
        pruned_types = self.prune_types(types, predicates, actions) # Remove types that are not used in any predicate or action

        Logger.print("Constructed actions:\n", "\n".join([str(action) for action in actions]))
        PddlGenerator.reset_actions()
        for action in actions:
            PddlGenerator.add_action(action)
        predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
        PddlGenerator.set_predicates(predicate_str)
        Logger.print(f"PREDICATES: {predicate_str}")
        
        in_tokens, out_tokens = model.token_usage()
        Logger.add_to_info(Action_Construction_Tokens=(in_tokens, out_tokens))

        return actions, predicates, pruned_types
    

    def construct_action(self, model, act_constr_prompt: str,
        action_name: str,
        action_desc: str,
        predicates: list[Predicate],
        syntax_validator: PDDL_Syntax_Validator,
        feedback_template: str = None,
        max_iters=8,
        shorten_message=False,
        feedback=True,
        mirror_symmetry=False):

        # constract an action from a given action description

        act_constr_prompt = act_constr_prompt.replace('{action_desc}', action_desc)
        act_constr_prompt = act_constr_prompt.replace('{action_name}', action_name)
        if len(predicates) == 0:
            predicate_str = "No predicate has been defined yet"
        else:
            predicate_str = ""
            for i, pred in enumerate(predicates): predicate_str += f"{i+1}. {pred['name']}: {pred['desc']}\n"            
        act_constr_prompt = act_constr_prompt.replace('{predicate_list}', predicate_str)

        if feedback_template is not None:
            feedback_template = feedback_template.replace('{action_desc}', action_desc)
            feedback_template = feedback_template.replace('{action_name}', action_name)
        elif feedback:
            raise ValueError("Feedback template is required when feedback is enabled.")

        messages = [{'role': 'user', 'content': act_constr_prompt}]

        received_feedback_at = None
        for iter in range(1, max_iters + 1 + (feedback is not None)):
            Logger.print(f'Generating PDDL of action: `{action_name}` | # of messages: {len(messages)}', subsection=False)

            msgs_to_send = messages if not shorten_message else self.shorten_messages(messages)
            Logger.log("Messages to send:\n", "\n".join([m["content"] for m in msgs_to_send]))
            llm_output = model.get_response(prompt=None, messages=msgs_to_send)
            messages.append({'role': 'assistant', 'content': llm_output})
            Logger.print("LLM Output:\n", llm_output)

            try:
                new_predicates = parse_new_predicates(llm_output)
                validation_info = syntax_validator.perform_validation(llm_output, curr_predicates = predicates, new_predicates = new_predicates)
                no_error, error_type, _, error_msg = validation_info
            except Exception as e:
                no_error = False
                error_msg = str(e)
                error_type = str(e.__class__.__name__)

            if no_error or error_type == "all_validation_pass":
                if received_feedback_at is None and feedback is not None:
                    received_feedback_at = iter
                    error_type = "feedback"
                    if feedback.lower() == "human":
                        action = self.parse_action(llm_output, action_name)
                        new_predicates = parse_new_predicates(llm_output)
                        preds = "\n".join([f"\t- {pred['clean']}" for pred in new_predicates])
                        msg  = f"\n\nThe action {action_name} has been constructed.\n\n"
                        msg += f"Action desc: \n\t{action_desc}\n\n"
                        msg += f"Parameters: \n\t{action['parameters']}\n\n"
                        msg += f"Preconditions: \n{action['preconditions']}\n\n"
                        msg += f"Effects: \n{action['effects']}\n\n"
                        msg += f"New predicates: \n{preds}\n"
                        # error_msg = human_feedback(msg)
                    else:
                        error_msg = self.get_llm_feedback(model, feedback_template, llm_output, predicates, new_predicates)
                    if error_msg is None:
                        break # No feedback and no error, so we can stop iterating
                else:
                    break # No error and feedback finished, so we can stop iterating

            Logger.print(f"Error of type {error_type} for action {action_name} iter {iter}:\n{error_msg}", subsection=False)

            prompt_dir = 'data/prompt_templates/action_construction/'

            with open(os.path.join(prompt_dir, "error.txt")) as f:
                error_template = f.read().strip()
            error_prompt = error_template.replace('{action_name}', action_name)
            error_prompt = error_prompt.replace('{action_desc}', action_desc)
            error_prompt = error_prompt.replace('{predicate_list}', predicate_str)
            error_prompt = error_prompt.replace('{error_msg}', error_msg)

            messages.append({'role': 'user', 'content': error_prompt})
        else:
            Logger.print(f"Reached maximum iterations. Stopping action construction for {action_name}.", subsection=False)

        action = self.parse_action(llm_output, action_name)
        new_predicates = parse_new_predicates(llm_output)
        # Remove re-defined predicates
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]]

        if mirror_symmetry:
            action = self.mirror_action(action, predicates + new_predicates)

        return action, new_predicates
    

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