"""
Paper: "NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions" Gestrin et al (2024)
Source code: https://github.com/mrlab-ai/NL2Plan
Run: python3 -m paper_reconstructions.nl2plan.main
"""

import os, json
from l2p import *

def format_json_output(data):
    return json.dumps(data, indent=4)


engine = "gpt-4o-mini"
api_key = os.environ.get("OPENAI_API_KEY")
openai_llm = OPENAI(model=engine, api_key=api_key)

domain_desc = load_file("paper_reconstructions/nl2plan/prompts/blocksworld.txt")
problem_desc = load_file("paper_reconstructions/nl2plan/prompts/blocksworld_p1.txt")

# open and create type extraction prompt builder class
role_desc = load_file("paper_reconstructions/nl2plan/prompts/type_extraction/role.txt")
tech_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/type_extraction/technique.txt"
)
task_desc = load_file("paper_reconstructions/nl2plan/prompts/type_extraction/task.txt")
type_extraction_prompt = PromptBuilder(
    role=role_desc, technique=tech_desc, task=task_desc
)

# open and create type hierarchy prompt builder class
role_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/hierarchy_construction/role.txt"
)
tech_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/hierarchy_construction/technique.txt"
)
task_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/hierarchy_construction/task.txt"
)
type_hierarchy_prompt = PromptBuilder(
    role=role_desc, technique=tech_desc, task=task_desc
)

# open and create NL action prompt builder class
role_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_extraction/role.txt"
)
tech_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_extraction/technique.txt"
)
task_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_extraction/task.txt"
)
action_extraction_prompt = PromptBuilder(
    role=role_desc, technique=tech_desc, task=task_desc
)

# open and create PDDL action prompt builder class
role_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_construction/role.txt"
)
tech_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_construction/technique.txt"
)
task_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/action_construction/task.txt"
)
action_construction_prompt = PromptBuilder(
    role=role_desc, technique=tech_desc, task=task_desc
)

# open and create compact action prompt builder class
role_desc = load_file("paper_reconstructions/nl2plan/prompts/task_extraction/role.txt")
tech_desc = load_file(
    "paper_reconstructions/nl2plan/prompts/task_extraction/technique.txt"
)
task_desc = load_file("paper_reconstructions/nl2plan/prompts/task_extraction/task.txt")
task_extraction_prompt = PromptBuilder(
    role=role_desc, technique=tech_desc, task=task_desc
)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
syntax_validator = SyntaxValidator()
planner = FastDownward(planner_path="downward/fast-downward.py")
feedback_builder = FeedbackBuilder()

unsupported_keywords = ["object", "pddl", "lisp"]


def type_extraction(
    model: LLM, domain_desc: str, type_extraction_prompt: PromptBuilder
) -> dict[str, str]:
    # STEP ONE: type extraction
    types, response = domain_builder.extract_type(
        model, domain_desc, type_extraction_prompt.generate_prompt()
    )

    feedback_template = load_file(
        "paper_reconstructions/nl2plan/prompts/type_extraction/feedback.txt"
    )
    types, _ = feedback_builder.type_feedback(
        model=model,
        domain_desc=domain_desc,
        feedback_template=feedback_template,
        feedback_type="llm",
        types=types,
        llm_response=response,
    )
    
    return types


def hierarchy_construction(
    model, domain_desc, type_hierarchy_prompt, types
) -> dict[str, str]:
    # STEP TWO: type hierarchy extraction
    type_hierarchy, response = domain_builder.extract_type_hierarchy(
        model=model,
        domain_desc=domain_desc,
        prompt_template=type_hierarchy_prompt.generate_prompt(),
        types=types,
    )

    feedback_template = load_file(
        "paper_reconstructions/nl2plan/prompts/hierarchy_construction/feedback.txt"
    )
    type_hierarchy, _ = feedback_builder.type_hierarchy_feedback(
        model=model,
        domain_desc=domain_desc,
        feedback_template=feedback_template,
        feedback_type="llm",
        type_hierarchy=type_hierarchy,
        llm_response=response,
    )

    return type_hierarchy


def action_extraction(
    model, domain_desc, action_extraction_prompt, type_hierarchy
) -> dict[str, str]:
    # STEP THREE: action extraction
    nl_actions, response = domain_builder.extract_nl_actions(
        model=model,
        domain_desc=domain_desc,
        prompt_template=action_extraction_prompt.generate_prompt(),
        types=type_hierarchy,
    )

    feedback_template = load_file(
        "paper_reconstructions/nl2plan/prompts/action_extraction/feedback.txt"
    )
    nl_actions, _ = feedback_builder.nl_action_feedback(
        model=model,
        domain_desc=domain_desc,
        llm_response=response,
        feedback_template=feedback_template,
        feedback_type="llm",
        nl_actions=nl_actions,
        type_hierarchy=type_hierarchy,
    )

    return nl_actions


