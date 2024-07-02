# """
# Activate virtual environment: source env/bin/activate

# L2P Checklist

# - [ ] Integrate action-construction architecture into work
#     - [ ] Implement add_predicates
# - [ ] Distribute each component into its separate class, let domain_builder be the coordinating class
# - [ ] Implement auto-feedback checklist
# - [ ] Implement LLM-generated feedback checklist
# - [ ] Implement PDDL generator — parser to assemble everything together

# - The action_construction pipeline consists of:
#     - Action extraction loop
#         - For each action description, construct singular action (parameter, precondition, effects) based on current predicts and put into a list
#         - Update list of new predicates 
#         - Prune unused predicates and types
#     - Once all actions generated, add actions (iteratively) and predicates to PDDLGenerator

# PDDLGenerator is essentially domain_builder / task_builder — CHANGE THINGS AROUND TO PERFORM SAME FUNCTION

# - [ ] Implement add_type — run through 
# - [ ] Implement add_action — run through whole pipeline

# - [ ] Implement task_builder
#     - [ ] extract_object
#     - [ ] extract_initial_state
#     - [ ] extract_goal_state
#     - [ ] Implement get functions
#     - [ ] Implement add functions — pipelines

# - [ ] Implement external planner tool
# # I would like to add the new types "country" and "continent"s

# """

# from pddl.logic import Predicate, constants, variables
# from pddl.core import Domain, Problem
# from pddl.action import Action
# from pddl.formatter import domain_to_string, problem_to_string
# from pddl.requirements import Requirements

# # # set up variables and constants
# # x, y, z = variables("x y z", types=["type_1"])
# # a, b, c = constants("a b c", type_="type_1")

# # # define predicates
# # p1 = Predicate("p1", x, y, z)
# # p2 = Predicate("p2", x, y)

# # # define actions
# # a1 = Action(
# #     "action-1",
# #     parameters=[x, y, z],
# #     precondition=p1(x, y, z) & ~p2(y, z),
# #     effect=p2(y, z)
# # )

# # # define the domain object.
# # requirements = [Requirements.STRIPS, Requirements.TYPING]
# # domain = Domain("my_domain",
# #                 requirements=requirements,
# #                 types={"type_1": None},
# #                 constants=[a, b, c],
# #                 predicates=[p1, p2],
# #                 actions=[a1])

# # print(domain_to_string(domain))

# # """
# # (define (domain my_domain)
# #     (:requirements :strips :typing)
# #     (:types type_1)
# #     (:constants a b c - type_1)
# #     (:predicates (p1 ?x - type_1 ?y - type_1 ?z - type_1)  (p2 ?x - type_1 ?y - type_1))
# #     (:action action-1
# #         :parameters (?x - type_1 ?y - type_1 ?z - type_1)
# #         :precondition (and (p1 ?x ?y ?z) (not (p2 ?y ?z)))
# #         :effect (p2 ?y ?z)
# #     )
# # )
# # """

# # problem = Problem(
# #     "problem-1",
# #     domain=domain,
# #     requirements=requirements,
# #     objects=[a, b, c],
# #     init=[p1(a, b, c), ~p2(b, c)],
# #     goal=p2(b, c)
# # )
# # print(problem_to_string(problem))

# # """
# # (define (problem problem-1)
# #     (:domain my_domain)
# #     (:requirements :strips :typing)
# #     (:objects a b c - type_1)
# #     (:init (not (p2 b c)) (p1 a b c))
# #     (:goal (p2 b c))
# # )
# # """

# # def parse_predicate(predicate_str):
# #     # Remove "PREDICATES: " prefix, parentheses and split the string
# #     predicate_str = predicate_str.strip(' ()')
# #     parts = predicate_str.split()
    
# #     # Extract predicate name
# #     predicate_name = parts[0]
    
# #     # Extract variables and their types
# #     variables_list = []
# #     types = []
    
# #     i = 1
# #     while i < len(parts):
# #         var = parts[i].replace('?', '')  # Remove question mark
# #         type_ = parts[i + 2]  # Get the type from the next index + 2
# #         variables_list.append(var)
# #         types.append(type_)
# #         i += 3  # Move to the next variable
    
# #     # Create variables using the PDDL library
# #     var_objects = variables(' '.join(variables_list), types=types)
    
# #     # Create the predicate
# #     predicate = Predicate(predicate_name, *var_objects)
    
# #     return predicate

