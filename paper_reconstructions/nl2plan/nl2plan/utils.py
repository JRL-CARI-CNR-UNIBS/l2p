from l2p import PromptBuilder
from l2p import load_file, load_files

def set_prompt(
    prompt_builder: PromptBuilder, 
    role_path: str, 
    examples_path: str, 
    task_path: str
    ) -> PromptBuilder:
        
    # load in files
    role = load_file(role_path)
    examples = load_files(examples_path)
    task = load_file(task_path)
    
    # set prompts to prompt builder class
    prompt_builder.set_role(role=role)
    for ex in examples:
        prompt_builder.set_examples(example=ex)
    prompt_builder.set_task(task=task)

    return prompt_builder