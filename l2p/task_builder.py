"""
This file contains collection of functions for PDDL task generation purposes
"""

from .utils.pddl_types import Predicate, Action
from .utils.pddl_parser import parse_objects, parse_initial, parse_goal, convert_to_dict, format_dict, format_predicates
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder

class TaskBuilder:
    def __init__(
        self, 
        objects: dict[str,str]=None, 
        initial: str=None, 
        goal: str=None
        ):
        
        self.objects=objects
        self.initial=initial
        self.goal=goal

    def extract_objects(self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str, 
            prompt_template: PromptBuilder,
            types: dict[str,str], 
            predicates: list[Predicate]
            ) -> tuple[dict[str,str], str]:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates]) \
            if predicates else "No predicates provided."
        types_str = "\n".join(types) if types else "No types provided."

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response
        
        objects = parse_objects(llm_response)

        return objects, llm_response

    def extract_initial_state(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str,
            prompt_template: PromptBuilder,
            types: dict[str,str]=None, 
            predicates: list[Predicate]=None,
            objects: dict[str,str]=None
            ) -> tuple[list[dict[str,str]], str]:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates]) \
            if predicates else "No predicates provided."
        types_str = "\n".join(types) if types else "No types provided."
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()]) if objects else "No objects provided."

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{objects}', objects_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        initial = parse_initial(llm_response)

        return initial, llm_response
        
    def extract_goal_state(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str,
            prompt_template: PromptBuilder,
            types: dict[str,str]=None, 
            predicates: list[Predicate]=None,
            objects: dict[str,str]=None,
            initial: str=None
            ) -> tuple[list[dict[str,str]], str]:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates]) \
            if predicates else "No predicates provided."
        types_str = "\n".join(types) if types else "No types provided."
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()]) if objects else "No objects provided."

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{objects}', objects_str)
        prompt_template = prompt_template.replace('{initial_state}', initial if initial else "No initial state provided.")
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        goal = parse_goal(llm_response)

        return goal, llm_response

    def extract_task(
            self, 
            model: LLM_Chat, 
            problem_desc: str="",
            domain_desc: str="", 
            prompt_template: PromptBuilder="", 
            types: dict[str,str]=None, 
            predicates: list[Predicate]=None,
            actions: list[Action]=None
            ) -> tuple[dict[str,str],list[dict[str,str]],list[dict[str,str]],str]:
        """
        Extracts objects, initial, and goal states from LLM output given domain description, types, and predicates
        Returns -> tuple[str,str,str]
        """
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates]) \
            if predicates else "No predicates provided."
        types_str = "\n".join(types) if types else "No types provided."
        action_str = self.format_action(actions=actions) if actions else "No actions provided."

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{types}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{actions}', action_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)
        
        llm_response = model.get_output(prompt=prompt_template)

        objects = parse_objects(llm_response)
        initial = parse_initial(llm_response)
        goal = parse_goal(llm_response)

        return objects, initial, goal, llm_response


    def extract_nl_initial():
        pass
    
    def extract_nl_goal():
        pass

    def extract_nl_conditions(
        self, 
        model: LLM_Chat, 
        problem_desc: str,
        domain_desc: str,
        prompt_template: PromptBuilder,
        type_hierarchy: dict[str,str]=None, 
        predicates: list[Predicate]=None,
        objects: dict[str,str]=None) -> str:
        """Extracts initial and goal states in natural language"""
        
        model.reset_tokens()

        if predicates:
            predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
            prompt_template = prompt_template.replace('{predicates}', predicate_str)
        if type_hierarchy:
            types_str = "\n".join(type_hierarchy)
            prompt_template = prompt_template.replace('{type_hierarchy}', types_str)
        if objects:
            objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
            prompt_template = prompt_template.replace('{objects}', objects_str)

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)
        
        return llm_response


    def delete_objects(self, name):
        self.objects = {var: type_ for var, type_ in self.objects.items() if var != name}
    
    def delete_initial_state(self):
        self.initial=None
    
    def delete_goal_state(self):
        self.goal=None


    def set_objects(self, objects: dict[str,str]):
        self.set_objects = objects

    def set_initial(self, initial: dict[str,str]):
        self.set_initial = initial

    def set_goal(self, goal: str):
        self.goal = goal


    def get_objects(self) -> dict[str,str]:
        return self.objects

    def get_initial(self) -> dict[str,str]:
        return self.initial
    
    def get_objects(self) -> str:
        return self.goal


    def generate_task(self, domain: str, objects: str, initial: str, goal: str):
        # Write problem file
        desc = "(define\n"
        desc += f"   (problem {domain}_problem)\n"
        desc += f"   (:domain {domain})\n\n"
        desc += f"   (:objects \n{objects}\n   )\n\n"
        desc += f"   (:init\n{initial}\n   )\n\n"
        desc += f"   (:goal\n{goal}\n   )\n\n"
        desc += ")"
        desc = desc.replace("AND","and").replace("OR","or") # The python PDDL package can't handle capital AND and OR
        return desc
    
    def format_action(self, actions: list[Action]) -> str:
        desc = ""
        for action in actions:
            param_str = "\n".join([f"{name} - {type}" for name, type in action['parameters'].items()])  # name includes ?
            desc += f"(:action {action['name']}\n"
            desc += f"   :parameters (\n{param_str}\n   )\n"
            desc += f"   :precondition\n{action['preconditions']}\n"
            desc += f"   :effect\n{action['effects']}\n"
            desc += ")\n\n"
        return desc

    def format_objects(self, objects: dict[str,str]) -> str:
        objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        return objects

    def format_initial(self, initial_states: list[dict[str,str]]) -> str:
        inner_str = [f"({state['name']} {' '.join(state['params'])})" for state in initial_states] # The main part of each predicate
        full_str = [f"(not {inner})" if state["neg"] else inner for state, inner in zip(initial_states, inner_str)] # Add the `not` if needed
        initial_states_str = "\n".join(full_str) # Combine the states into a single string
        
        return initial_states_str
    
    def format_goal(self, goal_states: list[dict[str,str]]) -> str:
        goal_states_str = "(AND \n"

        # loop through each dictionary in the list
        for item in goal_states:
            # extract the name and parameters from the dictionary
            name = item['name']
            params = " ".join(item['params'])
            goal_states_str += f"   ({name} {params}) \n" # append the predicate in the desired format

        goal_states_str += ")"
        
        return goal_states_str

if __name__ == "__main__":
    pass