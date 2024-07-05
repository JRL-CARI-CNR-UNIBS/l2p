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



# def extract_types(type_hierarchy) -> dict[str,str]:
#     def process_node(node, parent_type=None):
#         current_type = list(node.keys())[0]
#         description = node[current_type]
#         parent_type = parent_type if parent_type else current_type
#         formatted_str = f"{current_type} - {parent_type} ; {description}" if current_type != parent_type else f"{current_type} ; {description}"
        
#         result.add(formatted_str)
#         for child in node.get("children", []):
#             process_node(child, current_type)

#     result = {}
#     process_node(type_hierarchy)
#     return result


# def extract_types(type_hierarchy: dict[str,str]) -> dict[str,str]:
#     def process_node(node, parent_type=None):
#         current_type = list(node.keys())[0]
#         description = node[current_type]
#         parent_type = parent_type if parent_type else current_type

#         name = f"{current_type} - {parent_type}" if current_type != parent_type else f"{current_type}"
#         desc = f"; {description}"
        
#         result[name] = desc

#         for child in node.get("children", []):
#             process_node(child, current_type)

#     result = {}
#     process_node(type_hierarchy)
#     return result


# type_hierarchy = {
#     "object": "Object is always root, everything is an object",
#     "children": [
#         {
#             "place": "A type of object consisting of locations within a city.",
#             "children": [
#                 {
#                     "location": "A type of place.",
#                     "children": []
#                 },
#                 {
#                     "city": "A type of place containing multiple locations.",
#                     "children": []
#                 }
#             ]
#         },
#         {
#             "package": "A type of object consisting of items that need to be transported.",
#             "children": []
#         },
#         {
#             "vehicle": "A type of object consisting of vehicles.",
#             "children": [
#                 {
#                     "truck": "A type of vehicle.",
#                     "children": []
#                 },
#                 {
#                     "airplane": "A type of vehicle.",
#                     "children": []
#                 }
#             ]
#         }
#     ]
# }


# types = extract_types(type_hierarchy=type_hierarchy)
# print(types)


