"""
Paper: "Leveraging Environment Interaction for Automated PDDL Generation and Planning with Large Language Models" Mahdavi et al (2024)
Source code: N/A
Run: python3 -m tests.paper_reconstructions.llm+ew.llm+ew

Focus: using LLMs and environmental feedback to auto-generate both PDDL domain+problem files w/o human intervention
    - Problem of limited feedback from PDDL plan failures
    - Addresses how brittle PDDL domain are; omitting minor rules lead to cascading plan failures

Assumes the following:
    1. NL domain description
    2. NL task description
    3. Object list from ground-truth task: label recognitiion purposes
    4. Action interface (names and parameters) from ground-truth domain: assumes conduction of API calls
    
Algorithm:
    1. LLM to generate problem PDDL candidates
    2. For each problem candidate:
        - Keep history 'h(i)' of conversation (PDDL problem, NL domain description)
        - Initialize domain empty template as best: 'd(i)'
        
        For however many cycles 'c':
            - LLM to generate domain PDDL candidates 'd(i,1), d(i,2), ... ' given 'h(i)'
            - Calculate (argmax) current best domain PDDL candidate 'd(c)' - evaluate LLM responses using EW
            - Obtain NL feedback from EW on given list of objects and action interface: f(c)
            - Update history with "d(c)" and "f(c)"
            - Update best domain candidate (argmax) between current and overall candidate using EW
            
    3. Obtain (argmax) best pair '(d,p)' of domain candidate corresponding with respective problem candidate using EW
    4. Return 'd, p'
    
Algorithm GenerateDomainAndProblemPDDL

Input: 
  d_NL: Natural language description of the environment domain
  p_NL: Natural language description of the problem
  environment_action_interface: Interface for actions in the environment
  n_p: Number of problem PDDL candidates to generate
  c_max: Maximum number of iterations for domain refinement

Output:
  d_final: Final refined domain PDDL
  p_final: Final refined problem PDDL

Procedure:
1. Initialize problem PDDL candidates:
   p_candidates = LLM_np(p_NL)

2. For each problem candidate i from 1 to n_p:
   2.1. Initialize conversation history h_i with p_candidates[i] and d_NL
   
   2.2. Initialize an empty domain template:
        d_i_template = InitializeEmptyTemplate(d_NL)
   
   2.3. For each refinement cycle c from 1 to c_max:
        2.3.1. Generate domain candidates using LLM:
               d_i_candidates = LLM_nd(h_i)
        
        2.3.2. Select the best domain candidate based on EW score:
               d_best = argmax_{d in d_i_candidates} EWScore(d, p_candidates[i])
        
        2.3.3. Get natural language feedback for the selected domain:
               feedback_c = GetFeedbackFromEW(d_best, d_i_template, p_candidates[i])
        
        2.3.4. Update conversation history with feedback:
               h_i = UpdateHistory(h_i, feedback_c)
   
   2.4. Store the best domain candidate for this problem:
        d_i_best = d_best

3. Select the final refined domain and problem PDDLs:
   d_final, p_final = argmax_{d_i_best, p_candidates[i] | i=1 to n_p} EWScore(d_i_best, p_candidates[i])

4. Return the final refined domain and problem PDDLs:
   return d_final, p_final
   
Algorithm ExplorationWalk(EW)

Input:
  d: Domain description (PDDL)
  p: Problem description (PDDL)
  T_max: Maximum length of the exploration walk
  A: Set of actions in the domain
  E: Executability checker function (E(d, p, q) returns true if action sequence q is executable in d and p)

Output:
  EW_score: Exploration Walk score

Procedure:
1. Initialize EW_score = 0

2. For each problem instance p_i in p:
   2.1. Initialize total_walks = 0
   2.2. Initialize executable_walks = 0

   2.3. For each walk length T from 1 to T_max:
        2.3.1. Generate all possible action sequences q of length T from action set A
        2.3.2. For each action sequence q:
               2.3.2.1. If E(d, p_i, q) is true:
                        - executable_walks += 1
               2.3.2.2. Increment total_walks

   2.4. Compute executability ratio for problem p_i:
        executability_ratio_i = executable_walks / total_walks

   2.5. Accumulate executability ratio to EW_score:
        EW_score += executability_ratio_i

3. Normalize EW_score by the number of problem instances:
   EW_score = EW_score / |p|

4. Return EW_score
"""

import os, itertools
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.prompt_builder import PromptBuilder
from l2p.utils.pddl_parser import prune_predicates, prune_types, extract_types
from l2p.utils.pddl_VAL import parse_pddl

