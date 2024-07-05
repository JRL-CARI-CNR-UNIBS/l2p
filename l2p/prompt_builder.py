"""
This file uses inputted NL descriptions to generate prompts for LLM
"""

import os

class PromptBuilder:
    def __init__(self, role: str=None, technique: str=None, examples: list=None, task: str=None):
        self.role = role
        self.technique = technique
        self.examples = examples
        self.task = task


    def set_role(self, role):
        self.role = role

    def set_technique(self, technique):
        self.technique = technique

    def set_examples(self, example):
        self.examples.append(example)

    def set_task(self, task):
        self.task = task


    def get_role(self):
        return self.role

    def get_technique(self):
        return self.technique

    def get_examples(self):
        return self.examples

    def get_task(self):
        return self.task


    def remove_role(self):
        self.role = None

    def remove_technique(self):
        self.technique = None

    def remove_examples(self, idx):
        del self.examples[idx]

    def remove_task(self):
        self.task = None


    def generate_prompt(self):
        prompt = ""

        if self.role:
            prompt += f"[ROLE]: {self.role}\n\n"
            prompt += "------------------------------------------------\n"

        if self.technique:
            prompt += f"[TECHNIQUE]: {self.technique}\n\n"
            prompt += "------------------------------------------------\n"

        if len(self.examples) > 0:
            prompt += f"[EXAMPLE(S)]:\n"
            for i, example in enumerate(self.examples, 1):
                prompt += f"Example {i}:\n{example}\n\n"

            prompt += "------------------------------------------------\n"

        if self.task:
            prompt += f"[TASK]: {self.task}\n\n"

        return prompt.strip()
    

# USAGE EXAMPLE
if __name__ == "__main__":
    def open_file(filepath):
        with open(filepath, 'r') as file:
            return file.read()

    role_file_path = 'data/prompt_templates/type_extraction/role.txt'
    role_desc = open_file(role_file_path)
    tech_file_path = 'data/prompt_templates/type_extraction/technique.txt'
    tech_desc = open_file(tech_file_path)
    task_file_path = 'data/prompt_templates/type_extraction/task.txt'
    task_desc = open_file(task_file_path)
    domain_file_path = 'data/domains/logistics.txt'
    domain_desc = open_file(domain_file_path)

    # Directory where example files are stored
    examples_dir = 'data/prompt_templates/type_extraction/examples/'
    example_files = [f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))]

    # Read all example files
    examples = [open_file(os.path.join(examples_dir, f)) for f in example_files]

    type_extraction_prompt = PromptBuilder(role_desc, tech_desc, examples, task_desc, domain_desc)

    print(type_extraction_prompt.get_prompt())