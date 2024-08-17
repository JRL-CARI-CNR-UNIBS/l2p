"""
This file contains collection of functions for PDDL feedback generation purposes
"""

from .llm_builder import LLM_Chat
from .domain_builder import DomainBuilder
from .task_builder import TaskBuilder
from .utils.pddl_parser import convert_to_dict, parse_action, parse_new_predicates, parse_objects, parse_initial, parse_goal, parse_params, format_dict, format_predicates
from .utils.pddl_types import Action, Predicate
from collections import OrderedDict
import json

domain_builder = DomainBuilder()
task_builder = TaskBuilder()

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

        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)
    
        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is the feedback you outputted:\n{fb_msg}"
                f"\n\nFollow the same syntax format as the original output in your answer:\n{llm_response}"
            )

            types, _ = domain_builder.extract_type(model, domain_desc, prompt)

        return types, fb_msg

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
        
        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)
    
        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is the feedback you outputted:\n{fb_msg}"
                f"\n\nFollow the same syntax format as the original output in your answer:\n{llm_response}"
            )
            type_hierarchy, _ = domain_builder.extract_type_hierarchy(model, domain_desc, prompt)

        return type_hierarchy, fb_msg

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

        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)
    
        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is the feedback you outputted:\n{fb_msg}"
                f"\n\nFollow the same syntax format as the original output in your answer:\n{llm_response}"
            )
            nl_actions, _ = domain_builder.extract_type_hierarchy(model, domain_desc, prompt)

        return nl_actions, fb_msg

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

        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)
    
        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is the feedback you outputted:\n{fb_msg}"
                f"\n\nFollow the same syntax format as the original output in your answer:\n{llm_response}"
            )

            action, predicates, _ = domain_builder.extract_pddl_action(model, domain_desc, prompt, action['name'])
        return action, predicates, fb_msg

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
            ) -> tuple[bool, str]:
        """Makes LLM call using feedback prompt, then parses it into precondition format"""

        param_str = "\n".join([f"{name} - {type}" for name, type in parameter.items()])
        
        feedback_template = feedback_template.replace('{domain_desc}', domain_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{action_name}', action_name)
        feedback_template = feedback_template.replace('{action_desc}', action_desc)
        feedback_template = feedback_template.replace('{parameters}', param_str)

        return self.get_feedback(model, feedback_template, feedback_type, llm_response)

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
            ) -> tuple[bool, str]:
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

        return self.get_feedback(model, feedback_template, feedback_type, llm_response)

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
            ) -> tuple[bool, str]:
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

        return self.get_feedback(model, feedback_template, feedback_type, llm_response)


    def task_feedback(
            self, 
            model: LLM_Chat, 
            problem_desc: str, 
            feedback_template: str, 
            feedback_type: str,
            predicates: list[Predicate], 
            types: dict[str,str], 
            objects: dict[str,str]=None, 
            initial: list[dict[str,str]]=None, 
            goal: list[dict[str,str]]=None, 
            llm_response: str=""
            ) -> tuple[bool,str]:
        
        predicate_str = format_predicates(predicates)
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()]) if objects else ""
        initial_state_str = task_builder.format_initial(initial) if initial else ""
        goal_state_str = task_builder.format_goal(objects) if goal else ""
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(types))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        feedback_template = feedback_template.replace('{initial_state}', initial_state_str)
        feedback_template = feedback_template.replace('{goal_state}', goal_state_str)
    
        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)
    
        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is the feedback you outputted:\n{fb_msg}"
                f"\n\nFollow the same syntax format as the original output in your answer:\n{llm_response}"
            )

            objects, initial, goal, _ = task_builder.extract_task(model, problem_desc, prompt)

        return objects, initial, goal, fb_msg


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
        ) -> tuple[bool, str]:
        """Makes LLM call using feedback prompt, then parses it into objects format"""
        
        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)

        return self.get_feedback(model, feedback_template, feedback_type, llm_response)

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
        ) -> tuple[bool, str]:
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

        return self.get_feedback(model, feedback_template, feedback_type, llm_response)

    def goal_state_feedback(
        self, 
        model: LLM_Chat, 
        problem_desc: str,
        feedback_template: str, 
        feedback_type: str, 
        type_hierarchy: dict[str,str], 
        predicates: list[Predicate],
        objects: dict[str,str],
        initial: list[dict[str,str]],
        goal: list[dict[str,str]],
        llm_response: str
        ) -> list[dict[str,str]]:
        """Makes LLM call using feedback prompt, then parses it into format"""
        
        predicate_str = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in predicates])
        objects_str = "\n".join([f"{obj} - {type}" for obj, type in objects.items()])
        initial_state_str = task_builder.format_initial(initial)
        goal_state_str = task_builder.format_goal(goal)
        
        feedback_template = feedback_template.replace('{problem_desc}', problem_desc)
        feedback_template = feedback_template.replace('{llm_response}', llm_response)
        feedback_template = feedback_template.replace('{types}', format_dict(type_hierarchy))
        feedback_template = feedback_template.replace('{predicates}', predicate_str)
        feedback_template = feedback_template.replace('{objects}', objects_str)
        feedback_template = feedback_template.replace('{initial_state}', initial_state_str)
        feedback_template = feedback_template.replace('{initial_state}', goal_state_str)

        no_fb, fb_msg = self.get_feedback(model, feedback_template, feedback_type, llm_response)

        if not no_fb:
            prompt = (
                f"\n\nYou now are revising your answer using feedback. Here is your original output:\n{llm_response}"
                f"\n\nHere is the feedback you outputted:\n{fb_msg}"
                "\n\nFollow the same syntax format as the original output in your answer."
            )
            goal, _ = task_builder.extract_goal_state(model, problem_desc, prompt)

        return goal


    def human_feedback(self, info: str):
        print("START OF INFO\n", info)
        print("\nEND OF INFO\n\n")
        contents = []
        print("Provide feedback (or type 'done' to finish):\n")
        while True:
            line = input()
            if line.strip().lower() == "done":
                break
            contents.append(line)
        resp = "\n".join(contents)

        if resp.strip().lower() == "no feedback":
            return "no feedback"  # No feedback
        
        return resp
    
    def get_feedback(
            self, 
            model: LLM_Chat, 
            feedback_template: str, 
            feedback_type: str, 
            llm_response: str
            ) -> tuple[bool, str]:
        
        if feedback_type.lower() == "human":
            feedback_msg = self.human_feedback(llm_response)
        elif feedback_type.lower() == "llm":
            feedback_msg = model.get_output(prompt=feedback_template)
        elif feedback_type.lower() == "hybrid":
            feedback_msg = model.get_output(prompt=feedback_template)
            response = "\nORIGINAL LLM OUTPUT:\n" + llm_response + "\nFEEDBACK:\n" + feedback_msg
            feedback_msg.replace("no feedback".lower(), "")
            feedback_msg += self.human_feedback(response)
        else:
            raise ValueError("Invalid feedback_type. Expected 'human', 'llm', or 'hybrid'.")
        
        if 'no feedback' in feedback_msg.lower() or len(feedback_msg.strip()) == 0:
            return True, feedback_msg
        
        return False, feedback_msg
