"""
Paper: "NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions" Gestrin et al (2024)
Source code: https://github.com/mrlab-ai/NL2Plan
Run: python3 -m paper_reconstructions.nl2plan.main
"""

import argparse
from l2p import *
from .nl2plan.type_extraction import TypeExtraction
from .nl2plan.hierarchy_construction import HierarchyConstruction
from .nl2plan.action_extraction import ActionExtraction
from .nl2plan.action_construction import ActionConstruction
from .nl2plan.task_extraction import TaskExtraction
from .nl2plan.utils import set_prompt

DOMAINS = [
    "blocksworld",
    "household",
    "isr", # currently unsupported
    "isr-assisted", # currently unsupported
    "logistics",
    "tyreworld"
]

REQUIREMENTS = [
        ":strips",
        ":typing",
        ":equality",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":universal-preconditions",
        ":conditional-effects",
    ]

UNSUPPORTED_KEYWORDS = ["object", "pddl", "lisp"]

separator = "-" * 20

def run_nl2plan(args, domain: str, problem: str):
    # create necessary classes
    domain_builder = DomainBuilder() # L2P domain builder
    task_builder = TaskBuilder() # L2P task builder
    planner = FastDownward(planner_path=args.planner) # FastDownward planner
    log = "" # string to log all step output
    
    # initialize OpenAI engine
    api_key = os.environ.get("OPENAI_API_KEY")
    model = OPENAI(model=args.model, api_key=api_key)
    
    
    # A. Type Extraction
    type_extraction = TypeExtraction()
    type_extraction.prompt_template = set_prompt(
        type_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/type_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/type_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/type_extraction/task.txt")
    
    types = type_extraction.type_extraction(
        model=model, 
        domain_desc=load_file(f"paper_reconstructions/nl2plan/domains/{domain}/desc.txt"), 
        type_extraction_prompt=type_extraction.prompt_template,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/type_extraction/feedback.txt"))
    
    log += f"STEP ONE: TYPE EXTRACTION\n\n{types}\n\n"
    model.reset_tokens()
    
    # B. Hierarchy Construction
    hierarchy_construction = HierarchyConstruction()
    hierarchy_construction.prompt_template = set_prompt(
        hierarchy_construction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/task.txt")
    
    type_hierarchy = hierarchy_construction.hierarchy_construction(
        model=model, 
        domain_desc=load_file(f"paper_reconstructions/nl2plan/domains/{domain}/desc.txt"), 
        type_hierarchy_prompt=hierarchy_construction.prompt_template,
        types=types,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/hierarchy_construction/feedback.txt"))

    log += f"{separator}\nSTEP TWO: HIERARCHY CONSTRUCTION\n\n{type_hierarchy}\n\n"
    model.reset_tokens()
    
    # C. Action Extraction
    action_extraction = ActionExtraction()
    action_extraction.prompt_template = set_prompt(
        action_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/action_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_extraction/task.txt")
    
    nl_actions = action_extraction.action_extraction(
        model=model, 
        domain_desc=load_file(f"paper_reconstructions/nl2plan/domains/{domain}/desc.txt"), 
        action_extraction_prompt=action_extraction.prompt_template,
        type_hierarchy=type_hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_extraction/feedback.txt"))

    log += f"{separator}\nSTEP THREE: ACTION EXTRACTION\n\n{nl_actions}\n\n"
    model.reset_tokens()
    
    # D. Action Construction
    action_construction = ActionConstruction()
    action_construction.prompt_template = set_prompt(
        action_construction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/action_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_construction/task.txt")
    
    actions, predicates, = action_construction.action_construction(
        model=model, 
        domain_desc=load_file(f"paper_reconstructions/nl2plan/domains/{domain}/desc.txt"), 
        act_constr_prompt=action_construction.prompt_template,
        nl_actions=nl_actions,
        type_hierarchy=type_hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_construction/feedback.txt"),
        max_attempts=1
        )
    
    log += f"{separator}\n"
    log += "STEP FOUR: ACTION CONSTRUCTION\n\n"
    log += "ACTIONS:\n"
    log += '\n'.join([str(action) for action in actions]) + "\n\n"
    log += "PREDICATES:\n"
    log += '\n'.join([str(predicate) for predicate in predicates]) + "\n\n"
    model.reset_tokens()
    
    # E. Task Extraction
    task_extraction = TaskExtraction()
    task_extraction.prompt_template = set_prompt(
        task_extraction.prompt_template, 
        role_path="paper_reconstructions/nl2plan/prompts/task_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/task_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/task_extraction/task.txt")
    
    objects, initial, goal = task_extraction.task_extraction(
        model=model, 
        problem_desc=load_file(f"paper_reconstructions/nl2plan/domains/{domain}/{problem}.txt"), 
        task_extraction_prompt=task_extraction.prompt_template,
        types=type_hierarchy,
        predicates=predicates,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/feedback.txt"),
        error_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/error.txt")
        )
    
    log += f"{separator}\nSTEP FIVE: TASK EXTRACTION\n\n"
    log += f"OBJECTS:\n{objects}\n"
    log += f"INITIAL STATES:\n{initial}\n"
    log += f"GOAL STATES:\n{goal}\n"
    
    predicate_str = "\n".join(
        [pred["clean"].replace(":", " ; ") for pred in predicates]
    )
    
    types = format_types(type_hierarchy)  # retrieve types
    pruned_types = {
        name: description
        for name, description in types.items()
        if name not in UNSUPPORTED_KEYWORDS
    }  # remove unsupported words

    # format strings
    types_str = "\n".join(pruned_types)
    
    # generate PDDL specifications
    pddl_domain = domain_builder.generate_domain(
        domain=args.domain,
        requirements=args.requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions,
    )
    
    log += f"\n\nPDDL DOMAIN:\n{pddl_domain}"
    
    problem_name = args.domain + "_problem"
    pddl_problem = task_builder.generate_task(
        domain=args.domain,
        problem=problem_name,
        objects=objects,
        initial=initial,
        goal=goal,
    )
    
    log += f"\n\nPDDL PROBLEM:\n{pddl_problem}"
    
    # Ensure that the directories exist
    main_directory = f"paper_reconstructions/nl2plan/results/{domain}/{problem}"
    os.makedirs(main_directory, exist_ok=True)  # Creates the directory, if it doesn't exist

    # Write log file
    log_file = f"{main_directory}/log.txt"
    with open(log_file, "w") as f:
        f.write(log)

    # Write domain and problem files
    domain_file = f"{main_directory}/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
    problem_file = f"{main_directory}/problem.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    # Run planner
    _, plan = planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)

    # Write plan file
    plan_file = f"{main_directory}/plan.txt"
    with open(plan_file, "w") as f:
        f.write(plan)
    
    
    

if __name__ == "__main__":
    
    # # load in arguments to run program
    # parser = argparse.ArgumentParser(description="NL2Plan")
    # parser.add_argument('--model', type=str, default="gpt-4o-mini")
    # parser.add_argument('--domain', type=str, choices=DOMAINS, default="blocksworld")
    # parser.add_argument('--requirements', type=list[str], default=REQUIREMENTS)
    # parser.add_argument('--planner', type=str, default="/Users/marcustantakoun/Downloads/downward/fast-downward.py")
    # args = parser.parse_args()
    
    # # run LLM+P method
    # run_nl2plan(args=args, domain="blocksworld", problem="task2")

    planner = FastDownward(planner_path="/Users/marcustantakoun/Downloads/downward/fast-downward.py")
    domain_file = "paper_reconstructions/nl2plan/results/blocksworld/task2/domain.pddl"
    problem_file = "paper_reconstructions/nl2plan/results/blocksworld/task2/problem.pddl"

    # Run planner
    _, plan = planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)

    # Write plan file
    plan_file = "paper_reconstructions/nl2plan/results/blocksworld/task2/plan.txt"
    with open(plan_file, "w") as f:
        f.write(plan)