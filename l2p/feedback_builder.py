from .prompt_builder import PromptBuilder
from .llm_builder import LLM_Chat
from .utils.pddl_parser import convert_to_dict
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
            llm_response: str=None
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
            {'role': 'user', 'content': llm_feedback},
            {'role': 'assistant', 'content': llm_response}
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
            llm_response: str=None
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
            {'role': 'user', 'content': llm_feedback},
            {'role': 'assistant', 'content': llm_response}
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
            llm_response: str=None
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
            {'role': 'user', 'content': llm_feedback},
            {'role': 'assistant', 'content': llm_response}
        ]

        llm_feedback_response = model.get_output(messages=messages)

        # print("\n\nLLM FEEDBACK RESPONSE:\n", llm_feedback_response)

        new_nl_actions = convert_to_dict(llm_response=llm_feedback_response)
        return new_nl_actions, llm_feedback_response



    def pddl_action_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into format"""
        pass


    def predicate_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into predicate format"""
        pass


    def precondition_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into precondition format"""
        pass


    def effects_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into effects format"""
        pass




    def task_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        pass


    def objects_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into objects format"""
        pass


    def initial_state_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into format"""
        pass


    def goal_state_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
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

