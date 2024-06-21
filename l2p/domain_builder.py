"""
This file contains collection of functions for PDDL generation purposes

EXPERIMENT IF IT IS BETTER TO CREATE KNOWLEDGE GRAPH OR HAVE ITERATED DOMAIN GENERATION
"""

class Domain_Builder:
    def __init__(self,types, type_hierarchy, predicates, actions):
        self.types=types
        self.type_hierarchy=type_hierarchy
        self.predicates=predicates
        self.actions=actions

    def extract_type(self, model, prompt):
        response = model.get_response(prompt)

        print(response)
        
        start_marker = "(:types"
        end_marker = ")"

        start_index = response.find(start_marker)
        end_index = response.find(end_marker, start_index)

        if start_index == -1 or end_index == -1:
            raise ValueError("PDDL types section not found in the response")

        # Extract the PDDL types section
        pddl_section = response[start_index:end_index + len(end_marker)]

        # Initialize an empty dictionary to store the parsed types
        types_dict = {}

        # Split the section by lines for processing
        lines = pddl_section.strip().split('\n')

        # Process each line in the types section

        flag = False

        for line in lines:
            # Trim any leading/trailing whitespace
            line = line.strip()

            # Skip the (:types line and the closing parenthesis
            if line.startswith("(:types") or line.startswith(")") and flag == False:
                flag = True
                continue
            
            # Split the line by ';' to separate type and description
            if ';' in line:
                type_name, description = line.split(';', 1)
                type_name = type_name.strip()
                description = description.strip()
                types_dict[type_name] = description

        return response, types_dict
    

    def extract_type_hierarchy(self, model, prompt, type_list):
        response = model.get_response(prompt + "\n" + str(type_list))

        # Define the start and end markers for the hierarchy section
        hierarchy_start = "```"
        hierarchy_end = "```"

        # Extract the hierarchy section from the response
        start_index = response.find(hierarchy_start)
        end_index = response.find(hierarchy_end, start_index + len(hierarchy_start))

        if start_index == -1 or end_index == -1:
            raise ValueError("Hierarchy section not found in the response")

        hierarchy_section = response[start_index + len(hierarchy_start):end_index].strip().split("\n")

        # Initialize an empty dictionary to store the knowledge graph
        knowledge_graph = {}

        # Initialize a stack to keep track of the current path in the hierarchy
        stack = []

        for line in hierarchy_section:
            if line.strip().startswith("- "):
                # Remove leading/trailing whitespace and any preceding hyphens and spaces
                clean_line = line.lstrip('- ').strip()
                
                # Determine the current level of indentation (number of leading spaces)
                level = (len(line) - len(line.lstrip(' '))) // 4
                
                # Create a new node for the current line
                new_node = {'name': clean_line, 'children': []}
                
                # Adjust the stack to the current level
                while len(stack) > level:
                    stack.pop()
                
                # Insert the new node into the knowledge graph at the correct position
                if stack:
                    parent = stack[-1]
                    parent['children'].append(new_node)
                    stack.append(parent['children'][-1])
                else:
                    # If stack is empty, we are at the root level
                    knowledge_graph = new_node
                    stack.append(knowledge_graph)

        return response, knowledge_graph


    def add_type():
        # user inputs prompt to add a type to the domain, LLM takes current domain info and dynamically modifies file to integrate new type
        pass


    def add_action():
        # user inputs prompt to add an action to the domain, LLM takes current domain info and dynamically modifies file to integrate new action
        pass


    def delete_type():
        pass


    def delete_action():
        pass


    def extract_NL_action():
        pass


    def extract_action():
        pass


    def generate_domain():
        pass


    def get_types():
        # retrieve list of types and parse it to show PDDL format
        pass


    def get_type_hierarchy():
        pass


    def get_actions():
        pass


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