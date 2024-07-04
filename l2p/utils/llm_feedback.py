from .pddl_output_utils import parse_new_predicates, parse_params, combine_blocks
from .pddl_types import Action, Predicate
from l2p.llm_builder import LLM_Chat


def type_get_llm_feedback(self, model: LLM_Chat, feedback_prompt: str):
    feedback_output = model.get_output(feedback_prompt)
    if "no feedback" in feedback_output.lower() or len(feedback_output.strip()) == 0:
        return None
    else:
        feedback_output = "## Feedback" + feedback_output + "\nStart with a \"## Response\" header, then re-iterate an updated version of the \"## Actions\" header as before."
        feedback_output += "\n\n## Response\n"
        return feedback_output
    

def hierarchy_get_llm_feedback(self, model: LLM_Chat, feedback_prompt: str):
    feedback_output = model.get_output(feedback_prompt)
    if "no feedback" in feedback_output.lower() or len(feedback_output.strip()) == 0:
        return None
    else:
        feedback_output = "## Feedback" + feedback_output + "\nStart with a \"## Response\" header, then respond with the entire hierarchy below a \"## Hierarchy\" header as before."
        feedback_output += "\n\n## Response\n"
        return feedback_output
    
def nl_action_get_llm_feedback(self, model: LLM_Chat, actions: dict[str, str], feedback_template: str) -> str | None:
    """
    Gets feedback on the extracted actions.

    Args:
        model (LLM_Chat): The LLM_Chat language model connection.
        actions (dict[str, str]): A dictionary of extracted actions, where the keys are action names and the values are action descriptions.
        feedback_template (str): The feedback template to use.

    Returns:
        str | None: The feedback on the extracted actions.
    """
    action_str = "\n".join([f"- {name}: {desc}" for name, desc in actions.items()])
    feedback_prompt = feedback_template.replace('{actions}', action_str)

    feedback = model.get_output(prompt=feedback_prompt)

    if "no feedback" in feedback.lower() or len(feedback.strip()) == 0:
        return None
    
    feedback = "## Feedback" + feedback + "\nStart with a \"## Response\" header, then go through all the actions, even those kept from before, under a \"## Actions\" header as before."
    feedback += "\n\n## Response\n"
    return feedback


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

        feedback = model.get_response(prompt=feedback_prompt).strip()
        if "no feedback" in feedback.lower() or len(feedback.strip()) == 0:
            return None
        
        return feedback