# engine = "gpt-4o-mini"
engine = "gpt-3.5-turbo-0125"
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
model = GPT_Chat(client=client, engine=engine)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()

domain_template = \
"""
(define (domain gripper -strips)
    (:requirements :strips :typing)
    (:types room obj robot gripper)
    (:predicates)
    
    (:action move
        :parameters (?r - robot ?from ?to - room)
        :precondition ()
        :effect ())
        
    (:action pick
        :parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        :precondition ()
        :effect ())
        
    (:action drop
        :parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        :precondition ()
        :effect ())
)
"""

problem_template = \
"""
(define (problem gripper -2-3-4)
    (:domain gripper -strips)
    (:objects lgripper1 lgripper2 rgripper1 rgripper2 - gripper 
        ball1 ball2 ball3 ball4 - obj robot1 robot2 - robot 
        room1 room2 room3 - room)
    (:init )
    (:goal (and )) 
)
"""

grippers_domain_example = \
"""
(define 
    (domain gripper -strips)
    (:requirements :strips :typing)
    (:types room obj robot gripper)
    (:predicates (at-robby ?r - robot ?x - room)
        (at ?o - obj ?x - room)
        (free ?r - robot ?g - gripper)
        (carry ?r - robot ?o - obj ?g - gripper))
        
    (:action move
        :parameters (?r - robot ?from ?to - room)
        :precondition (and (at-robby ?r ?from))
        :effect (and (at-robby ?r ?to)
            (not (at-robby ?r ?from))))
            
    (:action pick
        :parameters (?r - robot ?obj - obj ?room - room ?g - gripper)
        :precondition (and (at ?obj ?room ) ( at - robby ?r ?room ) (free ?r ?g))
        :effect (and (carry ?r ?obj ?g ) (not (at ?obj ?room )) (not (free ?r ?g))))
        
    (:action drop
        :parameters (?r - robot ?obj - obj ?room - room ?g - gripper)
        :precondition (and (carry ?r ?obj ?g) (at-robby ?r ?room))
        :effect (and (at ?obj ?room) (free ?r ?g) (not (carry ?r ?obj ?g))))
)
"""

grippers_problem_example = \
"""
(define (problem gripper -2-3-4)
    (:domain gripper -strips)
    (:objects robot1 robot2 - robot
        rgripper1 lgripper1 rgripper2 lgripper2 - gripper
        room1 room2 room3 - room
        ball1 ball2 ball3 ball4 - obj)
        
    (:init 
        (at-robby robot1 room2)
        (free robot1 rgripper1)
        (free robot1 lgripper1)
        (at-robby robot2 room3)
        (free robot2 rgripper2)
        (free robot2 lgripper2)
        (at ball1 room3)
        (at ball2 room1)
        (at ball3 room1)
        (at ball4 room3)
    )    
    
    (:goal 
        (and
            (at ball1 room2)
            (at ball2 room2)
            (at ball3 room3)
            (at ball4 room3)
        )
    )
)
"""

grippers_domain_nl = \
"""
The gripper domain involves a world with multiple rooms, robots, and objects (balls). Each robot has two grippers that can be used to pick up and drop objects. The goal is to move objects from their initial locations to the desired goal locations using the robots and their grippers.

The domain includes three actions:
    1. move: This action allows a robot to move from one room to another. The precondition is that the robot must be in the starting room. The effect is that the robot is no longer in the starting room and is now in the destination room.
    2. pick: This action allows a robot to pick up an object using one of its grippers. The preconditions are that the object and the robot must be in the same room , and the specified gripper must be free (not holding any object). The effect is that the robot is now carrying the object with the specified gripper , the object is no longer in the room , and the gripper is no longer free.
    3. drop: This action allows a robot to drop an object it is carrying in a specific room using one of its grippers. The preconditions are that the robot must be carrying the object with the specified gripper and the robot must be in the specified room. The effect is that the object is now in the room , the gripper is free , and the robot is no longer carrying the object with that gripper.
"""

grippers_problem_nl = \
"""
You control two robots, each equipped with a left and right gripper, capable of moving objects (balls) between different rooms.

Initially:
    - Robot1 is in room2 and both its grippers (rgripper1 and lgripper1) are free.
    - Robot2 is in room3 and both its grippers (rgripper2 and lgripper2) are free.
    - Ball1 and Ball4 are in room3.
    - Ball2 and Ball3 are in room1. 
    
Your goal is to achieve the following configuration:
    - Ball1 must be moved to room2.
    - Ball2 must be moved to room2.
    - Ball3 must remain in room3.
    - Ball4 must remain in room3.
"""

