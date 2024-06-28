from .logger import Logger
from .pddl_output_utils import parse_new_predicates, parse_params, combine_blocks
from .pddl_types import Action, Predicate

def pddl_action_llm_feedback(self, model, feedback_template: str, llm_response: str, predicates: list[Predicate], new_predicates: list[Predicate]) -> str | None:
        all_predicates = predicates + [pred for pred in new_predicates if pred['name'] not in [p["name"] for p in predicates]]
        action_params = combine_blocks(llm_response.split("Parameters")[1].split("##")[0])
        action_preconditions = llm_response.split("Preconditions")[1].split("##")[0].split("```")[1].strip(" `\n")
        action_effects = llm_response.split("Effects")[1].split("##")[0].split("```")[-2].strip(" `\n")
        predicate_list = "\n".join([f"- {pred['name']}: {pred['desc']}" for pred in all_predicates])

        feedback_prompt = feedback_template.replace('{action_params}', action_params)
        feedback_prompt = feedback_prompt.replace('{action_preconditions}', action_preconditions)
        feedback_prompt = feedback_prompt.replace('{action_effects}', action_effects)
        feedback_prompt = feedback_prompt.replace('{predicate_list}', predicate_list)

        Logger.print("Requesting feedback from LLM", subsection=False)
        Logger.log("Feedback prompt:\n", feedback_prompt)
        feedback = model.get_response(prompt=feedback_prompt).strip()
        Logger.log("Received feedback:\n", feedback)
        if "no feedback" in feedback.lower() or len(feedback.strip()) == 0:
            Logger.print(f"No Received feedback:\n {feedback}")
            return None
        
        return feedback