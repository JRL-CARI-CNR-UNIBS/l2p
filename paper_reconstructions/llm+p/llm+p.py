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
from l2p.task_builder import TaskBuilder
from l2p.prompt_builder import PromptBuilder
from l2p.llm_builder import GPT_Chat
from tests.planner import FastDownward
from openai import OpenAI
from tests.setup import check_parse_domain, check_parse_problem

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

if __name__ == "__main__":
  
    # setup L2P requirements
    engine = "gpt-4o-mini"

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
    model = GPT_Chat(client=client, engine=engine)
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
        model=model, 
        problem_desc=problem_desc,
        prompt_template=prompt_builder.generate_prompt())

    # construct PDDL components into PDDL problem file
    object_str = task_builder.format_objects(objects)
    initial_state_str = task_builder.format_initial(initial)
    goal_state_str = task_builder.format_goal(goal)

    pddl_problem = task_builder.generate_task("blocksworld-4ops", object_str, initial_state_str, goal_state_str)

    # write down PDDL problem file
    problem_file = "paper_reconstructions/llm+p/results/problem.pddl"
    domain_file = "paper_reconstructions/llm+p/results/domain.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    # parse PDDL files
    pddl_domain = check_parse_domain(domain_file)
    with open(domain_file, "w") as f:
        f.write(pddl_domain)

    pddl_problem = check_parse_problem(problem_file)
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    # run planner
    planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    