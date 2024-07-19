from .llm_builder import LLM_Chat

class Feedback_Builder:

    def type_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            types: dict[str,str], 
            llm_response: str=None
            ) -> str:
        """Makes LLM call using feedback prompt, then parses it into type format"""

        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPES:\n" + str(types)
        prompt = "ROLE:\nYou are a PDDL expert and your task is to evaluate if a set of types are correct and sufficent for modelling a given domain. If it is, respond with 'no feedback'. If it isn't, provide your thoughts on how to correct the types. Don't model the available actions, but just the types of objects to be used.'\n\n"
        prompt += feedback_template

        # print("PROMPT FEEDBACK:\n", prompt)

        llm_feedback = model.get_output(prompt=prompt)

        return llm_feedback


    def type_hierarchy_feedback(
            self, 
            model: LLM_Chat, 
            domain_desc: str, 
            feedback_template: str, 
            type_hierarchy: dict[str,str], 
            llm_response: str=None
            ) -> str:
        """Makes LLM call using feedback prompt, then parses it into type hierarchy format"""

        feedback_template += "\n\nDOMAIN DESCRIPTION:\n" + domain_desc
        feedback_template += "\n\nORIGINAL LLM OUTPUT:\n" + llm_response
        feedback_template += "\n\nORIGINAL TYPE HIERARCHY:\n" + str(type_hierarchy)
        prompt = "ROLE:\nYour task is to evaluate if a type hierarchy is defined in the best way. You can suggest changing of the structure or adding types. If the hierarchy is optimal, respond with 'No feedback'. Note that everything is always supposed to be a subtype of the 'object' class. You shouldn't suggest any new types except those needed for organisation of the provided types.\n\n"
        prompt += feedback_template

        print("PROMPT FEEDBACK:\n", prompt)
        
        llm_feedback = model.get_output(prompt=prompt)

        return llm_feedback


    def nl_action_feedback(self, model: LLM_Chat, feedback_template: str, llm_response: str):
        """Makes LLM call using feedback prompt, then parses it into format"""
        pass


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

