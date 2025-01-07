import os
from l2p import *
from .utils import set_prompt

class ActionExtraction:
    def __init__(self):
        self.prompt_template = PromptBuilder()
        self.domain_builder = DomainBuilder()
        self.feedback_builder = FeedbackBuilder()
        self.nl_actions = dict[str,str]
    

    def action_extraction(
        self,
        model: LLM, 
        domain_desc: str, 
        action_extraction_prompt: PromptBuilder,
        type_hierarchy: dict[str,str],
        feedback_prompt: str
        ) -> dict[str, str]:
        
        nl_actions, response = self.domain_builder.extract_nl_actions(
            model=model,
            domain_desc=domain_desc,
            prompt_template=action_extraction_prompt.generate_prompt(),
            types=type_hierarchy,
        )

        nl_actions, response_fb = self.feedback_builder.nl_action_feedback(
            model=model,
            domain_desc=domain_desc,
            llm_response=response,
            feedback_template=feedback_prompt,
            feedback_type="llm",
            nl_actions=nl_actions,
            type_hierarchy=type_hierarchy,
        )

        return nl_actions
    
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
    
    action_extraction = ActionExtraction()
    
    action_extraction.prompt_template = set_prompt(
        action_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/action_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_extraction/task.txt")
    
    nl_actions = action_extraction.action_extraction(
        model=openai_llm, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        action_extraction_prompt=action_extraction.prompt_template,
        type_hierarchy=hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_extraction/feedback.txt"))
    
    for i in nl_actions:
        print(i)