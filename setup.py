"""
Activate virtual environment: source env/bin/activate

L2P Checklist

- [ ] Integrate action-construction architecture into work
    - [ ] Implement add_predicates
- [ ] Distribute each component into its separate class, let domain_builder be the coordinating class
- [ ] Implement auto-feedback checklist
- [ ] Implement LLM-generated feedback checklist
- [ ] Implement PDDL generator — parser to assemble everything together

- The action_construction pipeline consists of:
    - Action extraction loop
        - For each action description, construct singular action (parameter, precondition, effects) based on current predicts and put into a list
        - Update list of new predicates 
        - Prune unused predicates and types
    - Once all actions generated, add actions (iteratively) and predicates to PDDLGenerator

PDDLGenerator is essentially domain_builder / task_builder — CHANGE THINGS AROUND TO PERFORM SAME FUNCTION

- [ ] Implement add_type — run through 
- [ ] Implement add_action — run through whole pipeline

- [ ] Implement task_builder
    - [ ] extract_object
    - [ ] extract_initial_state
    - [ ] extract_goal_state
    - [ ] Implement get functions
    - [ ] Implement add functions — pipelines

- [ ] Implement external planner tool
# I would like to add the new types "country" and "continent"s

"""

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements

# # set up variables and constants
# x, y, z = variables("x y z", types=["type_1"])
# a, b, c = constants("a b c", type_="type_1")

# # define predicates
# p1 = Predicate("p1", x, y, z)
# p2 = Predicate("p2", x, y)

# # define actions
# a1 = Action(
#     "action-1",
#     parameters=[x, y, z],
#     precondition=p1(x, y, z) & ~p2(y, z),
#     effect=p2(y, z)
# )

# # define the domain object.
# requirements = [Requirements.STRIPS, Requirements.TYPING]
# domain = Domain("my_domain",
#                 requirements=requirements,
#                 types={"type_1": None},
#                 constants=[a, b, c],
#                 predicates=[p1, p2],
#                 actions=[a1])

# print(domain_to_string(domain))

# """
# (define (domain my_domain)
#     (:requirements :strips :typing)
#     (:types type_1)
#     (:constants a b c - type_1)
#     (:predicates (p1 ?x - type_1 ?y - type_1 ?z - type_1)  (p2 ?x - type_1 ?y - type_1))
#     (:action action-1
#         :parameters (?x - type_1 ?y - type_1 ?z - type_1)
#         :precondition (and (p1 ?x ?y ?z) (not (p2 ?y ?z)))
#         :effect (p2 ?y ?z)
#     )
# )
# """

# problem = Problem(
#     "problem-1",
#     domain=domain,
#     requirements=requirements,
#     objects=[a, b, c],
#     init=[p1(a, b, c), ~p2(b, c)],
#     goal=p2(b, c)
# )
# print(problem_to_string(problem))

# """
# (define (problem problem-1)
#     (:domain my_domain)
#     (:requirements :strips :typing)
#     (:objects a b c - type_1)
#     (:init (not (p2 b c)) (p1 a b c))
#     (:goal (p2 b c))
# )
# """

# def parse_predicate(predicate_str):
#     # Remove "PREDICATES: " prefix, parentheses and split the string
#     predicate_str = predicate_str.strip(' ()')
#     parts = predicate_str.split()
    
#     # Extract predicate name
#     predicate_name = parts[0]
    
#     # Extract variables and their types
#     variables_list = []
#     types = []
    
#     i = 1
#     while i < len(parts):
#         var = parts[i].replace('?', '')  # Remove question mark
#         type_ = parts[i + 2]  # Get the type from the next index + 2
#         variables_list.append(var)
#         types.append(type_)
#         i += 3  # Move to the next variable
    
#     # Create variables using the PDDL library
#     var_objects = variables(' '.join(variables_list), types=types)
    
#     # Create the predicate
#     predicate = Predicate(predicate_name, *var_objects)
    
#     return predicate

# # Example usage
# predicate_strs = [
#     "(on_table ?b - block)",
#     "(holding ?robot_arm - object ?block - object)",
#     "(on ?b1 - block ?b2 - block)"
# ]

# for predicate_str in predicate_strs:
#     predicate = parse_predicate(predicate_str)
#     # print(predicate)

from typing import List, Dict, TypedDict
from pddl.logic import Predicate, constants, variables
from pddl.core import Domain
from pddl.action import Action
from pddl.formatter import domain_to_string
from pddl.requirements import Requirements

# Define the ActionList structure
class ActionList(TypedDict):
    name: str
    desc: str
    raw: str
    parameters: List[Dict[str, str]]
    preconditions: str
    effects: str

def parse_predicate(predicate: str) -> tuple[Predicate, list[str], list[variables]]:

    parts = predicate.replace('(', '').replace(')', '').split()
    name = parts[0]
    var_names = []
    var_types_extracted = []
    
    # Extract variable names and types
    for i in range(1, len(parts), 3):
        if i+1 < len(parts) and parts[i+1] == '-':
            var_name = parts[i].strip('?')
            var_type = parts[i+2]
            var_names.append(var_name)
            var_types_extracted.append(var_type)
    
    # Debugging information
    print(f"Parsing predicate: {predicate}")
    print(f"Extracted variable names and types: {list(zip(var_names, var_types_extracted))}")

    vars = []
    for var_name, var_type in zip(var_names, var_types_extracted):

        # print(f"Var name: {var_name}")
        # print(f"Var type: {var_type}")

        vars.append(variables(var_name, types=[var_type])[0])

    return Predicate(name, *vars), name, vars



