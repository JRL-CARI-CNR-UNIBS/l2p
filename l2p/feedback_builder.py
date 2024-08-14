"""
This file contains collection of functions for PDDL feedback generation purposes
"""

from .llm_builder import LLM_Chat
from .utils.pddl_parser import convert_to_dict, parse_action, parse_new_predicates, parse_objects, parse_initial, parse_goal, parse_params, format_dict, format_predicates
from .utils.pddl_types import Action, Predicate
from collections import OrderedDict
import json

def format_json_output(data):
        return json.dumps(data, indent=4)

class FeedbackBuilder:

    def type_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            feedback_template: str, 
            feedback_type: str,
            types: dict[str,str], 
            llm_response: str=""
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into type format"""

        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        
        example = """START OF EXAMPLE:
## OUTPUT
{
    "location": "Locations can be visited and travelled between.",
    "house": "Constructed by the company. Are a type of location."
}
END OF EXAMPLE
"""
        
        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the types. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        
        new_types = convert_to_dict(llm_response=llm_feedback_response)
        return new_types, llm_feedback_response

    def type_hierarchy_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            feedback_template: str, 
            feedback_type: str,
            type_hierarchy: dict[str,str], 
            llm_response: str=""
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into type hierarchy format"""

        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        
        example = """START OF EXAMPLE:
## OUTPUT
{
    "location": "Locations can be visited and travelled between.",
    "house": "Constructed by the company. Are a type of location.",
}
END OF EXAMPLE
"""
        
        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the type hierarchy. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        
        type_hierarchy = convert_to_dict(llm_response=llm_feedback_response)
        return type_hierarchy, llm_feedback_response

    def nl_action_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str,
            feedback_type: str,
            nl_actions: dict[str,str], 
            llm_response: str="",
            type_hierarchy: dict[str,str]=None,
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into format"""

        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{nl_actions}', format_json_output(nl_actions))
        
        example = """START OF EXAMPLE:
## OUTPUT
{
    'build_floor: 'A worker performs an order to build a floor. Requires the worker to be there and for a build_floor_order for the house to exist. Example: worker_1 builds a floor at house_1 given that a build_floor_order for it exists.'
}   
"""

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the suggested natural language actions. Only follow what the suggestions made. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        new_nl_actions = convert_to_dict(llm_response=llm_feedback_response)
        return new_nl_actions, llm_feedback_response

    def pddl_action_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            feedback_type: str,
            action: Action, 
            predicates: list[Predicate], 
            types: dict[str,str], 
            llm_response: str=""
            ) -> tuple[Action, list[Predicate], str]:
        """Makes LLM call using feedback prompt, then parses it into format"""

        predicate_str = format_predicates(predicates)
        param_str = ", ".join([f"{name} - {type}" for name, type in action['parameters'].items()]) 
        
        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{action_name}', action['name'])
        feedback_template = feedback_template.replace('{parameters}', param_str)
        feedback_template = feedback_template.replace('{action_preconditions}', action['preconditions'])
        feedback_template = feedback_template.replace('{action_effects}', action['effects'])

        example = """START OF EXAMPLE:
### Action Parameters
```
- ?v - vehicle: The vehicle travelling
```

### Action Preconditions
```
(and
    (at ?v ?from) ; The vehicle is at the starting location
)
```

### Action Effects
```
(and
    (not (at ?v ?from)) ; ?v is no longer at ?from
)
```

### New Predicates
```
- (at ?o - object ?l - location): true if the object ?o (a vehicle or a worker) is at the location ?l
``` 
END OF EXAMPLE
        """

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL action and new predicates if added. Follow exact example syntax. Your end response must format the Action Parameters, Preconditions, and Effects, and New Predicates with ''' ''' comment blocks in PDDL as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        action = parse_action(llm_response=llm_feedback_response, action_name=action['name'])
        new_predicates = parse_new_predicates(llm_feedback_response)
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates

        return action, new_predicates, llm_feedback_response

    def parameter_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            feedback_type: str, 
            parameter: OrderedDict, 
            action_name: str, 
            action_desc: str,
            types: dict[str,str], 
            llm_response: str
            ):
        """Makes LLM call using feedback prompt, then parses it into precondition format"""

        param_str = "\n".join([f"{name} - {type}" for name, type in parameter.items()])
        
        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{action_name}', action_name)
        feedback_template = feedback_template.replace('{action_desc}', action_desc)
        feedback_template = feedback_template.replace('{parameters}', param_str)
        
        print(feedback_template)

        example = """START OF EXAMPLE:
