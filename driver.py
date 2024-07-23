from l2p.prompt_builder import PromptBuilder
from l2p.feedback_builder import Feedback_Builder
from l2p.domain_builder import Domain_Builder
from l2p.task_builder import Task_Builder
from l2p.llm_builder import LLM_Chat, get_llm
from l2p.utils.pddl_parser import prune_predicates, prune_types, extract_types
from l2p.utils.pddl_types import Action, Predicate
from l2p.utils.pddl_validator import Syntax_Validator
import os, json

# micro-functions
def format_json_output(data):
        return json.dumps(data, indent=4)

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

def run_granular_action_pipeline(
        model: LLM_Chat,
        domain_desc: str,
        param_prompt: PromptBuilder,
        precondition_prompt: PromptBuilder,
        effects_prompt: PromptBuilder,
        nl_actions: dict[str,str],
        feedback_builder: Feedback_Builder,
        feedback_template: str
        ):
    predicates = []
    max_iters = 2
    for iter in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():
            params, llm_response = domain_builder.extract_parameters(
                model=model,
                domain_desc=domain_desc,
                prompt_template=param_prompt.generate_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                types=domain_builder.get_type_hierarchy()
            )
            
            feedback_template = open_file('data/prompt_templates/action_construction/extract_params/feedback.txt')
            
            feedback_params, feedback_llm_response = feedback_builder.parameter_feedback(
                model=model, 
                domain_desc=domain_desc, 
                feedback_template=feedback_template, 
                feedback_type="llm",
                parameter=params,
                action_name=action_name,
                action_desc=action_desc,
                types=domain_builder.get_type_hierarchy(),
                llm_response=llm_response
                )
            
            if feedback_params != None:
                params=feedback_params

            preconditions, new_predicates, llm_response = domain_builder.extract_preconditions(
                model=model,
                domain_desc=domain_desc,
                prompt_template=precondition_prompt.generate_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                params=params,
                predicates=predicates
            )
            
            feedback_template = open_file('data/prompt_templates/action_construction/extract_preconditions/feedback.txt')
            
            feedback_preconditions, feedback_predicates, feedback_llm_response = feedback_builder.precondition_feedback(
                model=model, 
                domain_desc=domain_desc, 
                feedback_template=feedback_template, 
                feedback_type="llm",
                parameter=params,
                preconditions=preconditions,
                action_name=action_name,
                action_desc=action_desc,
                types=domain_builder.get_type_hierarchy(),
                predicates=new_predicates,
                llm_response=llm_response
                )
            
            if feedback_preconditions != None:
                preconditions=feedback_preconditions
                new_predicates=feedback_predicates
            
            predicates.extend(new_predicates)

            effects, new_predicates, llm_response = domain_builder.extract_effects(
                model=model,
                domain_desc=domain_desc,
                prompt_template=effects_prompt.generate_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                params=params,
                precondition=preconditions,
                predicates=predicates
            )
            
            feedback_template = open_file('data/prompt_templates/action_construction/extract_effects/feedback.txt')
            
            feedback_effects, feedback_predicates, feedback_llm_response = feedback_builder.effects_feedback(
                model=model, 
                domain_desc=domain_desc, 
                feedback_template=feedback_template, 
                feedback_type="llm",
                parameter=params,
                preconditions=preconditions,
                effects=effects,
                action_name=action_name,
                action_desc=action_desc,
                types=domain_builder.get_type_hierarchy(),
                predicates=new_predicates,
                llm_response=llm_response
                )
            
            if feedback_effects != None:
                effects=feedback_effects
                new_predicates=feedback_predicates
            
            predicates.extend(new_predicates)
            action = {"name": action_name, "parameters": params, "preconditions": preconditions, "effects": effects}
            actions.append(action)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    return actions, predicates

def run_compact_action_pipeline(model: LLM_Chat, domain_desc: str, domain_builder: Domain_Builder, prompt: PromptBuilder, nl_actions: dict[str,str], types: dict[str,str], feedback_builder: Feedback_Builder, feedback_template: str):
    # action-by-action method used in Guan et al. (2023): https://arxiv.org/abs/2305.14909
    # iterate through each action, dynamically create new predicates

    predicates = []
    max_iters = 2
    for _ in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():

            action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                model=model,
                prompt_template=prompt.generate_prompt(),
                action_name=action_name,
                action_desc=action_desc,
                predicates=predicates
            )

            # RUN FEEDBACK
            feedback_action, feedback_predicates, llm_feedback_response = feedback_builder.pddl_action_feedback(
                model=model, 
                domain_desc=domain_desc, 
                feedback_template=feedback_template, 
                feedback_type="llm",
                action=action, 
                predicates=predicates, 
                types=types, 
                llm_response=llm_response
                )
            
            if feedback_action != None:
                action=feedback_action
                new_predicates=feedback_predicates

            actions.append(action)
            predicates.extend(new_predicates)
            predicates = prune_predicates(predicates=predicates, actions=actions)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    return actions, predicates