def parse_action(action: ActionList, predicates: list[Predicate]=None) -> Action:
    name = action['name']

    params = []
    for param in action['parameters']:
        params.append(variables(param['name'].strip('?'), types=[param['type']])[0])
    
    # Debugging information
    print(f"Parsing action: {name}")
    print(f"Parameters: {params}")

    for p in predicates:
        print(p.name)
        # match predicate name with predicate found within action precondition/effect
        # if cases of and/not/or statements



def generate_pddl_code(types: List[str], predicates: List[str], actions: List[ActionList], constants_list: List[Dict[str, str]] = None) -> str:

    pred_list = []
    name_list = []
    var_list = []

    for p in predicates:
        parsed_predicate, name, vars = parse_predicate(p)

        pred_list.append(parsed_predicate)
        name_list.append(name)
        var_list.append(vars)
        
    print("")
    print(f"Parsed predicate: {pred_list}")
    print(f"Named predicate: {name_list}")
    print(f"Variables: {var_list}")

    action_list = []

    for a in actions:
        action = parse_action(a, pred_list)
        action_list.append(action)


    # Define domain
    requirements = [Requirements.STRIPS, Requirements.TYPING]
    types_dict = {t: None for t in types}

    domain = Domain("my_domain",
                    requirements=requirements,
                    types=types_dict,
                    predicates=pred_list,
                    actions=action_list
                    )

    return domain_to_string(domain)

    # Define constants dynamically
    # const_objects = [constants(c['name'], type_=c['type'])[0] for c in constants_list]



# # Example usage
# types = ['object', 'block', 'location', 'table', 'robot_arm']

# predicates = [
#     '(at ?o - object ?l - location)',
#     '(holding ?robot_arm - object ?block - object)',
#     '(on_table ?b - block)',
#     '(on ?b1 - block ?b2 - block)'
# ]

# actions = [
#     {
#         "name": "move",
#         "desc": "Move an object from one location to another",
#         "raw": "",
#         "parameters": [
#             {"name": "?r", "type": "object"},
#             {"name": "?loc", "type": "location"},
#             {"name": "?prev_loc", "type": "location"}
#         ],
#         "preconditions": "(and (not (at ?r ?loc)) (on_table ?loc))",
#         "effects": "(and (not (at ?r ?prev_loc)) (at ?r ?loc))"
#     }
# ]

# """
# ~(at ?r ?loc) & (on_table ?loc)

# (and
#     (not (at ?r ?loc)) ; The robot arm is not already at the location
#     (valid_location ?loc) ; The location is a valid location for the robot arm to move to
# )
# (and
#     (not (at ?r ?prev_loc)) ; The robot arm is no longer at its previous location
#     (at ?r ?loc) ; The robot arm is now at the specified location
# )
# """

# constants_list = [
#     {"name": "a", "type": "object"},
#     {"name": "d", "type": "block"},
#     {"name": "c", "type": "location"}
# ]

# pddl_code = generate_pddl_code(types, predicates, actions)
# print(pddl_code)

def extract_types(type_hierarchy):
    def process_node(node, parent_type=None):
        current_type = list(node.keys())[0]
        description = node[current_type]
        parent_type = parent_type if parent_type else current_type
        formatted_str = f"{current_type} - {parent_type} ; {description}" if current_type != parent_type else f"{current_type} ; {description}"
        
        result.append(formatted_str)
        for child in node.get("children", []):
            process_node(child, current_type)

    result = []
    process_node(type_hierarchy)
    return result

type_hierarchy = {
    "object": "Object is always root, everything is an object",
    "children": [
        {
            "block": "Objects that can be picked up and placed on the table or on top of another block.",
            "children": []
        },
        {
            "table": "A surface where blocks can be placed.",
            "children": []
        },
        {
            "robot_arm": "The mechanical arm that can pick up and place blocks.",
            "children": []
        },
        {
            "location": "General type for organizing the space where the blocks are placed.",
            "children": []
        }
    ]
}

converted_list = extract_types(type_hierarchy)
print(converted_list)

"""
{
    "object": "Object is always root, everything is an object",
    "children": [
        {
            "block": "Objects that can be picked up and placed on the table or on top of another block.",
            "children": []
        },
        {
            "table": "A surface where blocks can be placed.",
            "children": []
        },
        {
            "robot_arm": "The mechanical arm that can pick up and place blocks.",
            "children": []
        },
        {
            "location": "General type for organizing the space where the blocks are placed.",
            "children": []
        }
    ]
}

[
'object ; Object is always root, everything is an object', 
'block - object ; Objects that can be picked up and placed on the table or on top of another block.', 
'table - object ; A surface where blocks can be placed.', 
'robot_arm - object ; The mechanical arm that can pick up and place blocks.', 
'location - object ; General type for organizing the space where the blocks are placed.'
]



{
    "object": "Object is always root, everything is an object",
    "children": [
        {
            "movable_object": "A type of object that can be placed on the table or on top of another object.",
            "children": [
                {
                    "block": "A type of movable_object.",
                    "children": []
                },
                {
                    "stack": "A type of movable_object.",
                    "children": []
                }
            ]
        },
        {
            "table": "A type of location where blocks can be placed.",
            "children": []
        },
        {
            "robot_arm": "The mechanical arm that can pick up and place blocks.",
            "children": []
        }
    ]
}


"""