### Action Parameters
```
- ?v - vehicle: The vehicle travelling
```
END OF EXAMPLE
"""

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL action parameter. End your final answer starting with '### Action Parameters'. Your end response must format the Action Parameters with ''' ''' comment blocks in PDDL as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        
        print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        parameter = parse_params(llm_output=llm_feedback_response)
        return parameter, llm_feedback_response

    def precondition_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            feedback_type: str, 
            parameter: OrderedDict, 
            preconditions: str,
            action_name: str, 
            action_desc: str,
            types: dict[str,str],
            predicates: list[Predicate], 
            llm_response: str
            ):
        """Makes LLM call using feedback prompt, then parses it into precondition format"""
        
        param_str = "\n".join([f"{name} - {type}" for name, type in parameter.items()])
        predicate_str = format_predicates(predicates)
        
        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{action_name}', action_name)
        feedback_template = feedback_template.replace('{action_desc}', action_desc)
        feedback_template = feedback_template.replace('{parameters}', param_str)
        feedback_template = feedback_template.replace('{action_preconditions}', preconditions)
        
        example = """START OF EXAMPLE:
### Action Preconditions
```
(and
    (at ?v ?from) ; The vehicle is at the starting location
)
```

### New Predicates
```
- (at ?o - object ?l - location): true if the object ?o (a vehicle or a worker) is at the location ?l
``` 
END OF EXAMPLE
"""

        # prompt =  "You are a PDDL feedback analyist that must run the checklist on the given preconditions. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        # print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL action precondition and new predicates if added. Your end response must format the Action Preconditions and New Predicates with ''' ''' comment blocks in PDDL as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        preconditions = llm_feedback_response.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        new_predicates = parse_new_predicates(llm_output=llm_feedback_response)
        
        return preconditions, new_predicates, llm_response

    def effects_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            feedback_type: str, 
            parameter: OrderedDict, 
            preconditions: str,
            effects: str,
            action_name: str, 
            action_desc: str,
            types: dict[str,str],
            predicates: list[Predicate], 
            llm_response: str
            ):
        """Makes LLM call using feedback prompt, then parses it into effects format"""
        param_str = "\n".join([f"{name} - {type}" for name, type in parameter.items()])
        predicate_str = format_predicates(predicates)
        
        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{action_name}', action_name)
        feedback_template = feedback_template.replace('{action_desc}', action_desc)
        feedback_template = feedback_template.replace('{parameters}', param_str)
        feedback_template = feedback_template.replace('{action_preconditions}', preconditions)
        feedback_template = feedback_template.replace('{action_effects}', effects)
        
        example = """START OF EXAMPLE:
### Action Effects
```
(and
    (not (at ?v ?from)) ; ?v is no longer at ?from
)
```

### New Predicates
```
- (at ?o - object ?l - location): true if the object ?o (a vehicle or a worker) is at the location ?l
``` 
END OF EXAMPLE
"""

        # prompt =  "You are a PDDL feedback analyist that must run the checklist on the given effects. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        # print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL action effects and new predicates if added. Your end response must format the Action Effects and New Predicates with ''' ''' comment blocks in PDDL as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        effects = llm_response.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
        new_predicates = parse_new_predicates(llm_output=llm_feedback_response)
        
        return effects, new_predicates, llm_feedback_response


    def task_feedback(
            self, 
            model: LLM_Chat, 
            problem_desc: str, 
            feedback_template: str, 
            feedback_type: str,
            predicates: list[Predicate], 
            types: dict[str,str], 
            objects: dict[str,str], 
            initial: list[dict[str,str]], 
            goal: list[dict[str,str]], 
            llm_response: str=""
            ) -> tuple[dict[str,str],str,str,str]:
        
        predicate_str = format_predicates(predicates)
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        inner_str = [f"({state['name']} {' '.join(state['params'])})" for state in initial] # The main part of each predicate
        full_str = [f"(not {inner})" if state["neg"] else inner for state, inner in zip(initial, inner_str)] # Add the `not` if needed
        initial_state_str = "\n".join(full_str) # Combine the states into a single string
        goal_state_str = "(AND \n"
        for item in goal:
            # extract the name and parameters from the dictionary
            name = item['name']
            params = " ".join(item['params'])
            goal_state_str += f"   ({name} {params}) \n" # append the predicate in the desired format
        goal_state_str += ")"
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        feedback_template = feedback_template.replace('{initial_state}', initial_state_str)
        feedback_template = feedback_template.replace('{goal_state}', goal_state_str)

        print(feedback_template)

        example = """START OF EXAMPLE:    
## OBJECTS
```
truck1 - the first truck at the Chicago depot
```

## INITIAL
```
(at truck1 chicago_depot): truck1 is at the chicago_depot
```

