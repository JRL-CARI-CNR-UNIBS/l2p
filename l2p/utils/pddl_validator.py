from ..llm_builder import LLM_Chat

def validate_unsupported_keywords(llm_response: str, unsupported_keywords: list[str]):
    """
    Checks whether PDDL model uses unsupported logic keywords
    """
    for key in unsupported_keywords:
        if f'{key}' in llm_response:
            feedback_msg = f'The precondition or effect contains the keyword '

