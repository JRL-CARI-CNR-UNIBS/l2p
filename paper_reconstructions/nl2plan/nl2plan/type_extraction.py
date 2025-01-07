import os
from l2p import *
from .utils import set_prompt

class TypeExtraction:
    def __init__(self):
        self.prompt_template = PromptBuilder()
        self.domain_builder = DomainBuilder()
        self.feedback_builder = FeedbackBuilder()
        
        
    def type_extraction(
        self, 
        model: LLM, 
        domain_desc: str, 
        type_extraction_prompt: PromptBuilder, 
        feedback_prompt: str
        ) -> tuple[dict[str, str], str]:

        types, _ = self.domain_builder.extract_type(
            model=model, 
            domain_desc=domain_desc, 
            prompt_template=type_extraction_prompt.generate_prompt()
        )
        
        types, _ = self.feedback_builder.type_feedback(
            model=model,
            domain_desc=domain_desc,
            feedback_template=feedback_prompt,
            feedback_type="llm",
            types=types,
            llm_response="",
        )
        
        return types
    
if __name__ == "__main__":
    
    engine = "gpt-4o-mini"
    api_key = os.environ.get("OPENAI_API_KEY")
    
    openai_llm = OPENAI(model=engine, api_key=api_key)
    
    type_extraction = TypeExtraction()
    
    type_extraction.prompt_template = set_prompt(
        type_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/type_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/type_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/type_extraction/task.txt")
    
    types = type_extraction.type_extraction(
        model=openai_llm, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        type_extraction_prompt=type_extraction.prompt_template,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/type_extraction/feedback.txt"))
    
    print(types)