def action_construction(
    model, domain_desc, action_construction_prompt, nl_actions, type_hierarchy
) -> tuple[list[Action], list[Predicate]]:
    # STEP FOUR: action construction

    predicates = []
    max_iters = 2
    for _ in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():

            feedback_template = load_file(
                "paper_reconstructions/nl2plan/prompts/action_construction/feedback.txt"
            )

            # retrieve rest of list
            action_list = {
                a_name: a_desc
                for a_name, a_desc in nl_actions.items()
                if a_name != action_name
            }

            action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                model=model,
                domain_desc=domain_desc,
                prompt_template=action_construction_prompt.generate_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                action_list=action_list,
                predicates=predicates,
                types=type_hierarchy,
            )

            # perform syntax check on action model
            is_valid, feedback_msg = syntax_validator.validate_usage_predicates(
                llm_response, predicates, type_hierarchy
            )
            # if there is syntax error, run through feedback mechanism to retrieve new action model
            if is_valid == False:
                feedback_template += (
                    "\n\nThe following is a syntax error with your response:\n"
                    + feedback_msg
                )
                
            # TODO: currently buggy - run feedback at the end of the pipline

            # RUN FEEDBACK
            # action, new_predicates, _ = feedback_builder.pddl_action_feedback(
            #     model=model,
            #     domain_desc=domain_desc,
            #     llm_response=llm_response,
            #     feedback_template=feedback_template,
            #     feedback_type="llm",
            #     action=action,
            #     predicates=predicates,
            #     types=types,
            # )

            actions.append(action)
            predicates.extend(new_predicates)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    # discard predicates not found in action models + duplicates
    predicates = prune_predicates(predicates=predicates, actions=actions)

    return actions, predicates


def task_extraction(
    model, problem_desc, task_extraction_prompt, types, predicates, actions
) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]]]:
    # STEP FIVE: task extraction
    feedback_template = load_file(
        "paper_reconstructions/nl2plan/prompts/task_extraction/feedback.txt"
    )

    objects, initial, goal, llm_response = task_builder.extract_task(
        model=model,
        problem_desc=problem_desc,
        prompt_template=task_extraction_prompt.generate_prompt(),
        types=types,
        predicates=predicates,
        actions=actions,
    )

    feedback_msgs = []
    all_valid = True

    # List of validation checks
    validation_checks = [
        (syntax_validator.validate_task_objects, (objects, types)),
        (
            syntax_validator.validate_task_states,
            (initial, objects, predicates, "initial"),
        ),
        (syntax_validator.validate_task_states, (goal, objects, predicates, "goal")),
    ]

    # Perform each validation check
    for validator, args in validation_checks:
        is_valid, feedback_msg = validator(*args)
        if not is_valid:
            all_valid = False
            feedback_msgs.append(feedback_msg)

    # If any check fails, append feedback messages
    if not all_valid:
        feedback_template += (
            "\n\nThe following is a syntax error with your response:"
            + "\n".join(feedback_msgs)
        )

    objects, initial, goal, _ = feedback_builder.task_feedback(
        model=model,
        problem_desc=problem_desc,
        llm_response=llm_response,
        feedback_template=feedback_template,
        feedback_type="llm",
        predicates=predicates,
        types=types,
        objects=objects,
        initial=initial,
        goal=goal,
    )

    objects = task_builder.format_objects(objects)
    initial = task_builder.format_initial(initial)
    goal = task_builder.format_goal(goal)

    return objects, initial, goal


if __name__ == "__main__":

    # STEP ONE: type extraction
    types = type_extraction(openai_llm, domain_desc, type_extraction_prompt)

    print("Types:", format_json_output(types))
    print("END OF STEP ONE")

    # STEP TWO: hierarchy construction
    type_hierarchy = hierarchy_construction(
        openai_llm, domain_desc, type_hierarchy_prompt, types
    )

    print("Type Hierarchy", format_json_output(type_hierarchy))
    print("END OF STEP TWO")

    # STEP THREE: action extraction
    nl_actions = action_extraction(
        openai_llm, domain_desc, action_extraction_prompt, type_hierarchy
    )

    print("Natural Language Actions")
    for i in nl_actions:
        print(i)
    print("END OF STEP THREE")

    # STEP FOUR: action construction
    actions, predicates = action_construction(
        openai_llm, domain_desc, action_construction_prompt, nl_actions, type_hierarchy
    )

    print("PDDL Actions")
    for i in actions:
        print(i)
    print("--------------------")
    print("PDDL Predicates")
    for i in predicates:
        print(i)
    print("END OF STEP FOUR")

    types = format_types(type_hierarchy)  # retrieve types
    types = prune_types(
        types=types, predicates=predicates, actions=actions
    )  # discard types not in predicates / actions + duplicates
    types = {
        name: description
        for name, description in types.items()
        if name not in unsupported_keywords
    }  # remove unsupported words

    # STEP FIVE: task extraction
    objects, initial, goal = task_extraction(
        openai_llm, problem_desc, task_extraction_prompt, types, predicates, actions
    )

    print("Objects:\n", objects)
    print("Initial States:\n", initial)
    print("Goal States:\n", goal)
    print("END OF STEP FIVE")

    # format strings
    predicate_str = "\n".join(
        [pred["clean"].replace(":", " ; ") for pred in predicates]
    )
    types_str = "\n".join(types)

    requirements = [
        ":strips",
        ":typing",
        ":equality",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":universal-preconditions",
        ":conditional-effects",
    ]

    # generate PDDL specifications
    pddl_domain = domain_builder.generate_domain(
        domain="test_domain",
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions,
    )
    pddl_problem = task_builder.generate_task(
        domain="test_domain",
        problem="test_problem",
        objects=objects,
        initial=initial,
        goal=goal,
    )

    # write files
    domain_file = "paper_reconstructions/nl2plan/results/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
    problem_file = "paper_reconstructions/nl2plan/results/problem.pddl"
    with open(problem_file, "w") as f:
        f.write(pddl_problem)

    # run planner
    planner.run_fast_downward(domain_file=domain_file, problem_file=problem_file)
