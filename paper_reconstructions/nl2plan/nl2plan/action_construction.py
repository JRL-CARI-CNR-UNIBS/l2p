import os
from l2p import *

class ActionConstruction:
    def __init__(self):
        self.prompt_template = PromptBuilder()
        self.domain_builder = DomainBuilder()
        self.feedback_builder = FeedbackBuilder()
        self.syntax_validator = SyntaxValidator()
        self.pddl_actions = list[Action]
        self.pddl_predicates = list[Predicate]
        
    
    def set_prompt(self, role_path: str, examples_path: str, task_path: str):
        
        role = load_file(role_path)
        examples = load_files(examples_path)
        task = load_file(task_path)
        
        self.prompt_template.set_role(role=role)
        for ex in examples:
            self.prompt_template.set_examples(example=ex)
        self.prompt_template.set_task(task=task)
        
        
    def set_actions(self, actions: list[Action]):
        self.pddl_actions = actions
        
        
    def set_predicates(self, predicates: list[Predicate]):
        self.pddl_predicates = predicates
        
    
    def construct_action(
        self,
        model: LLM,
        domain_desc: str,
        act_constr_prompt: PromptBuilder,
        action_list: str,
        action_name: str,
        action_desc: str,
        predicates: list[Predicate],
        type_hierarchy: dict[str,str],
        syntax_validator: SyntaxValidator,
        feedback_prompt: str = None,
        max_attempts = 2,
        feedback = True
        ) -> tuple[Action, list[Predicate]]:
        """
        Construct a single action from a given action description using LLM language model.
        
        Args:
            model (LLM): The LLM language model connection.
            act_constr_prompt (PromptBuilder): action construction prompt.
            action_name (str): The name of the action.
            action_desc (str): The action description.
            predicates (list[Predicate]): A list of predicates.
            syntax_validator (SyntaxValidator): The PDDL syntax validator.
            feedback_prompt (str): Feedback template.
            max_iters (int): Maximum number of iterations to construct action. Defaults to 8.
            feedback (bool): Whether to request feedback from LLM. Defaults to True.
            
        Returns:
            Action: The constructed action.
            new_predicates (list[Predicate]): A list of new predicates
        """
        
        # fill in action construction prompt placeholders
        action_prompt = act_constr_prompt.generate_prompt()
        action_prompt = action_prompt.replace('{action_desc}', action_desc)
        action_prompt = action_prompt.replace('{action_name}', action_name)
        
        if len(predicates) == 0:
            predicate_str = "No predicate has been defined yet"
        else:    
            predicate_str = ""
            predicate_str = "\n".join([f"- {pred['clean']}" for pred in predicates])
        action_prompt = action_prompt.replace('{predicates}', predicate_str)
        
        # replace specific feedback template
        if feedback_prompt is not None:
            feedback_prompt = feedback_prompt.replace('{action_desc}', action_desc)
            feedback_prompt = feedback_prompt.replace('{action_name}', action_name)
        elif feedback:
            raise ValueError("Feedback template is required when feedback is enabled.")
            
        for iter in range(1, max_attempts + 1 + (feedback is not None)):
            print(f"Generating PDDL of action: `{action_name}`")
            
            try: 
                action, new_predicates, llm_response, validation_info = self.domain_builder.extract_pddl_action(
                        model=model,
                        domain_desc=domain_desc,
                        prompt_template=action_prompt,
                        action_name=action_name,
                        action_desc=action_desc,
                        action_list=action_list,
                        predicates=predicates,
                        types=format_types(type_hierarchy),
                        syntax_validator=syntax_validator
                    )
            
                no_error, error_msg = validation_info
                
            except Exception as e:
                no_error = False
                error_msg = str(e)
                
            if no_error:
                if feedback is not None:
                    
                    action, new_predicates, response_fb, _, no_fb = self.feedback_builder.pddl_action_feedback(
                        model=model,
                        domain_desc=domain_desc,
                        llm_response=llm_response,
                        feedback_template=feedback_prompt,
                        feedback_type="llm",
                        action=action,
                        predicates=predicates,
                        types=type_hierarchy
                    )
                    
                    if no_fb == True:
                        break
                    
            else:
                with open("paper_reconstructions/nl2plan/prompts/action_construction/error.txt") as f:
                    error_template = f.read().strip()
                error_prompt = error_template.replace('{action_name}', action_name)
                error_prompt = error_prompt.replace('{action_desc}', action_desc)
                error_prompt = error_prompt.replace('{predicate_list}', predicate_str)
                error_prompt = error_prompt.replace('{error_msg}', error_msg)
                error_prompt = error_prompt.replace('{llm_response}', llm_response)
                
                action, new_predicates, llm_response, validation_info = self.domain_builder.extract_pddl_action(
                        model=model,
                        domain_desc=domain_desc,
                        prompt_template=error_prompt,
                        action_name=action_name,
                        action_desc=action_desc,
                        action_list=action_list,
                        predicates=predicates,
                        types=type_hierarchy,
                        syntax_validator=syntax_validator
                    )
                    
        return action, new_predicates
            
    
    def action_construction(
        self,
        model: LLM,
        domain_desc: str,
        act_constr_prompt: PromptBuilder,
        nl_actions: dict[str,str],
        type_hierarchy: dict[str,str],
        feedback_prompt: str | None = None,
        max_attempts: int = 2,
        max_iters: int = 2
        ) -> tuple[list[Action], list[Predicate]]:
        
        action_list = "\n".join([f"- {name}: {desc}" for name, desc in nl_actions.items()])
        
        syntax_validator = SyntaxValidator()
        
        predicates = []
        for iter in range(max_iters):
            actions = []
            print(f"Starting iteration {iter + 1} of action construction")
            curr_preds = len(predicates)
            
            for action_name, action_desc in nl_actions.items():
                action, new_predicates = self.construct_action(
                    model=model,
                    domain_desc=domain_desc,
                    act_constr_prompt=act_constr_prompt,
                    action_list=action_list,
                    action_name=action_name,
                    action_desc=action_desc,
                    predicates=predicates,
                    type_hierarchy=type_hierarchy,
                    syntax_validator=syntax_validator,
                    feedback_prompt=feedback_prompt,
                    max_attempts=max_attempts,
                    feedback=True
                    )
                actions.append(action)
                predicates.extend(new_predicates)
                predicates = prune_predicates(predicates, actions)
            
            if len(predicates) == curr_preds:
                print("No new predicates created. Stopping action construction.")
                break
        else:
            print("Reached maximum iterations. Stopping action construction.")
        
        return actions, predicates
        
    
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
    
    # nl_actions = {
    #     "pick_block": "The robot arm picks up a block from a surface. Requires the block to be on a surface and not currently held by the arm. Example: robot_arm picks up block_1 from table_1.",
    #     "place_on_table": "The robot arm places a block on a table. Requires the block to be held by the arm and the table to be clear of other blocks. Example: robot_arm places block_1 on table_1.",
    #     "place_on_block": "The robot arm places a block on top of another block. Requires the block to be held by the arm and the target block to be clear (not currently held or covered by another block). Example: robot_arm places block_1 on block_2.",
    #     "release_block": "The robot arm releases a block it is currently holding. Requires the block to be held by the arm. Example: robot_arm releases block_1."
    # }
    
    nl_actions = {'pick_block': 'The robot arm picks up a block from the table or from on top of another block. The block must be accessible and not currently under another block. Example: robot_arm picks up block_1 from the table.', 'place_on_table': 'The robot arm places a block onto the table. The block must be held by the robot arm and the table must be clear of any other blocks in that position. Example: robot_arm places block_1 on the table.', 'place_on_block': 'The robot arm places a block on top of another block. The block being placed must be held by the robot arm, and the block it is being placed on must be stable and not currently under another block. Example: robot_arm places block_1 on block_2.', 'release_block': 'The robot arm releases the currently held block without placing it on the table or another block. This action is used to drop the block. The block is no longer held by the robot arm after this action is performed. Example: robot_arm releases block_1.', 'check_accessibility': 'The robot arm checks if a block is accessible for picking. Example: robot_arm checks if block_1 is accessible.'}

    
    action_construction = ActionConstruction()
    action_construction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/action_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_construction/task.txt")
    
    actions, predicates, = action_construction.action_construction(
        model=openai_llm, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        act_constr_prompt=action_construction.prompt_template,
        nl_actions=nl_actions,
        type_hierarchy=hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_construction/feedback.txt"),
        max_attempts=1
        )
    
    for i in actions:
        print(i)
        
    print()
    
    for i in predicates:
        print(i)