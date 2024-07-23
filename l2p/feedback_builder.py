from .llm_builder import LLM_Chat
from .utils.pddl_parser import convert_to_dict, parse_action, parse_new_predicates, parse_objects, parse_initial, parse_goal
from .utils.pddl_types import Action, Predicate
import json

def format_json_output(data):
        return json.dumps(data, indent=4)

class Feedback_Builder:

    def type_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            feedback_template: str, 
            types: dict[str,str], 
            llm_response: str=""
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into type format"""

        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPES:\n" + format_json_output(types)
        prompt = "ROLE:\nYou are a PDDL expert and your task is to evaluate if a set of types are correct and sufficent for modelling a given domain. If it is, respond with 'no feedback'. If it isn't, provide your thoughts on how to correct the types. Don't model the available actions, but just the types of objects to be used.'\n\n"
        prompt += feedback_template

        # print("PROMPT FEEDBACK:\n", prompt)

        llm_feedback = model.get_output(prompt=prompt)

        print("LLM FEEDBACK:\n", llm_feedback)

        if 'no feedback' in llm_feedback.lower() or len(llm_feedback.strip()) == 0:
            return None, llm_feedback
        else:
            llm_feedback = "## Feedback" + llm_feedback + "\nRe-iterate an updated version of the types. End your final answer starting with '## OUTPUT'."
            llm_feedback += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': llm_feedback}
        ]

        llm_feedback_response = model.get_output(messages=messages)
        
        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        new_types = convert_to_dict(llm_response=llm_feedback_response)
        return new_types, llm_feedback_response

    def type_hierarchy_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str,
            feedback_template: str, 
            type_hierarchy: dict[str,str], 
            llm_response: str=""
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into type hierarchy format"""

        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPE HIERARCHY:\n" + format_json_output(type_hierarchy)
        prompt = "ROLE:\nYour task is to evaluate if a type hierarchy is defined in the best way. You can suggest changing of the structure or adding types. Note that everything is always supposed to be a subtype of the 'object' class. You shouldn't suggest any new types except those needed for organisation of the provided types. If the hierarchy is optimal, respond with 'No feedback'.\n\n"
        prompt += feedback_template

        # print("PROMPT FEEDBACK:\n", prompt)
        
        llm_feedback = model.get_output(prompt=prompt)

        # print("LLM FEEDBACK:\n", llm_feedback)

        if 'no feedback' in llm_feedback.lower() or len(llm_feedback.strip()) == 0:
            return None, llm_feedback
        else:
            llm_feedback = "## Feedback" + llm_feedback + "\nRe-iterate an updated version of the type hierarchy. End your final answer starting with '## OUTPUT'."
            llm_feedback += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': llm_feedback}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)
        
        type_hierarchy = convert_to_dict(llm_response=llm_feedback_response)
        return type_hierarchy, llm_feedback_response

    def nl_action_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            nl_actions: dict[str,str], 
            llm_response: str=""
            ) -> tuple[dict[str,str], str]:
        """Makes LLM call using feedback prompt, then parses it into format"""

        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL NATURAL LANGUAGE ACTIONS:\n" + format_json_output(nl_actions)
        prompt = "ROLE:\nYou will be given a set of which are used for a PDDL domain. You should evaluate if they make up all the actions necessary for the given domain, or if any new actions have to be created or existing actions removed. Describe your thought process and comments your suggestions. Focus only on the actions currently, predicates will be specified at a later date. Be careful not to over complicate any domains, adding actions simply for complexity/completeness when they're not needed for the domain should be avoided, we're making a simplified model. Any actions involving 'checking' should not be considered an action, because that is a predicate in PDDL. Only suggest actions that cannot be described by a predicate. Keep the essentials. If the actions are well defined, simply respond with 'No feedback'.\n\n"
        prompt += feedback_template

        # print("PROMPT FEEDBACK:\n", prompt)
        
        llm_feedback = model.get_output(prompt=prompt)

        # print("LLM FEEDBACK:\n", llm_feedback)

        if 'no feedback' in llm_feedback.lower() or len(llm_feedback.strip()) == 0:
            return None, llm_feedback
        else:
            llm_feedback = "## Feedback" + llm_feedback + "\nRe-iterate an updated version of the natural language actions. Make sure it is not a nested dictionary. End your final answer starting with '## OUTPUT'."
            llm_feedback += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': llm_feedback}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        new_nl_actions = convert_to_dict(llm_response=llm_feedback_response)
        return new_nl_actions, llm_feedback_response



    def pddl_action_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            action: Action, 
            predicates: list[Predicate], 
            types: dict[str,str], 
            llm_response: str=""
            ) -> tuple[Action, list[Predicate], str]:
        """Makes LLM call using feedback prompt, then parses it into format"""

        predicate_str = ", ".join([pred["clean"].replace(":", " ; ") for pred in predicates])
        param_str = ", ".join([f"{name} - {type}" for name, type in action['parameters'].items()]) 
        
        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPES:\n" + format_json_output(types)
        feedback_template += "\n\nPDDL LIST OF PREDICATES: " + predicate_str
        feedback_template += "\n\nPDDL ACTION NAME: " + action['name']
        feedback_template += "\n\nPDDL ACTION PARAMETERS:" + param_str
        feedback_template += "\n\nPDDL ACTION PRECONDITIONS:\n" + action['preconditions']
        feedback_template += "\n\nPDDL ACTION EFFECTS:\n" + action['effects']

        example = """START OF EXAMPLE:
### Action Parameters
Okay, so we'll need the same parameters as last time, but we still need to clearly specify them again:
```
- ?v - vehicle: The vehicle travelling
- ?from - location: The location travelling from
- ?to - location: The location travelling to
```

### Action Preconditions
Now, we'll make the change to check both directions of the "connected" predicate as to create more robust PDDL.
```
(and
    (at ?v ?from) ; The vehicle is at the starting location
    (or (connected ?from ?to) (connected ?to ?from)) ; A road exists between the locations
)
```

### Action Effects
These are the exact same as above, but they need to be reiterated:
```
(and
    (not (at ?v ?from)) ; ?v is no longer at ?from
    (at ?v ?to) ; ?v is now instead at ?to
)
```

### New Predicates
These are the same as before:
```
- (at ?o - object ?l - location): true if the object ?o (a vehicle or a worker) is at the location ?l
- (connected ?l1 - location ?l2 - location): true if a road exists between ?l1 and ?l2 allowing vehicle travel between them.
``` 
END OF EXAMPLE
        """
    
        prompt = "You are a PDDL expert and will be given a set of PDDL actions to correct and give feedback and advice on. Consider not only if the actions are technically correct, but also whether they are defined following good standards such as flexibility and clarity. Overly specifying types by use of 'is-type' predicates should generally be avoided. Remember that the preconditions should make sure that only valid objects are passed to the action, we can't assume anything except the provided types. Don't assume any restrictions beyond those specified by the domain itself.  Don't unnecessarily overcomplicate the actions. Note that creating new options isn't possible. If the action is well defined, respond with 'no feedback'.\n\n"
        prompt += feedback_template

        #  print("PROMPT:\n", prompt)

        llm_feedback = model.get_output(prompt=prompt)

        #  print("LLM FEEDBACK:\n", llm_feedback)

        if 'no feedback' in llm_feedback.lower() or len(llm_feedback.strip()) == 0:
            return None, None, llm_feedback
        else:
            llm_feedback = "## Feedback" + llm_feedback + "\nRe-iterate an updated version of the PDDL action. Your end response must format the Action Parameters, Preconditions, and Effects, and New Predicates with ''' ''' comment blocks in PDDL as so:\n\n" + example
            llm_feedback += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': llm_feedback}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        action = parse_action(llm_response=llm_feedback_response, action_name=action['name'])
        new_predicates = parse_new_predicates(llm_feedback_response)
        new_predicates = [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]] # remove re-defined predicates

        return action, new_predicates, llm_feedback_response


    def predicate_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into predicate format"""
        pass


    def parameter_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into precondition format"""
        pass


    def precondition_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into precondition format"""
        pass


    def effects_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into effects format"""
        pass




    def task_feedback(
            self, 
            model: LLM_Chat, 
            problem_desc: str, 
            feedback_template: str, 
            predicates: list[Predicate], 
            types: dict[str,str], 
            objects: dict[str,str], 
            initial: str, 
            goal: str, 
            llm_response: str=""
            ) -> tuple[dict[str,str],str,str,str]:
        
        predicate_str = ", ".join([pred["clean"].replace(":", " ; ") for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        
        feedback_template += "\n\nPROBLEM DESCRIPTION:\n" + problem_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPES:\n" + format_json_output(types)
        feedback_template += "\n\nPDDL LIST OF PREDICATES: " + predicate_str
        feedback_template += "\n\nPDDL OBJECTS: " + objects_str
        feedback_template += "\n\nPDDL INITIAL STATE:" + initial
        feedback_template += "\n\nPDDL GOAL STATE:\n" + goal

        example = """START OF EXAMPLE:    
## Object Instances
The feedback suggested to use more trucks, but this would be wrong since the domain only specifies "A couple". So, we stick with the two trucks.
```
truck1 - the first truck at the Chicago depot
truck2 - the second truck at the Chicago depot
chicago_depot - location: The Chicago depot
house1 - The first house to build
house2 - The second house to build
house3 - The third house to build
jamie - administrator: The administrator Jamie
emma - general_worker: The first worker, Emma
bob - general_worker: The second worker, Bob
```

## Initial
Let's start by specifying where everyone is again. This time, we  make sure to include Bob.
```
(at truck1 chicago_depot): truck1 is at the chicago_depot
(at truck2 chicago_depot): truck2 is at the chicago_depot
(at jamie chicago_depot): Jamie is at the depot
(at emma chicago_depot): Emma is at the depot
(at bob chicago_depot): Bob is at the depot
(connected house1 chicago_depot): house1 is connected to the chicago_depot
(connected house2 chicago_depot): house2 is connected to the chicago_depot
(connected house3 chicago_depot): house3 is connected to the chicago_depot
(connected chicago_depot house1): chicago_depot is connected to house1
(connected chicago_depot house2): chicago_depot is connected to house2
(connected chicago_depot house3): chicago_depot is connected to house3
```

## Goal
For the goal, we remove the "truck1" location predicate, but still check that all the houses are finalised. 
```
(AND ; all the following should be done
   (finalised house1) ; house 1 is done
   (finalised house2) ; house 2 is done
   (finalised house3) ; house 3 is done
)
```
END OF EXAMPLE
        """

        prompt = "You are a PDDL expert and will be given the parts of a PDDL problem file to give feedback on. Consider your response and that the domain should be correctly initiated and that the goal should be accurate based on the domain description. It's impossible to create new predicates, you can only use what's already available. Think through your feedback step by step. If the action is well defined, respond with 'No feedback'.\n\n"
        prompt += feedback_template

        #  print("PROMPT:\n", prompt)

        llm_feedback = model.get_output(prompt=prompt)

        #  print("LLM FEEDBACK:\n", llm_feedback)

        if 'no feedback' in llm_feedback.lower() or len(llm_feedback.strip()) == 0:
            return None, None, None, llm_feedback
        else:
            llm_feedback = "## Feedback" + llm_feedback + "\nRe-iterate an updated version of the PDDL task. End your response underneath the headers '## Object Instances', '## Initial', and '## Goal' as so:\n\n" + example
            llm_feedback += "\n\n## Response\n"
        
        messages = [
            {'role': 'assistant', 'content': llm_response},
            {'role': 'user', 'content': llm_feedback}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        objects = parse_objects(llm_feedback_response)
        initial = parse_initial(llm_feedback_response)
        goal = parse_goal(llm_feedback_response)

        return objects, initial, goal, llm_feedback_response


    def objects_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into objects format"""
        pass


    def initial_state_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into format"""
        pass


    def goal_state_feedback(self, model: LLM_Chat, domain_desc: str, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into format"""
        pass




    def human_feedback(self, info: str):
        print(info)
        contents = []
        print("Provide feedback (or 'None'). End with ctrl+d.\n")
        while True:
            try:
                line = input()
            except EOFError:
                break
            contents.append(line)
        resp = "\n".join(contents)

        if resp.strip().lower() == "none":
            return None # No feedback

        return resp