# # # Example usage
# # predicate_strs = [
# #     "(on_table ?b - block)",
# #     "(holding ?robot_arm - object ?block - object)",
# #     "(on ?b1 - block ?b2 - block)"
# # ]

# # for predicate_str in predicate_strs:
# #     predicate = parse_predicate(predicate_str)
# #     # print(predicate)

# from typing import List, Dict, TypedDict
# from pddl.logic import Predicate, constants, variables
# from pddl.core import Domain
# from pddl.action import Action
# from pddl.formatter import domain_to_string
# from pddl.requirements import Requirements

# # Define the ActionList structure
# class ActionList(TypedDict):
#     name: str
#     desc: str
#     raw: str
#     parameters: List[Dict[str, str]]
#     preconditions: str
#     effects: str

# def parse_predicate(predicate: str) -> tuple[Predicate, list[str], list[variables]]:

#     parts = predicate.replace('(', '').replace(')', '').split()
#     name = parts[0]
#     var_names = []
#     var_types_extracted = []
    
#     # Extract variable names and types
#     for i in range(1, len(parts), 3):
#         if i+1 < len(parts) and parts[i+1] == '-':
#             var_name = parts[i].strip('?')
#             var_type = parts[i+2]
#             var_names.append(var_name)
#             var_types_extracted.append(var_type)
    
#     # Debugging information
#     print(f"Parsing predicate: {predicate}")
#     print(f"Extracted variable names and types: {list(zip(var_names, var_types_extracted))}")

#     vars = []
#     for var_name, var_type in zip(var_names, var_types_extracted):

#         # print(f"Var name: {var_name}")
#         # print(f"Var type: {var_type}")

#         vars.append(variables(var_name, types=[var_type])[0])

#     return Predicate(name, *vars), name, vars



# def parse_action(action: ActionList, predicates: list[Predicate]=None) -> Action:
#     name = action['name']

#     params = []
#     for param in action['parameters']:
#         params.append(variables(param['name'].strip('?'), types=[param['type']])[0])
    
#     # Debugging information
#     print(f"Parsing action: {name}")
#     print(f"Parameters: {params}")

#     for p in predicates:
#         print(p.name)
#         # match predicate name with predicate found within action precondition/effect
#         # if cases of and/not/or statements





# def generate_pddl_code(types: List[str], predicates: List[str], actions: List[ActionList], constants_list: List[Dict[str, str]] = None) -> str:

#     pred_list = []
#     name_list = []
#     var_list = []

#     for p in predicates:
#         parsed_predicate, name, vars = parse_predicate(p)

#         pred_list.append(parsed_predicate)
#         name_list.append(name)
#         var_list.extend(vars)
        
#     print("")
#     print(f"Parsed predicate: {pred_list}")
#     print(f"Named predicate: {name_list}")
#     print(f"Variables: {var_list}")

#     action_list = []

#     for a in actions:
#         action = parse_action(a, pred_list)
#         # action_list.append(action)


#     # Define domain
#     requirements = [Requirements.STRIPS, Requirements.TYPING]
#     types_dict = {t: None for t in types}

#     domain = Domain("my_domain",
#                     requirements=requirements,
#                     types=types_dict,
#                     predicates=pred_list
#                     )

#     return domain_to_string(domain)

#     # Define constants dynamically
#     # const_objects = [constants(c['name'], type_=c['type'])[0] for c in constants_list]



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

# # def extract_types(type_hierarchy):
# #     def process_node(node, parent_type=None):
# #         current_type = list(node.keys())[0]
# #         description = node[current_type]
# #         parent_type = parent_type if parent_type else current_type
# #         formatted_str = f"{current_type} - {parent_type} ; {description}" if current_type != parent_type else f"{current_type} ; {description}"
        
# #         result.append(formatted_str)
# #         for child in node.get("children", []):
# #             process_node(child, current_type)

# #     result = []
# #     process_node(type_hierarchy)
# #     return result

# # type_hierarchy = {
# #     "object": "Object is always root, everything is an object",
# #     "children": [
# #         {
# #             "block": "Objects that can be picked up and placed on the table or on top of another block.",
# #             "children": []
# #         },
# #         {
# #             "table": "A surface where blocks can be placed.",
# #             "children": []
# #         },
# #         {
# #             "robot_arm": "The mechanical arm that can pick up and place blocks.",
# #             "children": []
# #         },
# #         {
# #             "location": "General type for organizing the space where the blocks are placed.",
# #             "children": []
# #         }
# #     ]
# # }

