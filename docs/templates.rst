Templates
================
It is **highly** recommended to use the base templates to properly extract LLM output into the designated Python formats from these methods.

Below are some examples of the base prompt structure that should be used in this library with your customised prompt. More details of each methods' prompt structure is found in **l2p/data/prompt_templates**

Domain Extraction Prompts Example
-------------------------------------------------------
This is an example found in `l2p/data/prompt_templates/action_construction/extract_action`

**Role**: ::

    End your final answers underneath the headers: '### Action Parameters,' '### Action Preconditions,' '### Action Effects,' and '### New Predicates' with ''' ''' comment blocks in PDDL as so:

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

**Task**: ::

    Here is the task:

    ## Domain
    {domain_desc}

    ## Types
    {types}

    ## Future actions to be used later:
    {action_list}

    ## Action name
    {action_name}

    ## Action description
    {action_desc}

    # Available predicates
    {predicates}


Task Extraction Prompts Example
---------------------------------------------------

This is an example found in `l2p/data/prompt_templates/task_extraction/extract_task`

**Role**: ::

    Do not, under any circumstance, output the answers in PDDL format. Final answer must be in the following format at the end:
    ## OBJECTS
    ```
    truck1 - truck
    ```

    ## INITIAL
    ```
    (at truck1 chicago_depot): truck1 is at the chicago_depot
    ```

    ## GOAL
    ```
    (AND ; all the following should be done
    (finalised house1) ; house 1 is done
    )
    ```

**Task**: ::

    ## Domain
    {domain_desc}

    ## Types
    {types}

    ## Predicates
    {predicates}

    ## Problem description
    {problem_desc}