# L2P
The L2P classes can be split up into the following:

## domain_builder.py
This class is responsible for generating PDDL domain information via LLMs. It contains the following functions:

- **extract_type()**: extracts domain types
- **extract_type_hierarchy()**: organises domain types into hierarchy
- **extract_nl_actions()**: extract actions in natural language
- **extract_pddl_action()**: extracts an action specification (parameters, preconditions, effects) and predicates
- **extract_pddl_actions()**: extracts all action models
- **extract_parameters()**: extracts PDDL parameters for specific action
- **extract_preconditions()**: extracts PDDL preconditions for specific action
- **extract_effects()**: extracts PDDL effects for specific action
- **extract_predicates()**: extracts PDDL predicates

It also contains delete, set, get, and generate functions:
- **delete_type()**: deletes specific type in current model
- **delete_nl_action()**: deletes specific NL action in current model
- **delete_pddl_action()**: deletes specific PDDL action in current model
- **delete_predicate()**: deletes specific predicate in current model
- **get/set_type()**: retrieves/sets type in current model
- **get/set_type_hierarchy()**: retrieves/sets type_hierarchy in current model
- **get/set_nl_actions()**: retrieves/sets NL actions in current model
- **get/set_pddl_action()**: retrieves/sets PDDL actions in current model
- **get/set_predicate()**: retrieves/sets predicates current model
- **generate_domain()**: generates markup of PDDL domain given key info from current model

## task_builder.py
This class is responsible for generating PDDL task information via LLMs. It contains the following functions:
- **extract_objects()**: extracts PDDL object types from specific action
- **extract_initial_state()**: extracts PDDL initial states from specific action
- **extract_goal_state()**: extracts PDDL goal states from specific action
- **extract_task()**: extract whole PDDL task specification
- **extract_nl_conditions()**: extracts NL initial and goal states

It also contains delete, set, get, and generate functions:
- **delete_objects()**: deletes specific object from current model
- **delete_initial()**: deletes specific initial state from current model
- **delete_goal()**: deletes specific goal state from current model
- **get/set_objects()**: retrieves/sets objects
- **get/set_initial()**: retrieves/sets initial state
- **get/set_goal()**: retrieves/sets goal state
- **generate_task()**: generates markup of PDDL task given key info from current model

## feedback_builder.py
This class is responsible for returning feedback information via LLMs. It contains the following functions:
- **get_feedback()**: retrieves the type of feedback user requests and returns feedack message; takes in either "human" "llm" or "hybrid" which is both
- **human_feedback()**: enables user to provide human-in-the-loop feedback

These are the domain feedback:
- **type_feedback()**: returns feedback revised types
- **type_hierarchy_feedback()**: returns feedback revised type hierarchy
- **nl_action_feedback()**: returns feedback revised NL actions
- **pddl_action_feedback()**: returns feedback revised PDDL action
- **parameter_feedback()**: returns feedback revised parameters of specific action
- **precondition_feedback()**: returns feedback revised preconditions of specific action
- **effect_feedback()**: returns feedback revised effects of specific action
- **predicate_feedback()**: returns feedback revised predicates
- **task_feedback()**: returns whole feedback revised PDDL task

These are the problem feedback
- **objects_feedback()**: returns feedback revised objects
- **initial_state_feedback()**: returns feedback revised initial states
- **goal_state_feedback()**: returns feedback revised goal states

## prompt_builder.py
This class is responsible for generating prompt templates for LLMs. Users can utilise this class to assemble their prompts in an organised manner; capable of swapping different prompts. Specifically, it consists of:
- **Roles**: this is meant to give an overview task for LLM to generate
- **Technique**: this is meant to give a prompting technique (i.e CoT, ZPD, etc.)
- **Example**: this is meant to give in-context example for LLM to follow.
- **Task**: this is meant for placeholders. Users should observe examples and extraction functions for proper info extraction

## llm_builder.py
This class is responsible for extracting LLMs

## utils
This parent folder contains other tools necessary for L2P. They consist of:

### pddl_parser.py
Contains tools to parse L2P information extraction

### pddl_types.py
Contains PDDL types 'Action' and 'Predicate'

### pddl validator.py
Contains tools to validate PDDL specifications and returns error feedback.