grippers_problem_plan_example = \
"""
(move robot2 room3 room1)
(pick robot2 ball2 room1 lgripper2)
(move robot2 room1 room2)
(drop robot2 ball2 room2 lgripper2)
(move robot1 room2 room1)
(pick robot1 ball3 room1 lgripper1)
(move robot1 room1 room3)
(pick robot1 ball1 room3 rgripper1)
(drop robot1 ball3 room3 lgripper1)
(move robot1 room3 room2)
(drop robot1 ball1 room2 rgripper1)
"""

unsupported_keywords = ['object', 'pddl', 'lisp']

def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

# open and create type extraction prompt builder class
role_desc = open_file('data/prompt_templates/type_extraction/role.txt')
tech_desc = open_file('data/prompt_templates/type_extraction/technique.txt')
task_desc = open_file('data/prompt_templates/type_extraction/task.txt')
type_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create type hierarchy prompt builder class
role_desc = open_file('data/prompt_templates/hierarchy_construction/role.txt')
tech_desc = open_file('data/prompt_templates/hierarchy_construction/technique.txt')
task_desc = open_file('data/prompt_templates/hierarchy_construction/task.txt')
type_hierarchy_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create NL action prompt builder class      
role_desc = open_file('data/prompt_templates/action_extraction/role.txt')
tech_desc = open_file('data/prompt_templates/action_extraction/technique.txt')
task_desc = open_file('data/prompt_templates/action_extraction/task.txt')
nl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create PDDL action prompt builder class
role_desc = open_file('data/prompt_templates/action_construction/extract_action/role.txt')
tech_desc = open_file('data/prompt_templates/action_construction/extract_action/technique.txt')
task_desc = open_file('data/prompt_templates/action_construction/extract_action/task.txt')
pddl_action_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

# open and create compact action prompt builder class
role_desc = open_file('data/prompt_templates/task_extraction/extract_task/role.txt')
tech_desc = open_file('data/prompt_templates/task_extraction/extract_task/technique.txt')
task_desc = open_file('data/prompt_templates/task_extraction/extract_task/task.txt')
task_extraction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)


def generate_pddl_domain_candidate(model, history) -> str:
    
    PDDL_problem = "\n\nHere is a PDDL task file that should correspond to your answer:\n" + history[0] + "\n\n"
    domain_desc = history[1]
    
    types, response = domain_builder.extract_type(model, domain_desc, type_extraction_prompt.generate_prompt() + PDDL_problem)
    domain_builder.set_types(types)
    
    type_hierarchy, response = domain_builder.extract_type_hierarchy(model, domain_desc, type_hierarchy_prompt.generate_prompt() + PDDL_problem, domain_builder.get_types())
    domain_builder.set_type_hierarchy(type_hierarchy)
    
    nl_actions, response = domain_builder.extract_nl_actions(model, domain_desc, nl_action_extraction_prompt.generate_prompt() + PDDL_problem, domain_builder.get_type_hierarchy())
    domain_builder.set_nl_actions(nl_actions)
    
    predicates = []
    max_iters = 1
    for _ in range(max_iters):

        actions = []
        current_preds = len(predicates)

        for action_name, action_desc in nl_actions.items():
            action, new_predicates, llm_response = domain_builder.extract_pddl_action(
                model,
                pddl_action_extraction_prompt.generate_prompt() + PDDL_problem,
                action_name,
                action_desc,
                predicates
            )

            actions.append(action)
            predicates.extend(new_predicates)

        if len(predicates) == current_preds:
            print("No new predicates created. Stopping action construction.")
            break

    predicates = prune_predicates(predicates=predicates, actions=actions) # discard predicates not found in action models + duplicates
    types = extract_types(type_hierarchy) # retrieve types
    pruned_types = prune_types(types=types, predicates=predicates, actions=actions) # discard types not in predicates / actions + duplicates
    pruned_types = {name: description for name, description in pruned_types.items() if name not in unsupported_keywords} # remove unsupported words
    predicate_str = "\n".join([pred["clean"].replace(":", " ; ") for pred in predicates])
    types_str = "\n".join(pruned_types)

    requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

    pddl_domain = domain_builder.generate_domain(
        domain="test_domain", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )
    
    print(pddl_domain)
    
    return pddl_domain
    
    
