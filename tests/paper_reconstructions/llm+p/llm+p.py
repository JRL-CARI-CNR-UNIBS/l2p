"""
Paper: "LLM+P: Empowering Large Language Models with Optimal Planning Proficiency" Liu et al (2023)
Source code: https://github.com/Cranial-XIX/llm-pddl
python3 -m tests.paper_reconstructions.llm+p.llm+p

Assumes the following:
    1. NL task description
    2. Ground-truth PDDL domain
"""

from l2p.task_builder import TaskBuilder
from l2p.llm_builder import GPT_Chat
from planner import FastDownward
from openai import OpenAI
import os

def get_context():
    blocksworld_p_example_nl = \
    """
    You have 5 blocks. 
    b2 is on top of b5. 
    b5 is on top of b1. 
    b1 is on top of b4. 
    b3 is on top of b2. 
    b4 is on the table. 
    b3 is clear. 
    Your arm is empty. 
    Your goal is to move the blocks. 
    b4 should be on top of b3. 
    """

    blocksworld_p_example_pddl = \
    """
    (define (problem BW-rand-5)
    (:domain blocksworld-4ops)
    (:objects b1 b2 b3 b4 b5 )
    (:init
    (arm-empty)
    (on b1 b4)
    (on b2 b5)
    (on b3 b2)
    (on-table b4)
    (on b5 b1)
    (clear b3)
    )
    (:goal
    (and
    (on b4 b3))
    )
    )
    """

    blocksworld_p_example_sol = \
    """
    unstack b3 from b2,
    putdown b3,
    unstack b2 from b5,
    putdown b2,
    unstack b5 from b1,
    putdown b5,
    unstack b1 from b4,
    putdown b1,
    pickup b4,
    stack b4 on b3
    """
    
    return blocksworld_p_example_nl, blocksworld_p_example_pddl, blocksworld_p_example_sol

def create_llm_ic_pddl_prompt(task_nl, context):
        # our method (LM+P), create the problem PDDL given the context
        context_nl, context_pddl, context_sol = context
        prompt = f"I want you to solve planning problems. " + \
                f"An example planning problem is: \n {context_nl} \n" + \
                f"The problem PDDL file to this problem is: \n {context_pddl} \n" + \
                f"Do not attempt to declare any types.\n" + \
                f"Now I have a new planning problem and its description is: \n {task_nl} \n" + \
                f"The problem you are to extract from is under the header '## Problem description'\n" + \
                f"Do not, under any circumstance, output the answers in PDDL format. Final answer must be in the following format at the end: \n" + \
"""
## OBJECTS
```
truck1 - truck
```

## INITIAL
```
(at truck1 chicago_depot): truck1 is at the chicago_depot
```

## GOAL
```
(AND ; all the following should be done
   (finalised house1) ; house 1 is done
)
```"""

        return prompt
     
task_nl = \
"""
You have 3 blocks. 
b3 is on top of b2. 
b1 is on top of b3. 
b2 is on the table. 
b1 is clear. 
Your arm is empty. 
Your goal is to move the blocks. 
b2 should be on top of b3. 
b3 should be on top of b1. 
"""

if __name__ == "__main__":
  
  # setup L2P requirements
  engine = "gpt-4o-mini"

  client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
  model = GPT_Chat(client=client, engine=engine)
  task_builder = TaskBuilder()
  planner = FastDownward()

  # prompt function taken from LLM+P
  prompt = create_llm_ic_pddl_prompt(task_nl, get_context())

  # extract PDDL from prompt
  objects, initial, goal, llm_response = task_builder.extract_task(model=model, prompt_template=prompt)

  # construct PDDL components into PDDL problem file
  objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
  pddl_problem = task_builder.generate_task("blocksworld-4ops", objects, initial, goal)

  # write down PDDL problem file
  problem_file = "tests/paper_reconstructions/llm+p/problem.pddl"
  domain_file = "tests/paper_reconstructions/llm+p/domain.pddl"
  with open(problem_file, "w") as f:
      f.write(pddl_problem)

  # run planner
  planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    