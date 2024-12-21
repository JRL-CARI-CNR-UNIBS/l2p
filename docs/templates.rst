Templates
================
It is **highly** recommended to use the base templates to properly extract LLM output into the designated Python formats from these methods.

Below are some examples of the base prompt structure that should be used in this library with your customized prompt using the `PromptBuilder` class. More details of each methods' prompt structure is found in **l2p/templates**.

Domain Extraction Prompts Example
-------------------------------------------------------
This is an example using `l2p/templates/domain_templates/extract_pddl_action.txt`

.. code-block:: python
    :linenos:

    from l2p.prompt_builder import PromptBuilder
    from l2p.utils import load_file

    # LOAD BASE FORMAT TEMPLATE
    template_path = "templates/domain_templates/extract_pddl_action.txt"
    base_template = load_file(template_path)

    role_desc = (
        "You are a PDDL action constructor. Your job is to take the task given in natural language and convert it into the following format:\n\n"
        f"{base_template}" # INSERT BASE TEMPLATE
    )
                
    tech_desc = """
    You should follow a Chain of Thought (CoT) process for constructing a PDDL action before outputting the final answer:

    1. Construct action parameters and create necessary predicates to produce action preconditions in PDDL
    2. Construct necessary predicates to produce action effects in PDDL
    3. Check for inconsistencies and/or requirements and state the errors if there are any. If there are errors, generate a suggestion response (i.e. deleting, modifying, adding types)
    4. Re-iterate parameters, preconditions, effects, and predicates
    """
                
    task_desc = f"""
    ## Domain
    {domain_desc}

    ## Available types
    {types}

    ## Future actions to be implemented later
    {action_list}

    ## Action name (to implement now)
    {action_name}

    ## Action description (corresponding action description)
    {action_desc}

    ## Available predicates
    {predicates}
    """
                
    action_construction_prompt = PromptBuilder(role=role_desc, technique=tech_desc, task=task_desc)

    print(action_construction_prompt.generate_prompt())


The following is the output: ::
    
    [ROLE]: You are a PDDL action constructor. Your job is to take the task given in natural language and convert it into the following format:

    End your final answers underneath the headers: '### Action Parameters,' '### Action Preconditions,' '### Action Effects,' and '### New Predicates' with ''' ''' comment blocks in PDDL as so:

    ### Action Parameters
    ```
    - ?t - type: 'parameter_description'
    ```

    ### Action Preconditions
    ```
    (and
        (predicate_name ?t1 ?t2) ; COMMENT DESCRIPTION
    )
    ```

    ### Action Effects
    ```
    (and
        (predicate_name ?t1 ?t2) ; COMMENT DESCRIPTION
    )
    ```

    ### New Predicates
    ```
    - (predicate_name ?t1 - type_1 ?t2 - type_2): 'predicate_description'
    ``` 

    If there are no new predicates created, keep an empty space enclosed ```  ``` with the '### New Predicates' header.

    ------------------------------------------------
    [TECHNIQUE]: 
    You should follow a Chain of Thought (CoT) process for constructing a PDDL action before outputting the final answer:

    1. Construct action parameters and create necessary predicates to produce action preconditions in PDDL
    2. Construct necessary predicates to produce action effects in PDDL
    3. Check for inconsistencies and/or requirements and state the errors if there are any. If there are errors, generate a suggestion response (i.e. deleting, modifying, adding types)
    4. Re-iterate parameters, preconditions, effects, and predicates

    ------------------------------------------------
    [TASK]:
    Here is the task to solve:

    ## Domain
    {domain_desc}

    ## Available types
    {types}

    ## Future actions to be implemented later
    {action_list}

    ## Action name (to implement now)
    {action_name}

    ## Action description (corresponding action description)
    {action_desc}

    ## Available predicates
    {predicates}


Users have the flexibility to customize all aspects of their prompts, with the exception of the provided base template. While users can include few-shot examples to guide the LLM, the base template must remain intact during inference.