# # converted_list = extract_types(type_hierarchy)
# # print(converted_list)

# """
# {
#     "object": "Object is always root, everything is an object",
#     "children": [
#         {
#             "block": "Objects that can be picked up and placed on the table or on top of another block.",
#             "children": []
#         },
#         {
#             "table": "A surface where blocks can be placed.",
#             "children": []
#         },
#         {
#             "robot_arm": "The mechanical arm that can pick up and place blocks.",
#             "children": []
#         },
#         {
#             "location": "General type for organizing the space where the blocks are placed.",
#             "children": []
#         }
#     ]
# }

# [
# 'object ; Object is always root, everything is an object', 
# 'block - object ; Objects that can be picked up and placed on the table or on top of another block.', 
# 'table - object ; A surface where blocks can be placed.', 
# 'robot_arm - object ; The mechanical arm that can pick up and place blocks.', 
# 'location - object ; General type for organizing the space where the blocks are placed.'
# ]



# {
#     "object": "Object is always root, everything is an object",
#     "children": [
#         {
#             "movable_object": "A type of object that can be placed on the table or on top of another object.",
#             "children": [
#                 {
#                     "block": "A type of movable_object.",
#                     "children": []
#                 },
#                 {
#                     "stack": "A type of movable_object.",
#                     "children": []
#                 }
#             ]
#         },
#         {
#             "table": "A type of location where blocks can be placed.",
#             "children": []
#         },
#         {
#             "robot_arm": "The mechanical arm that can pick up and place blocks.",
#             "children": []
#         }
#     ]
# }


# """

# # from l2p.llm_builder import get_llm

# # model = get_llm("gpt-3.5-turbo-0125")

# # string = """ Give me the most efficient way of doing this: "formatted_types = ""
# #     for i in pruned_types:
# #         formatted_types += f"{i}\n"" """


# # print(model.get_response(prompt=string))

#     # print("\n\n---------------------------------\n\n")
#     # print("Adding new type:\n")

#     # types = domain_builder.add_type(model=model, domain_desc=domain_desc, prompt_template=type_extraction_prompt.get_prompt())
#     # domain_builder.set_types(types=types)
#     # print("New types: ", format_json_output(domain_builder.get_types()))

#     # print("\n\n---------------------------------\n\n")
#     # print("New type hierarchy output:\n")

#     # type_hierarchy = domain_builder.extract_type_hierarchy(model=model, domain_desc=domain_desc, prompt_template=type_hierarchy_prompt.get_prompt(), types=domain_builder.get_types())
#     # domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
#     # print(format_json_output(type_hierarchy))

# """
# (define (domain test_domain)
#    (:requirements
#       :strips :typing :equality :negative-preconditions :disjunctive-preconditions
#       :universal-preconditions :conditional-effects
#    )

#    (:types 
#       object ; Object is always root, everything is an object
#       block - object ; Objects that can be picked up and placed on the table or on top of another block.
#       table - object ; A surface where blocks can be placed.
#       robot_arm - object ; The mechanical arm that can pick up and place blocks.
#       location - object ; General type for organizing the space where the blocks are placed.
#    )

#    (:predicates 
#       (held ?b - object ?r - object) ;  true if the object ?b is held by the object ?r
#       (on_table ?b - object) ;  true if the object ?b is placed on the table
#       (on ?b1 - block ?b2 - block) ;  true if block ?b1 is placed on top of block ?b2
#    )

#    (:action pick_up_block
#       :parameters (
#          ?robot_arm - object
#          ?block - object
#          ?location - location
#       )
#       :precondition
#          (and
#              (at ?robot_arm ?location) ; The robot arm is at the location
#              (at ?block ?location) ; The block is at the location
#          )
#       :effect
#          (and
#              (not (at ?block ?location)) ; The block is no longer at the location
#              (held ?block ?robot_arm) ; The block is now held by the robot arm
#          )
#    )

#    (:action place_on_table
#       :parameters (
#          ?r - object
#          ?b - object
#       )
#       :precondition
#          (and
#              (held ?b ?r) ; The robot arm is holding the block
#          )
#       :effect
#          (and
#              (not (held ?b ?r)) ; The block is no longer held by the robot arm
#              (on_table ?b) ; The block is now placed on the table
#          )
#    )