def generate_pddl_task_candidate(model, prompt_template) -> str:
    
    prompt_template += \
        """
        Your task is to extract the initial state and the goal state for a PDDL problem based on a domain description and the available predicates. Consider that if a predicate is checked by an action for an object, it should probably somehow be possible to make true or start true. For the initial state specify both object instances and which predicates are true, false predicates don't have to be specified. For the goal, specify the states which need to have specific values regardless if those are true or false. Do it step-by-step and explain your thoughts. Respond with the exact headings provided. You can't assume that any object, regardless of type, already exists. Everything you wish to use should be defined here. Also, remember that any symmetrical predicates likely should be defined both ways. Even if there is one goal state, it must contain the PDDL 'AND' syntax

The problem you are to extract from is under the header '## Problem description'

Also it is crucial you follow these checks: 
    - objects types should be found in types list
    - objects name should not be the same as a type name
    - object name should not be the same as a predicate name
    - objects should have meaningful names
    - objects should only be appointed by its respective type

Do not, under any circumstance, output the answers in PDDL format. Final answer must be in the following format at the end:
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
```
        """
    
    objects, initial, goal, llm_response = task_builder.extract_task(model=model, prompt_template=prompt_template)
    objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
    pddl_problem = task_builder.generate_task("gripper_domain", objects_str, initial, goal)
    
    return pddl_problem


# def exploration_walk(d: str, p: str, T_max: int, model) -> float:
#     # Generate all possible action sequences of lengths up to T_max
#     all_sequences = generate_all_action_sequences(d, T_max)
#     executable_sequences = 0
#     total_sequences = len(all_sequences)
    
#     for seq in all_sequences:
#         if validate_sequence(d, p, seq, model):
#             executable_sequences += 1
            
#     return executable_sequences / total_sequences if total_sequences > 0 else 0


# def generate_all_action_sequences(d: str, T_max: int) -> list[str]:
#     # For simplicity, assume we have a way to get the actions from the domain
#     actions = # pddl_parser.extract_actions(d)
#     all_sequences = []
    
#     # Generate all possible action sequences of lengths 1 to T_max
#     for t in range(1, T_max + 1):
#         sequences = list(itertools.product(actions, repeat=t))
#         all_sequences.extend(sequences)
    
#     return all_sequences


# def validate_sequence(d: str, p: str, seq: list[str], model) -> bool:
#     # Placeholder for validating a sequence of actions in a given PDDL domain and problem
#     # Assume we have an executability checker using the model
#     problem_file = "temp_problem.pddl"
#     with open(problem_file, "w") as f:
#         f.write(p)
    
#     # Validate the domain and problem using VAL parser
#     try:
#         output = parse_pddl("VAL/build/macos64/Release/bin/Parser", domain_file=d, problem_file=problem_file)
#         return output is None  # No errors mean the sequence is executable
#     except Exception as e:
#         print(f"Validation error: {e}")
#         return False


def select_final_domain_and_problem(best_domains: list[str], p_candidates: list[Tuple[str, str, str, str]]) -> tuple[str, str]:
    # Placeholder for selecting the best final domain and problem based on some criteria
    # Here, we might choose the one with the highest EW score or any other metric
    best_d = best_domains[0]
    best_p = p_candidates[0]
    return best_d, best_p

if __name__ == "__main__":
    domain_nl = grippers_domain_nl
    problem_nl = grippers_problem_nl

    T_max = 10
    c_max = 1
    n_p = 1
    n_d = 1
    
    # step 1: generate initial PDDL problem candidates
    p_candidates = [generate_pddl_task_candidate(model, problem_nl) for _ in range(n_p)]
    
    best_domains = []
    
    for i in range(n_p):
        
        history = [p_candidates[i], domain_nl]
        best_domain = domain_template
        
        for c in range(c_max):
            # generate PDDL domain candidates
            d_candidates = [generate_pddl_domain_candidate(model, history) for _ in range(n_d)]
            
            # calculate EW for each domain candidate
            # scores = [exploration_walk(d, p_candidates[i], T_max, model) for d in d_candidates]
            
            # DONT KNOW HOW TO IMPLEMENT EXPLORATION WALK - WILL NEED TO REVISIT
            scores = ""
            
            # select current best domain candidate for specific corresponding problem candidate
            best_d_index = scores.index(max(scores))
            best_domain = d_candidates[best_d_index]
            
            feedback = ""
            
            history.append((best_domain, feedback))
            
        best_domains.append(best_domain)
        
    d_final, p_final = select_final_domain_and_problem(best_domains, p_candidates)
    
    print("Final Domain:")
    print(d_final)
    print("Final Problem:")
    print(p_final)