## GOAL
```
(AND
   (finalised house1) ; house 1 is done
)
```
END OF EXAMPLE
        """

        # prompt = "You are a PDDL expert and will be given the parts of a PDDL problem file to give feedback on. Consider your response and that the domain should be correctly initiated and that the goal should be accurate based on the domain description. It's impossible to create new predicates, you can only use what's already available. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, None, None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL task. Follow exact example syntax. End your response underneath the capitalized headers '## OBJECTS', '## INITIAL', and '## GOAL' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        objects = parse_objects(llm_feedback_response)
        initial = parse_initial(llm_feedback_response)
        goal = parse_goal(llm_feedback_response)

        return objects, initial, goal, llm_feedback_response

    def objects_feedback(
        self, 
        model: LLM_Chat, 
        problem_desc: str,
        feedback_template: str, 
        feedback_type: str, 
        type_hierarchy: dict[str,str], 
        predicates: list[Predicate],
        objects: dict[str,str],
        llm_response: str
        ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into objects format"""
        
        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        
        example = """START OF EXAMPLE:
## OUTPUT
{
    'truck1': 'vehicle'
}
END OF EXAMPLE
"""

        # prompt =  "You are a PDDL problem file feedback analyist that must run the checklist on the given object instances. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        # print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL object instances. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            objects = convert_to_dict(parts[1].strip())
        else:
            objects = {}

        return objects, llm_feedback_response

    def initial_state_feedback(
        self, 
        model: LLM_Chat, 
        problem_desc: str,
        feedback_template: str, 
        feedback_type: str, 
        type_hierarchy: dict[str,str], 
        predicates: list[Predicate],
        objects: dict[str,str],
        initial: list[dict[str,str]],
        llm_response: str
        ) -> tuple[str, str]:
        """Makes LLM call using feedback prompt, then parses it into format"""
        
        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        inner_str = [f"({state['name']} {' '.join(state['params'])})" for state in initial] # The main part of each predicate
        full_str = [f"(not {inner})" if state["neg"] else inner for state, inner in zip(initial, inner_str)] # Add the `not` if needed
        initial_state_str = "\n".join(full_str) # Combine the states into a single string
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        feedback_template = feedback_template.replace('{initial_state}', initial_state_str)
        
        example = """START OF EXAMPLE:
## OUTPUT
{
    '(at truck1 chicago_depot)': 'truck1 is at the chicago_depot',
}
END OF EXAMPLE
"""

        # prompt =  "You are a PDDL problem file feedback analyist that must run the checklist on the given initial state. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        # print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL initial state. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            initial = convert_to_dict(parts[1].strip())
        else:
            initial = {}

        initial = "\n".join(initial.keys())

        return initial, llm_feedback_response

    def goal_state_feedback(
        self, 
        model: LLM_Chat, 
        problem_desc: str,
        domain_desc: str, 
        feedback_template: str, 
        feedback_type: str, 
        type_hierarchy: dict[str,str], 
        predicates: list[Predicate],
        objects: dict[str,str],
        initial: list[dict[str,str]],
        goal: list[dict[str,str]],
        llm_response: str
        ) -> tuple[str, str]:
        """Makes LLM call using feedback prompt, then parses it into format"""
        
        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        inner_str = [f"({state['name']} {' '.join(state['params'])})" for state in initial] # The main part of each predicate
        full_str = [f"(not {inner})" if state["neg"] else inner for state, inner in zip(initial, inner_str)] # Add the `not` if needed
        initial_state_str = "\n".join(full_str) # Combine the states into a single string
        goal_state_str = "(AND \n"
        for item in goal:
            # extract the name and parameters from the dictionary
            name = item['name']
            params = " ".join(item['params'])
            goal_state_str += f"   ({name} {params}) \n" # append the predicate in the desired format
        goal_state_str += ")"
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        feedback_template = feedback_template.replace('{initial_state}', initial_state_str)
        feedback_template = feedback_template.replace('{initial_state}', goal_state_str)
        
        example = """START OF EXAMPLE:
## OUTPUT
(AND
   (finalised house1) ; house 1 is done
)
END OF EXAMPLE
"""

        # prompt =  "You are a PDDL problem file feedback analyist that must run the checklist on the given goal state. " + INSTRUCTION
        # prompt += feedback_template

        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        elif feedback_type.lower() == "validator":
            feedback_msg = feedback_template
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        # print("FEEDBACK MESSAGE:\n", feedback_msg)

        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return None, feedback_msg
        else:
            feedback_msg = "## Feedback" + feedback_msg + "\nRe-iterate an updated version of the PDDL goal state. Your end response must format in a Python dictionary under header '## OUTPUT' as so:\n\n" + example
            feedback_msg += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': feedback_msg}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        parts = llm_response.split('## OUTPUT', 1)
        if len(parts) > 1:
            goal = parts[1].strip()
        else:
            goal = "Could not parse answer. Here is original LLM response:\n" + llm_response

        return goal, llm_feedback_response


    def human_feedback(self, info: str):

        print("START OF INFO\n", info)
        print("\nEND OF INFO\n\n")
        contents = []
        print("Provide feedback (or 'no feedback'). End with ctrl+d.\n")
        while True:
            try:
                line = input()
            except EOFError:
                break
            contents.append(line)
        resp = "\n".join(contents)

        if resp.strip().lower() == "no feedback":
            return "no feedback" # No feedback
        
        return resp
