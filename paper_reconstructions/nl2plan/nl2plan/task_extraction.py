import os
from l2p import *
from .utils import set_prompt

class TaskExtraction:
    def __init__(self):
        self.prompt_template = PromptBuilder()
        self.task_builder = TaskBuilder()
        self.feedback_builder = FeedbackBuilder()
        self.syntax_validator = SyntaxValidator()

        
    def task_extraction(
        self, 
        model: LLM, 
        problem_desc: str, 
        task_extraction_prompt: PromptBuilder, 
        types: dict[str,str],
        predicates: list[Predicate], 
        feedback_prompt: str,
        error_prompt: str,
        max_attempts: int = 8
        ) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]]]:

        objects, initial, goal, llm_response = self.task_builder.extract_task(
            model=model,
            problem_desc=problem_desc,
            prompt_template=task_extraction_prompt.generate_prompt(),
            types=format_types(types),
            predicates=predicates
        )
        
        all_valid = True
        for _ in range(max_attempts):
            
            feedback_msgs = []
            all_valid = True
            types_list = format_types(types)
            types_list = {k: types_list[k] for i, k in enumerate(types_list) if i != 0}
            
            # list of validation checks
            validation_checks = [
                self.syntax_validator.validate_task_objects(objects, types_list),
                self.syntax_validator.validate_task_states(initial, objects, predicates, "initial"),
                self.syntax_validator.validate_task_states(goal, objects, predicates, "goal"),
            ]

            # Perform each validation check
            for validator, args in validation_checks:
                is_valid, feedback_msg = validator, args
                if not is_valid:
                    all_valid = False
                    feedback_msgs.append(feedback_msg)

            # If any check fails, append feedback messages
            if not all_valid:
                error_prompt = error_prompt.replace("{error_msg}", str(feedback_msgs))
                error_prompt = error_prompt.replace("{task}", "goal and state extraction")
                objects, initial, goal, _ = self.feedback_builder.task_feedback(
                    model=model,
                    problem_desc=problem_desc,
                    llm_response=llm_response,
                    feedback_template=error_prompt,
                    feedback_type="llm"
                )
                
            else: break
        
        if not all_valid:
            raise ValueError(f"Validation failed: {feedback_msgs}")

        objects, initial, goal, _ = self.feedback_builder.task_feedback(
            model=model,
            problem_desc=problem_desc,
            llm_response=llm_response,
            feedback_template=feedback_prompt,
            feedback_type="llm",
            predicates=predicates,
            types=types,
            objects=objects,
            initial=initial,
            goal=goal,
        )

        objects = self.task_builder.format_objects(objects)
        initial = self.task_builder.format_initial(initial)
        goal = self.task_builder.format_goal(goal)

        return objects, initial, goal
    
if __name__ == "__main__":
    
    engine = "gpt-4o-mini"
    api_key = os.environ.get("OPENAI_API_KEY")
    
    openai_llm = OPENAI(model=engine, api_key=api_key)
    
    hierarchy = {
        'object': 'Object is always root, everything is an object', 
        'children': [
            {'movable_object': 'A meta-type that includes all objects that can be moved by the robot arm.', 
                'children': [
                    {'block': 'A type of movable_object.', 'children': []}
                    ]
            }, 
            {'surface': 'A parent type for all surfaces, including tables.', 
                'children': [
                    {'table': 'A type of surface that serves as a base for the blocks.', 'children': []}
                    ]
            }
            ]
        }
    
    
    predicates = [{'name': 'on_surface', 'desc': 'true if the block ?b is on the surface ?s', 'raw': '(on_surface ?b - block ?s - surface): true if the block ?b is on the surface ?s', 'params': OrderedDict([('?b', 'block'), ('?s', 'surface')]), 'clean': '(on_surface ?b - block ?s - surface): true if the block ?b is on the surface ?s'},
                {'name': 'held', 'desc': 'true if the block ?b is currently held by the robot arm', 'raw': '(held ?b - block): true if the block ?b is currently held by the robot arm', 'params': OrderedDict([('?b', 'block')]), 'clean': '(held ?b - block): true if the block ?b is currently held by the robot arm'},
                {'name': 'movable', 'desc': "'The block is movable (not under another block)'", 'raw': "(movable ?b - block): 'The block is movable (not under another block)'", 'params': OrderedDict([('?b', 'block')]), 'clean': "(movable ?b - block): 'The block is movable (not under another block)'"},
                {'name': 'on_block', 'desc': "'Indicates that block ?b is placed on top of block ?b2'", 'raw': "(on_block ?b - block ?b2 - block): 'Indicates that block ?b is placed on top of block ?b2'", 'params': OrderedDict([('?b', 'block'), ('?b2', 'block')]), 'clean': "(on_block ?b - block ?b2 - block): 'Indicates that block ?b is placed on top of block ?b2'"}]
    
    task_extraction = TaskExtraction()
    
    task_extraction.prompt_template = set_prompt(
        task_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/task_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/task_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/task_extraction/task.txt")
    
    object, initial, goal = task_extraction.task_extraction(
        model=openai_llm, 
        problem_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/task1.txt"), 
        task_extraction_prompt=task_extraction.prompt_template,
        types=hierarchy,
        predicates=predicates,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/feedback.txt"),
        error_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/error.txt")
        )
    
    print(object)
    print(initial)
    print(goal)