def run_granular_task_pipeline(
        model: LLM_Chat,
        problem_desc: str,
        domain_desc: str,
        object_extraction_prompt: PromptBuilder,
        initial_extraction_prompt: PromptBuilder,
        goal_extraction_prompt: PromptBuilder,
        types: dict[str,str],
        predicates: list[Predicate],
        feedback_builder: Feedback_Builder,
        ) -> tuple[dict[str,str],str,str]:
    
    objects, llm_response = task_builder.extract_objects(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        prompt_template=object_extraction_prompt.generate_prompt(),
        type_hierarchy=types,
        predicates=predicates
        )
    
    
    feedback_template = open_file('data/prompt_templates/task_extraction/extract_objects/feedback.txt')
    
    feedback_objects, llm_feedback_response = feedback_builder.objects_feedback(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        feedback_template=feedback_template,
        feedback_type="llm",
        type_hierarchy=domain_builder.get_type_hierarchy(),
        predicates=predicates,
        objects=objects,
        llm_response=llm_response
    )
    
    if feedback_objects != None:
            objects=feedback_objects

    initial, llm_response = task_builder.extract_initial_state(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        prompt_template=initial_extraction_prompt.generate_prompt(),
        type_hierarchy=types,
        predicates=predicates,
        objects=objects
        )
    
    feedback_template = open_file('data/prompt_templates/task_extraction/extract_initial/feedback.txt')
    
    feedback_initial, llm_feedback_response = feedback_builder.initial_state_feedback(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        feedback_template=feedback_template,
        feedback_type="llm",
        type_hierarchy=domain_builder.get_type_hierarchy(),
        predicates=predicates,
        objects=objects,
        initial=initial,
        llm_response=llm_response
    )
    
    if feedback_initial != None:
            initial=feedback_initial

    goal, llm_response = task_builder.extract_goal_state(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        prompt_template=goal_extraction_prompt.generate_prompt(),
        type_hierarchy=types,
        predicates=predicates,
        objects=objects
        )
    
    feedback_template = open_file('data/prompt_templates/task_extraction/extract_goal/feedback.txt')
    
    feedback_goal, llm_feedback_response = feedback_builder.goal_state_feedback(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        feedback_template=feedback_template,
        feedback_type="llm",
        type_hierarchy=domain_builder.get_type_hierarchy(),
        predicates=predicates,
        objects=objects,
        initial=initial,
        goal=goal,
        llm_response=llm_response
    )
    
    if feedback_goal != None:
            goal=feedback_goal
    
    # objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
    
    return objects, initial, goal
    
def run_compact_task_pipeline(
        model: LLM_Chat,
        problem_desc: str, 
        domain_desc: str, 
        task_extraction_prompt: PromptBuilder, 
        types: dict[str,str], 
        predicates: list[Predicate],
        actions: list[Action],
        feedback_builder: Feedback_Builder,
        ) -> tuple[dict[str,str],str,str]:
    
    feedback_template = open_file('data/prompt_templates/task_extraction/extract_task/feedback.txt')

    objects, initial, goal, llm_response = task_builder.extract_task(
        model=model,
        problem_desc=problem_desc,
        domain_desc=domain_desc,
        prompt_template=task_extraction_prompt.generate_prompt(),
        types=types,
        predicates=predicates,
        actions=actions
        )
    
    for _ in range(2):
        feedback_objects, feedback_initial, feedback_goal, llm_feedback_response = feedback_builder.task_feedback(
            model=model, 
            problem_desc=problem_desc, 
            feedback_template=feedback_template,
            feedback_type="llm",
            predicates=predicates,
            types=types,
            objects=objects,
            initial=initial,
            goal=goal,
            llm_response=llm_response
            )
    
        if feedback_objects != None:
                objects=feedback_objects
                initial=feedback_initial
                goal=feedback_goal
        else:
            break

    return objects, initial, goal

def open_examples(examples_dir):
    example_files = [f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))]
    examples = [open_file(os.path.join(examples_dir, f)) for f in example_files]
    return examples

