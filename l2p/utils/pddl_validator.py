"""
This file contains collection of functions PDDL syntax validations
"""

from collections import OrderedDict
from .pddl_types import Predicate

class Syntax_Validator:

    def validate_unsupported_keywords(self, llm_response: str, unsupported_keywords: list[str]) -> tuple[bool, str]:
        """Checks whether PDDL model uses unsupported logic keywords"""

        for key in unsupported_keywords:
            if f'{key}' in llm_response:
                feedback_msg = f'ERROR: The precondition or effect contains the keyword {key}.'
                return False, feedback_msg

        feedback_msg = "PASS: Unsupported keywords not found in PDDL model."
        return True, feedback_msg

    def validate_params(self, parameters: OrderedDict, types: dict[str,str]) -> tuple[bool,str]:
        """Checks whether a PDDL action parameter contains types found in object types."""
        
        for param_name in parameters:
            param_type = parameters[param_name]

            if not any(param_type in t for t in types.keys()):
                feedback_msg = f'There is an invalid object type `{param_type}` for the parameter {param_name} not found in the types {types.keys()}. If you need to use a new type, you can emulate it with an "is_{{type}} ?o - object" precondition. Please revise the PDDL model to fix this error.'
                return False, feedback_msg
            
        feedback_msg = "PASS: All parameter types found in object types."
        return True, feedback_msg

    def validate_types_predicates(self, predicates: list[Predicate], types: dict[str,str]) -> tuple[bool,str]:
        """Check if predicate name is same as object type"""

        invalid_predicates = list()
        for pred in predicates:
            if pred['name'].lower() in types:
                invalid_predicates.append(pred['name'])
        if len(invalid_predicates) > 0:
            feedback_msg = f'ERROR: The following predicate(s) have the same name(s) as existing object types:'
            for pred_i, pred_name in enumerate(list(invalid_predicates)):
                feedback_msg += f'\n{pred_i + 1}. {pred_name}'
            feedback_msg += '\nPlease rename these predicates.'
            return False, feedback_msg
        
        feedback_msg = "PASS: all predicate names are unique to object type names"
        return True, feedback_msg

    def validate_duplicate_predicates(self, curr_predicates: list[Predicate], new_predicates: list[Predicate]) -> tuple[bool,str]:
        
        curr_pred_dict = {pred['name'].lower(): pred for pred in curr_predicates}
        duplicated_predicates = list()

        for predicates in new_predicates:
            if predicates['name'].lower() in curr_pred_dict:
                curr = curr_pred_dict[new_predicates['name'].lower()]
                if len(curr['params']) != len(predicates['params']) or any([t1 != t2 for t1,t2 in zip(curr['params'], predicates['params'])]):
                    duplicated_predicates.append((predicates['raw'], curr_pred_dict[predicates['name'].lower()]['raw']))
        
        if len(duplicated_predicates) > 0:
            feedback_msg = f'ERROR: The following predicate(s) have the same name(s) as existing predicate(s):'
            for pred_i, duplicate_pred_info in enumerate(duplicated_predicates):
                new_pred_full, existing_pred_full = duplicate_pred_info
                feedback_msg += f'\n{pred_i + 1}. {new_pred_full.replace(":", ",")}; existing predicate with the same name: {existing_pred_full.replace(":", ",")}'
            
            feedback_msg += '\n\nYou should reuse existing predicates whenever possible. If you are reusing existing predicate(s), you shouldn\'t list them under \'New Predicates\'. If existing predicates are not enough and you are devising new predicate(s), please use names that are different from existing ones.'
            feedback_msg += '\n\nPlease revise the PDDL model to fix this error.\n\n'
            feedback_msg += 'Parameters:'
            return False, feedback_msg
        
        feedback_msg = "PASS: all predicate names are unique to each other"
        return True, feedback_msg


    def validate_preconditions(self): pass

    def validate_effects(self): pass

    def validate_types(self): pass


    def validate_objects(self): pass

    def validate_initial_state(self): pass

    def validate_goal_state(self): pass

    
if __name__ == '__main__':

    unsupported_keywords = ['balls']

    pddl_snippet = """
    Apologies for the confusion. Since the predicates are already defined, I will not list them under 'New Predicates'. Here is the revised PDDL model.

    Parameters:
    1. ?x - householdObject: the object to put in/on the furniture or appliance
    2. ?y - furnitureAppliance: the furniture or appliance to put the object in/on

    (:types city - location location vehicle - object airplane truck - vehicle)

    Preconditions:
    ```
    (and
        (robot-at ?y)
        (robot-holding ?x)
        (pickupable ?x)
        (object-clear ?x)
        (or
            (not (openable ?y))
            (opened ?y)
        )
    )
    ```

    Effects:
    ```
    (and
        (not (robot-holding ?x))
        (robot-hand-empty)
        (object-on ?x ?y)
        (if (openable ?y) (closed ?y))
    )
    ```

    New Predicates:
    1. (closed ?y - furnitureAppliance): true if the furniture or appliance ?y is closed
    2. (openable ?y - householdObject): true if the furniture or appliance ?y can be opened
    3. (furnitureappliance ?x - furnitureAppliance): true if xxxxxxxxx
        """
    
    params = {
        '?x': 'truck',
        '?y': 'object'
        }
    
    types = {
        'object': '; Object is always root, everything is an object', 
        'truck - vehicle': '; A type of vehicle used for transporting packages within locations in a city.', 
        'airplane - vehicle': '; A type of vehicle used for transporting packages between cities.', 
        'location - object': '; A type of object consisting of places within a city that are directly linked to other locations.', 
        'city - location': '; A type of location representing a city that is directly connected to other cities.'
        }
    
    # validated, feedback_msg = validate_unsupported_keywords(pddl_snippet, unsupported_keywords)
    validated, feedback_msg = validate_params(params, types)

    print("Validated:", validated)
    print("Feedback Message:", feedback_msg)

