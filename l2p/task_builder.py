from .utils.pddl_types import Predicate, Action
from .llm_builder import LLM_Chat, get_llm
from .prompt_builder import PromptBuilder

class Task_Builder:
    def __init__(self, domain, objects, initial, goal):
        self.domain=domain
        self.objects=objects
        self.initial=initial
        self.goal=goal

    def extract_nl_objects(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate],
            action_desc: dict[str,str],
            feedback: bool=False, 
            feedback_template: str=None
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

        # implement parsing function to obtain dict[str,str] consisting of NL objects {"name": "desc"}

        pass

    def extract_pddl_objects(self, 
            model: LLM_Chat, 
            domain_desc: str, 
            prompt_template: PromptBuilder,
            type_hierarchy: dict[str,str], 
            predicates: list[Predicate],
            action_desc: dict[str,str],
            feedback: bool=False, 
            feedback_template: str=None
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

    def extract_initial_state(self, model: LLM_Chat, prompt_template: str):
        llm_response = model.get_response(prompt_template)
        print(llm_response.strip())

    def extract_goal_state():
        pass

    def generate_task():
        pass

if __name__ == "__main__":
    
    # task = Task_Builder()
    # description = "The AI agent here is a mechanical robot arm that can pick and place the blocks. Only one block may be moved at a time: it may either be placed on the table or placed atop another block. Because of this, any blocks that are, at a given time, under another block cannot be moved."
    
    # print(task.extract_initial_state("GPT-3.5-Turbo", description))

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