if __name__ == "__main__":

    # THIS IS IMPORTANT TO LOOK INTO
    unsupported_keywords = ['object', 'pddl']

    # model = get_llm("gpt-3.5-turbo-0125")
    # model = get_llm("gpt-4o")
    model = get_llm("gpt-4o-mini")

    # instantiate domain builder class
    domain_desc = open_file('data/domains/blocksworld.txt')
    domain_builder = Domain_Builder(types=None,type_hierarchy=None,predicates=None,nl_actions=None,pddl_actions=None)

    problem_list = []
    problem_list.append(open_file("data/problems/blocksworld_p1.txt"))
    # problem_list.append(open_file("data/problems/blocksworld_p2.txt"))
    # problem_list.append(open_file("data/problems/blocksworld_p3.txt"))

    task_builder = Task_Builder(objects=None, initial=None, goal=None)

    feedback_builder = Feedback_Builder()

    # open and create type extraction prompt builder class
    role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/type_extraction/examples/')
    task_desc = open_file('data/prompt_templates/type_extraction/task.txt')
    type_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create type hierarchy prompt builder class
    role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
    tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/hierarchy_construction/examples/')
    task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')
    type_hierarchy_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create NL action prompt builder class      
    role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
    tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_extraction/examples/')
    task_desc = open_file('data/prompt_templates/action_extraction/task.txt')
    nl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create PDDL action prompt builder class
    role_desc = open_file('data/prompt_templates/action_construction/extract_action/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/extract_action/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/extract_action/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/extract_action/task.txt')
    pddl_action_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/action_construction/extract_params/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/extract_params/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/extract_params/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/extract_params/task.txt')
    pddl_param_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/action_construction/extract_preconditions/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/extract_preconditions/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/extract_preconditions/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/extract_preconditions/task.txt')
    pddl_precondition_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/action_construction/extract_effects/role.txt')
    tech_desc = open_file('data/prompt_templates/action_construction/extract_effects/technique.txt')
    ex_desc = open_examples('data/prompt_templates/action_construction/extract_effects/examples/')
    task_desc = open_file('data/prompt_templates/action_construction/extract_effects/task.txt')
    pddl_effects_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/task_extraction/extract_objects/role.txt')
    tech_desc = open_file('data/prompt_templates/task_extraction/extract_objects/technique.txt')
    ex_desc = open_examples('data/prompt_templates/task_extraction/extract_objects/examples/')
    task_desc = open_file('data/prompt_templates/task_extraction/extract_objects/task.txt')
    object_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/task_extraction/extract_initial/role.txt')
    tech_desc = open_file('data/prompt_templates/task_extraction/extract_initial/technique.txt')
    ex_desc = open_examples('data/prompt_templates/task_extraction/extract_initial/examples/')
    task_desc = open_file('data/prompt_templates/task_extraction/extract_initial/task.txt')
    initial_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    role_desc = open_file('data/prompt_templates/task_extraction/extract_goal/role.txt')
    tech_desc = open_file('data/prompt_templates/task_extraction/extract_goal/technique.txt')
    ex_desc = open_examples('data/prompt_templates/task_extraction/extract_goal/examples/')
    task_desc = open_file('data/prompt_templates/task_extraction/extract_goal/task.txt')
    goal_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # open and create compact action prompt builder class
    role_desc = open_file('data/prompt_templates/task_extraction/extract_task/role.txt')
    tech_desc = open_file('data/prompt_templates/task_extraction/extract_task/technique.txt')
    ex_desc = open_examples('data/prompt_templates/task_extraction/extract_task/examples/')
    task_desc = open_file('data/prompt_templates/task_extraction/extract_task/task.txt')
    task_extraction_prompt = PromptBuilder(role_desc, tech_desc, ex_desc, task_desc)

    # extract types
    print("Extracted types output:\n")
    types, response = domain_builder.extract_type(model, domain_desc, type_extraction_prompt.generate_prompt())
    domain_builder.set_types(types=types)
    print("Types: ", format_json_output(domain_builder.get_types()))
    
    feedback_template = open_file('data/prompt_templates/type_extraction/feedback.txt')
    new_types, feedback_response = feedback_builder.type_feedback(model, domain_desc, feedback_template, types, response)
    # print("FEEDBACK:\n", feedback_response)
    print("\nNEW TYPES:\n", format_json_output(new_types))

    if new_types != None:
        print("CHANGED TYPES")
        domain_builder.set_types(types=new_types)
    
    # extract type hierarchy
    print("\n\n---------------------------------\n\nType hierarchy output:\n")
    type_hierarchy, response = domain_builder.extract_type_hierarchy(model, domain_desc, type_hierarchy_prompt.generate_prompt(), domain_builder.get_types())
    domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    print(format_json_output(type_hierarchy))

    feedback_template = open_file('data/prompt_templates/hierarchy_construction/feedback.txt')
    new_type_hierarchy, feedback_response = feedback_builder.type_hierarchy_feedback(model, domain_desc, feedback_template, type_hierarchy, response)
    print("\nFEEDBACK:\n", feedback_response)
    print("\nNEW TYPE HIERARCHY:\n", format_json_output(type_hierarchy))

    if new_type_hierarchy != None:
        print("CHANGED type hierarchy")
        domain_builder.set_type_hierarchy(new_type_hierarchy)

    # extract NL action descriptions
    print("\n\n---------------------------------\n\nNatural language action output:\n")
    nl_actions, response = domain_builder.extract_nl_actions(model, domain_desc, nl_action_extraction_prompt.generate_prompt(), domain_builder.get_type_hierarchy())
    domain_builder.set_nl_actions(nl_actions)
    for i in nl_actions: print(i)

    feedback_template = open_file('data/prompt_templates/action_extraction/feedback.txt')
    new_nl_actions, feedback_response = feedback_builder.nl_action_feedback(model, domain_desc, feedback_template, nl_actions, response)
    print("\nFEEDBACK:\n", feedback_response)
    print("\nNEW NL ACTIONS:\n", format_json_output(new_nl_actions))

    if new_nl_actions != None:
        print("CHANGED NL ACTION")
        domain_builder.set_nl_actions(new_nl_actions)
    
    # extract PDDL formatted actions
    print("\n\n---------------------------------\n\nPDDL action output:\n")

    # GRANULAR ACTION EXTRACTION PIPELINE
    
    feedback_template = ""
    
    actions, predicates = run_granular_action_pipeline(
        model=model, 
        domain_desc=domain_desc, 
        param_prompt=pddl_param_extraction_prompt,
        precondition_prompt=pddl_precondition_extraction_prompt,
        effects_prompt=pddl_effects_extraction_prompt,
        nl_actions=nl_actions,
        feedback_builder=feedback_builder,
        feedback_template=feedback_template
        )

    
    # COMPACT ACTION EXTRACTION PIPELINE
    # feedback_template = open_file('data/prompt_templates/action_construction/extract_action/feedback.txt')
    # actions, predicates = run_compact_action_pipeline(
    #     model=model, 
    #     domain_desc=domain_desc,
    #     domain_builder=domain_builder, 
    #     prompt=pddl_action_extraction_prompt,
    #     nl_actions=domain_builder.get_nl_actions(),
    #     types=domain_builder.get_type_hierarchy(),
    #     feedback_builder=feedback_builder,
    #     feedback_template=feedback_template
    # )

    predicates = prune_predicates(predicates=predicates, actions=actions) # discard predicates not found in action models + duplicates
    types = extract_types(type_hierarchy) # retrieve types
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions) # discard types not in predicates / actions + duplicates

    pruned_types = {name: description for name, description in pruned_types.items() if name not in unsupported_keywords} # remove unsupported words

    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    types_str = "\n".join(pruned_types)

    requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']
    print("[DOMAIN]\n") 
    pddl_domain = domain_builder.generate_domain(
        domain="test_domain", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )

    domain_file = "data/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
    print(f"PDDL domain written to {domain_file}")

    print("\n\n---------------------------------\n\nPDDL task extraction:\n")

    # feedback_template = open_file('data/prompt_templates/task_extraction/extract_task/feedback.txt')

    for i, problem in enumerate(problem_list, start=1):
        
        # GRANULAR TASK PIPELINE
        objects, initial_states, goal_states = run_granular_task_pipeline(
            model=model, 
            problem_desc=problem, 
            domain_desc=domain_desc, 
            object_extraction_prompt=object_extraction_prompt,
            initial_extraction_prompt=initial_extraction_prompt,
            goal_extraction_prompt=goal_extraction_prompt,
            types=pruned_types,
            predicates=predicates,
            feedback_builder=feedback_builder
        )
        
        # COMPACT TASK PIPELINE
        # objects, initial_states, goal_states = run_compact_task_pipeline(
        #     model=model, 
        #     problem_desc=problem, 
        #     domain_desc=domain_desc, 
        #     task_extraction_prompt=task_extraction_prompt,
        #     types=pruned_types,
        #     predicates=predicates,
        #     actions=actions,
        #     feedback_builder=feedback_builder,
        # )

        objects = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])

        print("[TASK]\n") 

        # Iteratively create new test domain names
        test_domain_name = f"test_domain"
        pddl_problem = task_builder.generate_task(domain=test_domain_name, objects=objects, initial=initial_states, goal=goal_states)
        print(pddl_problem)

        # Iteratively create new file names
        problem_file = f"data/problem_{i}.pddl"
        with open(problem_file, "w") as f:
            f.write(pddl_problem)
        print(f"PDDL problem written to {problem_file}")