"""
This file uses inputted NL descriptions to generate prompts for LLM
"""

import os

class PromptBuilder:
    def __init__(self, role, technique, examples: list, task, domain):
        self.role = role
        self.technique = technique
        self.examples = examples
        self.task = task
        self.domain = domain
        self.prompt = self.generate_prompt()


    def set_role(self, role):
        self.role = role
        self.prompt = self.generate_prompt()

    def set_technique(self, technique):
        self.technique = technique
        self.prompt = self.generate_prompt()

    def set_examples(self, example):
        self.examples.append(example)
        self.prompt = self.generate_prompt()

    def set_task(self, task):
        self.task = task
        self.prompt = self.generate_prompt()

    def set_domain(self, domain):
        self.domain = domain
        self.prompt = self.generate_prompt()


    def get_role(self):
        return self.role

    def get_technique(self):
        return self.technique

    def get_examples(self):
        return self.examples

    def get_task(self):
        return self.task

    def get_domain(self):
        return self.domain

    def get_prompt(self):
        return self.prompt


    def remove_role(self):
        self.role = ""
        self.prompt = self.generate_prompt()

    def remove_technique(self):
        self.technique = ""
        self.prompt = self.generate_prompt()

    def remove_examples(self, idx):
        del self.examples[idx]
        self.prompt = self.generate_prompt()

    def remove_task(self):
        self.task = ""
        self.prompt = self.generate_prompt()

    def remove_domain(self):
        self.domain = ""
        self.prompt = self.generate_prompt()


    def generate_prompt(self):
        prompt = ""

        if self.role:
            prompt += f"[ROLE]: {self.role}\n\n"

        if self.technique:
            prompt += f"[TECHNIQUE]: {self.technique}\n\n"

        if self.examples:
            prompt += f"[EXAMPLE(S)]:\n"
            for i, example in enumerate(self.examples, 1):
                prompt += f"Example {i}:\n{example}\n\n"

        if self.task:
            prompt += f"[TASK]: {self.task}\n\n"

        if self.domain:
            prompt += f"[DOMAIN]: {self.domain}\n"

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