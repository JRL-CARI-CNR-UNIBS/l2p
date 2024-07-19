from .utils.pddl_types import Predicate, Action
from .utils.pddl_parser import parse_objects, parse_initial, parse_goal, convert_to_dict
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder

class Task_Builder:
    def __init__(self, objects: dict[str,str], initial: dict[str,str], goal: str):
        self.objects=objects
        self.initial=initial
        self.goal=goal

    def extract_objects(self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str, 
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate]
            ) -> dict[str,str]:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        types_str = "\n".join(type_hierarchy)

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template) # get LLM response
        
        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            objects = convert_to_dict(parts[1].strip())
        else:
            objects = {}

        return objects

    def extract_initial_state(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str,
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate],
            objects: dict[str,str]
            ) -> str:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        types_str = "\n".join(type_hierarchy)
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{objects}', objects_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        # FIX THIS SO THAT IT JUST RETURNS STRING INSTEAD OF DICT

        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            initial = convert_to_dict(parts[1].strip())
        else:
            initial = {}

        initial = "\n".join(initial.keys())

        return initial
        
    def extract_goal_state(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str,
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate],
            objects: dict[str,str]
            ) -> str:
        
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        types_str = "\n".join(type_hierarchy)
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', types_str)
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{objects}', objects_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            goal = parts[1].strip()
        else:
            goal = "Could not parse answer. Here is original LLM response:\n" + llm_response

        return goal

    def extract_task(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str, 
            prompt_template: PromptBuilder, 
            types: dict[str,str], 
            predicates: list[Predicate],
            actions: list[Action]
            ) -> tuple[str,str,str,str]:
        """
        Extracts objects, initial, and goal states from LLM output given domain description, types, and predicates
        Returns -> tuple[str,str,str]
        """
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        action_str = self.format_action(actions=actions)

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(types))
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{actions}', action_str)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        print("LLM RESPONSE TASK BUILDER:\n", llm_response)

        objects = parse_objects(llm_response)
        initial = parse_initial(llm_response)
        goal = parse_goal(llm_response)

        return objects, initial, goal, llm_response


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

if __name__ == "__main__":

    pass