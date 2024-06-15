"""
This file uses inputted NL descriptions to generate prompts for LLM
"""

class PromptBuilder:
    def __init__(self):
        self.domain_description = ""
        self.role = ""
        self.COT_example = []
        self.task = ""

    def set_domain_description(self, description):
        self.domain_description = description

    def set_role(self, role):
        self.role = role

    def set_COT_example(self, example):
        self.COT_example.append(example)

    def set_task(self, task):
        self.task = task

    def generate_prompt(self):
        prompt = ""

        if self.role:
            prompt += f"Role: {self.role}\n\n"
        
        if self.COT_example:
            prompt += f"Chain-of-Thought Example(s):\n"
            for i, example in enumerate(self.COT_example, 1):
                prompt += f"Example {i}:\n{example}\n\n"

            prompt += "\n"

        if self.task:
            prompt += f"Task: {self.task}\n\n"

        if self.domain_description:
            prompt += f"Domain Description: {self.domain_description}\n"

        return prompt.strip()


# USAGE EXAMPLE
if __name__ == "__main__":
    prompt_gen = PromptBuilder()

    prompt_gen.set_role("You are an assistant skilled in generating PDDL components.")
    prompt_gen.set_domain_description("A robot navigates a grid-like environment with obstacles.")
    prompt_gen.set_COT_example("First, identify all grid cells.")
    prompt_gen.set_COT_example("Next, determine which cells are occupied by obstacles.")
    prompt_gen.set_task("Generate necessary PDDL predicates for the robot to navigate the grid.")

    final_prompt = prompt_gen.generate_prompt()
    print(final_prompt)