"""
- object: The root type, everything is an object.
    - person: A type of object that includes individuals within the Catholic Church.
        - Catholic: A person who practices the Catholic faith.
            - clergy: A Catholic who has taken holy orders and serves the Church.
                - Priest: A clergy member who serves the Church.
                    - Bishop: A higher-ranking priest responsible for overseeing a diocese.
                        - Archbishop: A bishop who oversees an archdiocese and other bishops.
                            - Cardinal: A bishop or archbishop appointed by the Pope to the College of Cardinals.
                                - Pope: The highest-ranking leader of the Catholic Church.
    - role: A type of object representing various roles within the Catholic Church.
        - Priesthood: The role and duties of a priest.
        - Leadership: Positions of authority such as bishops, archbishops, and cardinals.
    - location: A type of object representing places within the Catholic Church.
        - Church: The general place of worship and community for Catholics.
        - Diocese: A district under the pastoral care of a bishop.
        - Archdiocese: A larger district under the pastoral care of an archbishop.
        - Vatican: The sovereign state and residence of the Pope.
    - process: A type of object representing various processes within the Catholic Church.
        - Rite of Christian Initiation: The process of becoming a Catholic.
        - Catechism: Education in the Catholic faith.
        - Ordination: The process by which a person becomes a priest.
        - Conclave: The process of electing a new Pope.
"""

        # """ FEEDBACK MECHANISM """
        # if feedback is not None:
        #     if feedback.lower() == "human":
        #         feedback_msg = human_feedback(f"\n\nThe types extracted are:\n{type_str}\n")
        #     else:
        #         feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        #         feedback_template = feedback_template.replace('{type_list}', type_str)
        #         feedback_msg = self.type_get_llm_feedback(model, feedback_template)
        #     if feedback_msg is not None:
        #         messages = [
        #             {'role': 'user', 'content': prompt_template},
        #             {'role': 'assistant', 'content': llm_response},
        #             {'role': 'user', 'content': feedback_msg}
        #         ]
        #         llm_response = model.get_output(messages=messages)
        #         if "## Types" in llm_response:
        #             header = llm_response.split("## Types")[1].split("## ")[0]
        #         else:
        #             header = llm_response
        #         dot_list = combine_blocks(header)
        #         if len(dot_list) == 0:
        #             dot_list = "\n".join([l for l in header.split("\n") if l.strip().startswith("-")])
        #         if dot_list.count("-") == 0: # No types
        #             return {}
        #         types = dot_list.split('\n')
        #         types = [t.strip("- \n") for t in types if t.strip("- \n")] # Remove empty strings and dashes

        #         type_dict = {
        #                 t.split(":")[0].strip().replace(" ", "_"): 
        #                 t.split(":")[1].strip()
        #             for t in types
        #         }

                # dict_pattern = re.compile(r'{.*}', re.DOTALL) # regular expression to find the JSON-like dictionary structure
        # match = dict_pattern.search(llm_response) # search for the pattern in the llm_response

        # if match:
        #     dict_str = match.group(0)

        #     """ FEEDBACK MECHANISM """
        #     if feedback is not None:
        #         if feedback.lower() == "human":
        #             feedback_msg = human_feedback(f"\n\nThe hierarchy constructed is:\n{dict_str}\n")
        #         else:
        #             feedback_template = feedback_template.replace('{type_hierarchy}', dict_str)
        #             feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        #             feedback_msg = self.hierarchy_get_llm_feedback(model, feedback_template)

        #         if feedback_msg is not None:
        #             messages = [
        #                 {'role': 'user', 'content': prompt_template},
        #                 {'role': 'assistant', 'content': llm_response},
        #                 {'role': 'user', 'content': feedback_msg}
        #             ]
        #             llm_response = model.get_output(messages=messages)
        #             dict_pattern = re.compile(r'{.*}', re.DOTALL) # regular expression to find the JSON-like dictionary structure
        #             match = dict_pattern.search(llm_response) # search for the pattern in the llm_response

        #     # safely evaluate the string to convert it into a Python dictionary
        #     try:
        #         type_hierarchy = ast.literal_eval(dict_str)
  
        #         return type_hierarchy
        #     except Exception as e:
        #         print(f"Error parsing dictionary: {e}")
        #         return None
        # else:
        #     print("No dictionary found in the llm_response.")
        #     return None

                # if feedback is not None:
        #     if feedback.lower() == "human":
        #         action_strs = "\n".join([f"- {name}: {desc}" for name, desc in nl_actions.items()])
        #         feedback_msg = human_feedback(f"\n\nThe actions extracted are:\n{action_strs}\n")
        #     else:
        #         feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        #         feedback_template = feedback_template.replace('{type_hierarchy}', str(type_hierarchy))
        #         feedback_msg = self.nl_action_get_llm_feedback(model, nl_actions, feedback_template)
        #     if feedback_msg is not None:
        #         messages = [
        #             {'role': 'user', 'content': prompt_template},
        #             {'role': 'assistant', 'content': llm_response},
        #             {'role': 'user', 'content': feedback_msg}
        #         ]
        #         llm_response = model.get_output(messages=messages)

        #         # extract list of actions section
        #         splits = llm_response.split("```")
        #         action_outputs = [splits[i].strip() for i in range(1, len(splits), 2)] # Every other split *should* be an action

        #         # parse actions into dict[str, str]
        #         nl_actions = {}
        #         for action in action_outputs:
        #             name = action.split("\n")[0].strip()
        #             desc = action.split("\n", maxsplit=1)[1].strip() # Works even if there is no blank line
        #             nl_actions[name] = desc

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements
from pddl import parse_domain

domain_file = 'data/domain.pddl'

domain = parse_domain(domain_file)
pddl_domain = domain_to_string(domain)

print(pddl_domain)

# Write PDDL domain string to a file
with open(domain_file, "w") as f:
    f.write(pddl_domain)

print(f"PDDL domain written to {domain_file}")




    # print("\n\n---------------------------------\n\nAdding new type output:\n")

    # user_input = input("Please enter the type you want to add:\n")
    # prompt = "You are to add a new type into the types already listed. Format it the same way in Python dictionary\n\n" + user_input 

    # new_types = domain_builder.add_type(
    #      model=model,
    #      domain_desc=domain_desc,
    #      prompt_template=prompt
    # )
    # domain_builder.set_types(types=new_types)
    # print("New types: ", format_json_output(domain_builder.get_types()))

    # # extract type hierarchy
    # print("\n\n---------------------------------\n\nType hierarchy output:\n")
    # type_hierarchy = domain_builder.extract_type_hierarchy(
    #     model=model, 
    #     domain_desc=domain_desc, 
    #     prompt_template=type_hierarchy_prompt.get_prompt(), 
    #     types=domain_builder.get_types(),
    #     feedback="LLM",
    #     feedback_template=open_file('data/prompt_templates/hierarchy_construction/feedback.txt')
    #     )
    # domain_builder.set_type_hierarchy(type_hierarchy=type_hierarchy)
    # print(format_json_output(type_hierarchy))