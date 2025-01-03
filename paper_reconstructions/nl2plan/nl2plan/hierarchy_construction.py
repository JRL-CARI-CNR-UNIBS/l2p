import os
from l2p import *

class HierarchyConstruction:
    def __init__(self):
        self.prompt_template = PromptBuilder()
        self.domain_builder = DomainBuilder()
        self.feedback_builder = FeedbackBuilder()
        self.type_hierarchy = dict[str, str]
    
    def set_prompt(self, role_path: str, examples_path: str, task_path: str):
        
        role = load_file(role_path)
        examples = load_files(examples_path)
        task = load_file(task_path)
        
        self.prompt_template.set_role(role=role)
        for ex in examples:
            self.prompt_template.set_examples(example=ex)
        self.prompt_template.set_task(task=task)
        
    def set_types(self, types: dict[str,str]):
        self.type_hierarchy = types
    
    def hierarchy_construction(
        self, 
        model: LLM, 
        domain_desc: str, 
        type_hierarchy_prompt: PromptBuilder, 
        types: dict[str,str],
        feedback_prompt: str
        ) -> dict[str, str]:

        type_hierarchy, _ = self.domain_builder.extract_type_hierarchy(
            model=model,
            domain_desc=domain_desc,
            prompt_template=type_hierarchy_prompt.generate_prompt(),
            types=types,
        )

        type_hierarchy, _ = self.feedback_builder.type_hierarchy_feedback(
            model=model,
            domain_desc=domain_desc,
            feedback_template=feedback_prompt,
            feedback_type="llm",
            type_hierarchy=type_hierarchy,
            llm_response="",
        )

        return type_hierarchy
    
if __name__ == "__main__":
    
    engine = "gpt-4o-mini"
    api_key = os.environ.get("OPENAI_API_KEY")
    
    openai_llm = OPENAI(model=engine, api_key=api_key)
    
    types = {
        'block': 'The individual units that can be picked and placed by the robot arm. They can be stacked or placed on a table.', 
        'table': 'A flat surface where blocks can be placed. It serves as a base for the blocks.', 
        'movable_object': 'A meta-type that includes all objects that can be moved by the robot arm, specifically blocks in this case.'}
    
    hierarchy_construction = HierarchyConstruction()
    hierarchy_construction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/task.txt")
    
    type_hierarchy = hierarchy_construction.hierarchy_construction(
        model=openai_llm, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        type_hierarchy_prompt=hierarchy_construction.prompt_template,
        types=types,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/hierarchy_construction/feedback.txt"))
    
    print(type_hierarchy)