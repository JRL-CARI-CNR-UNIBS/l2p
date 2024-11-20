"""
Paper: "LLM+P: Empowering Large Language Models with Optimal Planning Proficiency" Liu et al (2023)
Source code: https://github.com/Cranial-XIX/llm-pddl
Run: python3 -m tests.paper_reconstructions.llm+p.llm+p

Assumes the following:
    1. NL task description
    2. Ground-truth PDDL domain
    
This library only focuses on model generation, so it is not concerned with the other phase of LLM+P: LLM translating PDDL plans to NL
"""

import os
from l2p import *
from l2p.utils.pddl_planner import FastDownward

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

if __name__ == "__main__":
  
    # setup L2P requirements
    engine = "gpt-4o-mini"
    api_key = os.environ.get('OPENAI_API_KEY')
    openai_llm = OPENAI(model=engine, api_key=api_key)
    planner = FastDownward()

    # prompts taken from LLM+P
    role = open_file("paper_reconstructions/llm+p/prompts/role.txt")
    example = open_file("paper_reconstructions/llm+p/prompts/example.txt")
    task = open_file("paper_reconstructions/llm+p/prompts/task.txt")

    problem_desc = open_file("paper_reconstructions/llm+p/prompts/problem_desc.txt")

    # assemble prompt builder
    prompt_builder = PromptBuilder(role=role, examples=[example], task=task)

    task_builder = TaskBuilder()

    # extract PDDL from prompt
    objects, initial, goal, llm_response = task_builder.extract_task(
        model=openai_llm, 
        problem_desc=problem_desc,
        prompt_template=prompt_builder.generate_prompt())

    # construct PDDL components into PDDL problem file
    object_str = task_builder.format_objects(objects)
    initial_state_str = task_builder.format_initial(initial)
    goal_state_str = task_builder.format_goal(goal)

    pddl_problem = task_builder.generate_task("blocksworld-4ops", "blocksworld-4ops_problem", object_str, initial_state_str, goal_state_str)

    # write down PDDL problem file
    problem_file = "paper_reconstructions/llm+p/results/problem.pddl"
    domain_file = "paper_reconstructions/llm+p/results/domain.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    print("PDDL problem:\n", pddl_problem)

    # run planner
    planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    