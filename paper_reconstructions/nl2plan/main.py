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

DOMAINS = [
    "blocksworld",
    "household",
    "isr",
    "isr-assisted",
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

def run_nl2plan(args):
    # create necessary classes
    domain_builder = DomainBuilder() # L2P domain builder
    task_builder = TaskBuilder() # L2P task builder
    planner = FastDownward(planner_path=args.planner) # FastDownward planner
    
    # initialize OpenAI engine
    api_key = os.environ.get("OPENAI_API_KEY")
    model = OPENAI(model=args.model, api_key=api_key)
    
    
    # A. Type Extraction
    type_extraction = TypeExtraction()
    type_extraction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/type_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/type_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/type_extraction/task.txt")
    
    types = type_extraction.type_extraction(
        model=model, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        type_extraction_prompt=type_extraction.prompt_template,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/type_extraction/feedback.txt"))
    
    print("TYPES:\n", types)
    model.reset_tokens()
    
    # B. Hierarchy Construction
    hierarchy_construction = HierarchyConstruction()
    hierarchy_construction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/hierarchy_construction/task.txt")
    
    type_hierarchy = hierarchy_construction.hierarchy_construction(
        model=model, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        type_hierarchy_prompt=hierarchy_construction.prompt_template,
        types=types,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/hierarchy_construction/feedback.txt"))
    
    print("\n\nTYPE HIERARCHY:\n", type_hierarchy)
    model.reset_tokens()
    
    # C. Action Extraction
    action_extraction = ActionExtraction()
    action_extraction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/action_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_extraction/task.txt")
    
    nl_actions = action_extraction.action_extraction(
        model=model, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        action_extraction_prompt=action_extraction.prompt_template,
        type_hierarchy=type_hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_extraction/feedback.txt"))
    
    print("\n\nNL ACTIONS:\n", nl_actions)
    model.reset_tokens()
    
    # D. Action Construction
    action_construction = ActionConstruction()
    action_construction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/action_construction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/action_construction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/action_construction/task.txt")
    
    actions, predicates, = action_construction.action_construction(
        model=model, 
        domain_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/desc.txt"), 
        act_constr_prompt=action_construction.prompt_template,
        nl_actions=nl_actions,
        type_hierarchy=type_hierarchy,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/action_construction/feedback.txt"),
        max_attempts=1
        )
    
    print("\n\nACTIONS:")
    for i in actions:
        print(i)
    
    print("\n\nPREDICATES:")
    for i in predicates:
        print(i)
        
    model.reset_tokens()
    
    # E. Task Extraction
    task_extraction = TaskExtraction()
    task_extraction.set_prompt(
        role_path="paper_reconstructions/nl2plan/prompts/task_extraction/role.txt", 
        examples_path="paper_reconstructions/nl2plan/prompts/task_extraction/examples",
        task_path="paper_reconstructions/nl2plan/prompts/task_extraction/task.txt")
    
    objects, initial, goal = task_extraction.task_extraction(
        model=model, 
        problem_desc=load_file("paper_reconstructions/nl2plan/domains/blocksworld/task1.txt"), 
        task_extraction_prompt=task_extraction.prompt_template,
        types=type_hierarchy,
        predicates=predicates,
        feedback_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/feedback.txt"),
        error_prompt=load_file("paper_reconstructions/nl2plan/prompts/task_extraction/error.txt")
        )
    
    print("\n\nOBJECTS:\n", objects)
    print("\n\nINITIAL STATES:\n", initial)
    print("\n\nGOAL STATES:\n", goal)
    
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
    
    print("\n\nPDDL DOMAIN:\n", pddl_domain)
    
    problem_name = args.domain + "_problem"
    pddl_problem = task_builder.generate_task(
        domain=args.domain,
        problem=problem_name,
        objects=objects,
        initial=initial,
        goal=goal,
    )
    
    print("\n\nPDDL PROBLEM:\n", pddl_problem)

    # write files
    domain_file = "paper_reconstructions/nl2plan/results/blocksworld/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
    problem_file = "paper_reconstructions/nl2plan/results/blocksworld/problem.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    # run planner
    planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
    
    

if __name__ == "__main__":
    
    # load in arguments to run program
    parser = argparse.ArgumentParser(description="LLM+P")
    parser.add_argument('--model', type=str, default="gpt-4o-mini")
    parser.add_argument('--domain', type=str, choices=DOMAINS, default="blocksworld")
    parser.add_argument('--requirements', type=list[str], default=REQUIREMENTS)
    parser.add_argument('--planner', type=str, default="/Users/marcustantakoun/Downloads/downward/fast-downward.py")
    args = parser.parse_args()
    
    # run LLM+P method
    run_nl2plan(args=args)
