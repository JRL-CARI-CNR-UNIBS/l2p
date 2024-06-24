"""
This file contains collection of functions for PDDL generation purposes

EXPERIMENT IF IT IS BETTER TO CREATE KNOWLEDGE GRAPH OR HAVE ITERATED DOMAIN GENERATION
"""

import re
import ast

class Domain_Builder:
    def __init__(self, types, type_hierarchy, predicates, actions):
        self.types=types
        self.type_hierarchy=type_hierarchy
        self.predicates=predicates
        self.actions=actions

    def extract_type(self, model, prompt):

        response = model.get_response(prompt)
        
        # Regular expression to find the JSON-like dictionary structure
        dict_pattern = re.compile(r'{.*}', re.DOTALL)
        
        # Search for the pattern in the response
        match = dict_pattern.search(response)
        
        if match:
            dict_str = match.group(0)
            
            # Safely evaluate the string to convert it into a Python dictionary
            try:
                dictionary = ast.literal_eval(dict_str)
                self.types=dictionary
                return response, dictionary
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return None
        else:
            print("No dictionary found in the response.")
            return None
    

    def extract_type_hierarchy(self, model, prompt, type_list):
        response = model.get_response(prompt + "\n" + str(type_list))

        # Regular expression to find the JSON-like dictionary structure
        dict_pattern = re.compile(r'{.*}', re.DOTALL)
        
        # Search for the pattern in the response
        match = dict_pattern.search(response)
        
        if match:
            dict_str = match.group(0)
            
            # Safely evaluate the string to convert it into a Python dictionary
            try:
                dictionary = ast.literal_eval(dict_str)
                self.type_hierarchy=dictionary
                return response, dictionary
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return None
        else:
            print("No dictionary found in the response.")
            return None
        
    def extract_NL_actions(self, model, prompt):
        response = model.get_response(prompt + "\n" + str(self.types) + "\n" + str(self.type_hierarchy))
        print(response)


    def add_type(self, model, prompt):
        # user inputs prompt to add a type to the domain, LLM takes current domain info and dynamically modifies file to integrate new type
        user_input = input("Please describe the type you would like to add to the domain file: ")
        response, types_dict = self.extract_type(model, prompt + "\n" + user_input + " Here are the original types: \n" + str(self.types))

        return response, types_dict

    def add_action():
        # user inputs prompt to add an action to the domain, LLM takes current domain info and dynamically modifies file to integrate new action
        pass


    def delete_type():
        pass


    def delete_action():
        pass


    def extract_NL_action():
        # singular action
        pass


    def extract_action():
        pass


    def generate_domain():
        pass


    def get_types(self):
        return self.types


    def get_type_hierarchy(self):
        return self.type_hierarchy


    def get_actions(self):
        return self.actions


    def get_type_checklist():
        pass


    def get_hierarchy_checklist():
        pass


    def get_action_checklist():
        pass


if __name__ == "__main__":
    
    domain = Domain_Builder()
    description = "The AI agent here is a mechanical robot arm that can pick and place the blocks. Only one block may be moved at a time: it may either be placed on the table or placed atop another block. Because of this, any blocks that are, at a given time, under another block cannot be moved."
    
    print(domain.extract_type("GPT-3.5-Turbo", description))