#    (:action place_on_block
#       :parameters (
#          ?r - object
#          ?b - block
#          ?on_block - block
#       )
#       :precondition
#          (and
#              (held ?b ?r) ; The robot arm is holding the block
#              (on_table ?on_block) ; The block on which the other block is being placed is on the table
#          )
#       :effect
#          (and
#              (not (held ?b ?r)) ; The block is no longer held by the robot arm
#              (on ?b ?on_block) ; The block is now placed on top of the specified block
#          )
#    )

#    (:action move_block
#       :parameters (
#          ?r - object
#          ?b - object
#          ?from - location
#          ?to - location
#       )
#       :precondition
#          (and
#              (held ?b ?r) ; The robot arm is holding the block
#              (at ?b ?from) ; The block is at the starting location
#              (not (on ?b ?b2)) ; The block is not on top of another block
#          )
#       :effect
#          (and
#              (not (at ?b ?from)) ; The block is no longer at the starting location
#              (at ?b ?to) ; The block is now at the destination location
#          )
#    )
# """

# import re

# def parse_logical_expression(expression):
#     # Define mappings for logical operators
#     operator_mappings = {
#         'and': '&',
#         'or': '|',
#         'not': '~'
#     }
    
#     # Function to replace operators in a match object
#     def replace_operator(match):
#         return operator_mappings[match.group(0)]
    
#     # Regular expression to find logical operators
#     operator_pattern = re.compile(r'\b(and|or|not)\b')
    
#     # Replace logical operators with their Python equivalents
#     reformatted_expression = operator_pattern.sub(replace_operator, expression)
    
#     # Add spaces around parentheses to ensure proper tokenization
#     reformatted_expression = re.sub(r'(\(|\))', r' \1 ', reformatted_expression)
    
#     # Tokenize the expression
#     tokens = reformatted_expression.split()
    
#     # Stack to keep track of expressions
#     stack = []
    
#     for token in tokens:
#         if token == ')':
#             # Pop elements until '('
#             expr = []
#             while stack and stack[-1] != '(':
#                 expr.append(stack.pop())
#             stack.pop()  # Remove '('
#             expr.reverse()
            
#             # Combine the expression
#             if expr[0] == '~':
#                 combined = f"~{''.join(expr[1:])}"
#             else:
#                 combined = f"({' '.join(expr)})"
#             stack.append(combined)
#         else:
#             stack.append(token)
    
#     # Join the final expression
#     final_expression = ' '.join(stack)
    
#     # Replace multiple spaces with a single space
#     final_expression = re.sub(r'\s+', ' ', final_expression)
    
#     # Ensure proper formatting for the final expression
#     final_expression = final_expression.replace('( ', '(').replace(' )', ')')
    
#     return final_expression

# # Test cases
# expressions = [
#     ("(and (not (at ?r ?prev_loc)) (at ?r ?loc))", "~(at ?r ?prev_loc) & (at ?r ?loc)"),
#     ("(and (not (at ?r ?loc)) (on_table ?loc))", "~(at ?r ?loc) & (on_table ?loc)"),
#     ("(and (held ?b ?r) (at ?b ?from) (not (on ?b ?b2)))", "(held ?b ?r) & (at ?b ?from) & ~(on ?b ?b2)"),

#     ("(and (and (held ?b ?r) (at ?b ?from)) (not (on ?b ?b2)))", "((held ?b ?r) & (at ?b ?from)) & ~(on ?b ?b2)")
# ]

# for expr, expected in expressions:
#     result = parse_logical_expression(expr)
#     print(f"Expression: {expr}\nExpected: {expected}\nResult: {result}\n")

# """
# Expression: (& ~(at ?r ?prev_loc) (at ?r ?loc))
# Expected: ~(at ?r ?prev_loc) & (at ?r ?loc)

# Expression: (& ~(at ?r ?loc) (on_table ?loc))
# Expected: ~(at ?r ?loc) & (on_table ?loc)

# Expression: (& (held ?b ?r) (at ?b ?from) ~(on ?b ?b2))
# Expected: (held ?b ?r) & (at ?b ?from) & ~(on ?b ?b2)

# Expression: (& (& (held ?b ?r) (at ?b ?from)) ~(on ?b ?b2))
# Expected: ((held ?b ?r) & (at ?b ?from)) & ~(on ?b ?b2)
# """


from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements
from pddl import parse_domain

domain = parse_domain('data/domain.pddl')

print(domain_to_string(domain))