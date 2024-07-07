from .utils.pddl_types import Predicate, Action
from .utils.pddl_parser import parse_objects, parse_initial, parse_goal
from .llm_builder import LLM_Chat
from .prompt_builder import PromptBuilder

class Task_Builder:
    def __init__(self, objects: dict[str,str], initial: dict[str,str], goal: str):
        self.objects=objects
        self.initial=initial
        self.goal=goal

    def extract_objects(self, 
            model: LLM_Chat, 
            domain_desc: str, 
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate],
            action_desc: dict[str,str]
            ) -> dict[str,str]:
        
        model.reset_token_usage()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])

        action_str = ""
        for action, description in action_desc.items():
            action_str += f"Action: {action}\nDescription: {description}\n\n"

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(type_hierarchy))
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{actions}', action_str)

        llm_response = model.get_response(prompt=prompt_template) # get LLM response

        # implement parsing function to obtain dict[str,str] consisting of PDDL objects {"name": "desc"}

        pass

    def extract_initial_state(self, model: LLM_Chat, prompt_template: PromptBuilder):
        llm_response = model.get_response(prompt_template)
        print(llm_response.strip())

    def extract_goal_state(self, model: LLM_Chat, prompt_template: PromptBuilder):
        pass


    def extract_task(
            self, 
            model: LLM_Chat, 
            problem_desc: str,
            domain_desc: str, 
            prompt_template: PromptBuilder, 
            types: dict[str,str], 
            predicates: list[Predicate],
            actions: list[Action]
            ) -> tuple[str,str,str]:
        """
        Extracts objects, initial, and goal states from LLM output given domain description, types, and predicates
        Returns -> tuple[str,str,str]
        """
        model.reset_tokens()

        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])

        desc = ""
        for action in actions:
            param_str = "\n".join([f"{name} - {type}" for name, type in action['parameters'].items()])  # name includes ?
            desc += f"(:action {action['name']}\n"
            desc += f"   :parameters (\n{param_str}\n   )\n"
            desc += f"   :precondition\n{action['preconditions']}\n"
            desc += f"   :effect\n{action['effects']}\n"
            desc += ")\n\n"

        prompt_template = prompt_template.replace('{domain_desc}', domain_desc)
        prompt_template = prompt_template.replace('{type_hierarchy}', str(types))
        prompt_template = prompt_template.replace('{predicates}', predicate_str)
        prompt_template = prompt_template.replace('{actions}', desc)
        prompt_template = prompt_template.replace('{problem_desc}', problem_desc)

        llm_response = model.get_output(prompt=prompt_template)

        print("LLM RESPONSE TASK BUILDER:\n", llm_response)

        objects = parse_objects(llm_response)
        initial = parse_initial(llm_response)
        goal = parse_goal(llm_response)

        return objects, initial, goal




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

if __name__ == "__main__":
    

    actions_dict = {
    'pick_up_block': 'The robot arm picks up a block from its current location. Example: robot_arm picks up block_1 from table.',
    'place_on_table': 'The robot arm places a block on the table. Example: robot_arm places block_2 on table.',
    'place_on_block': 'The robot arm places a block on top of another block. Example: robot_arm places block_3 on top of block_4.',
    'move_block': 'The robot arm moves a block from one location to another. Example: robot_arm moves block_5 from table to stack_1.',
    'move_arm': 'The robot arm moves to a different location. Example: robot_arm moves to table.'
    }

    action_str = ""
    for action, description in actions_dict.items():
        action_str += f"Action: {action}\n Description: {description}\n\n"

    print(action_str)
