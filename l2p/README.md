# L2P

Below are the in-depth usage of L2P. It is **highly** recommended to use the base template to properly extract LLM output into the designated Python formats from these methods.

## DomainBuilder

### *class* l2p.DomainBuilder(types: dict[str, str] = None, type_hierarchy: dict[str, str] = None, predicates: list[Predicate] = None, nl_actions: dict[str, str] = None, pddl_actions: list[Action] = None)

#### \_\_init_\_(types: dict[str, str] = None, type_hierarchy: dict[str, str] = None, predicates: list[Predicate] = None, nl_actions: dict[str, str] = None, pddl_actions: list[Action] = None)

Initializes a domain builder object

* **Parameters:**
  * **types** (*dict* *[**str* *,**str* *]*) – types dictionary with name: description key-value pair
  * **type_hierarchy** (*dict* *[**str* *,**str* *]*) – type hierarchy dictionary
  * **predicates** (*list* *[**Predicate* *]*) – list of Predicate objects
  * **nl_actions** (*dict* *[**str* *,**str* *]*) – dictionary of extracted actions, where the keys are action names and values are action descriptions
  * **pddl_actions** (*list* *[**Action* *]*) – list of Action objects

#### action_desc(action: Action) → str

Helper function to format individual action descriptions

#### action_descs(actions) → str

Helper function to combine all action descriptions

#### delete_nl_action(name: str)

Deletes specific NL action from current model

#### delete_pddl_action(name: str)

Deletes specific PDDL action from current model

#### delete_predicate(name: str)

Deletes specific predicate from current model

#### delete_type(name: str)

Deletes specific type from current model

#### extract_effects(model: LLM, domain_desc: str, prompt_template: str, action_name: str, action_desc: str, params: list[str] = None, precondition: str = None, predicates: list[Predicate] = None, max_retries: int = 3) → tuple[str, list[Predicate], str]

Extracts effects from single action description via LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **action_name** (*str*) – action name
  * **action_desc** (*str*) – action description
  * **params** (*list* *[**str* *]*) – list of parameters from action
  * **precondition** (*str*) – PDDL format of preconditions
  * **predicates** (*list* *[**Predicate* *]*) – list of current predicates in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  PDDL format of effects
  new_predicates (list[Predicate]): a list of new predicates
  llm_response (str): the raw string LLM response
* **Return type:**
  effects (str)

#### extract_nl_actions(model: LLM, domain_desc: str, prompt_template: str, types: dict[str, str] = None, nl_actions: dict[str, str] = None, max_retries: int = 3) → tuple[dict[str, str], str]

Extract actions in natural language given domain description using LLM.

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **nl_actions** (*dict* *[**str* *,* *str* *]*) – NL actions currently in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  a dictionary of extracted actions {action name: action description}
  llm_response (str): the raw string LLM response
* **Return type:**
  nl_actions (dict[str, str])

#### extract_parameters(model: LLM, domain_desc: str, prompt_template: str, action_name: str, action_desc: str, types: dict[str, str] = None, max_retries: int = 3) → tuple[OrderedDict, list, str]

Extracts parameters from single action description via LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **action_name** (*str*) – action name
  * **action_desc** (*str*) – action description
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  ordered list of parameters
  param_raw (list()): list of raw parameters
  llm_response (str): the raw string LLM response
* **Return type:**
  param (OrderedDict)

#### extract_pddl_action(model: LLM, domain_desc: str, prompt_template: str, action_name: str, action_desc: str = None, action_list: dict[str, str] = None, predicates: list[Predicate] = None, types: dict[str, str] = None, max_retries: int = 3) → tuple[Action, list[Predicate], str]

Extract an action and predicates from a given action description using LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – action construction prompt
  * **action_name** (*str*) – action name
  * **action_desc** (*str*) – action description
  * **action_list** (*dict* *[**str* *,**str* *]*) – dictionary of other actions to be translated
  * **predicates** (*list* *[**Predicate* *]*) – list of predicates in current model
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  constructed action class
  new_predicates (list[Predicate]): a list of new predicates
  llm_response (str): the raw string LLM response
* **Return type:**
  action (Action)

#### extract_pddl_actions(model: LLM, domain_desc: str, prompt_template: str, nl_actions: dict[str, str] = None, predicates: list[Predicate] = None, types: dict[str, str] = None) → tuple[list[Action], list[Predicate], str]

Extract all actions from a given action description using LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – action construction prompt
  * **nl_actions** (*dict* *[**str* *,* *str* *]*) – NL actions currently in model
  * **predicates** (*list* *[**Predicate* *]*) – list of predicates
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
* **Returns:**
  constructed action class
  new_predicates (list[Predicate]): a list of new predicates
  llm_response (str): the raw string LLM response
* **Return type:**
  action (Action)

#### extract_preconditions(model: LLM, domain_desc: str, prompt_template: str, action_name: str, action_desc: str, params: list[str] = None, predicates: list[Predicate] = None, max_retries: int = 3) → tuple[str, list[Predicate], str]

Extracts preconditions from single action description via LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **action_name** (*str*) – action name
  * **action_desc** (*str*) – action description
  * **params** (*list* *[**str* *]*) – list of parameters from action
  * **predicates** (*list* *[**Predicate* *]*) – list of current predicates in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  PDDL format of preconditions
  new_predicates (list[Predicate]): a list of new predicates
  llm_response (str): the raw string LLM response
* **Return type:**
  preconditions (str)

#### extract_predicates(model: LLM, domain_desc: str, prompt_template: str, types: dict[str, str] = None, predicates: list[Predicate] = None, nl_actions: dict[str, str] = None, max_retries: int = 3) → tuple[list[Predicate], str]

Extracts predicates via LLM

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – list of current predicates in model
  * **nl_actions** (*dict* *[**str* *,* *str* *]*) – NL actions currently in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  a list of new predicates
  llm_response (str): the raw string LLM response
* **Return type:**
  new_predicates (list[Predicate])

#### extract_type(model: LLM, domain_desc: str, prompt_template: str, types: dict[str, str] = None, max_retries: int = 3) → tuple[dict[str, str], str]

Extracts types with domain given

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  dictionary of types with (name:description) pair
  llm_response (str): the raw string LLM response
* **Return type:**
  type_dict (dict[str,str])

#### extract_type_hierarchy(model: LLM, domain_desc: str, prompt_template: str, types: dict[str, str] = None, max_retries: int = 3) → tuple[dict[str, str], str]

Extracts type hierarchy from types list and domain given

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  dictionary of type hierarchy
  llm_response (str): the raw string LLM response
* **Return type:**
  type_hierarchy (dict[str,str])

#### format_predicates(predicates: list[Predicate]) → str

Helper function that formats predicate list into string

#### generate_domain(domain: str, types: str, predicates: str, actions: list[Action], requirements: list[str]) → str

Generates PDDL domain from given information

* **Parameters:**
  * **domain** (*str*) – domain name
  * **types** (*str*) – domain types
  * **predicates** (*str*) – domain predicates
  * **actions** (*list* *[**Action* *]*) – domain actions
  * **requirements** (*list* *[**str* *]*) – domain requirements
* **Returns:**
  PDDL domain
* **Return type:**
  desc (str)

#### get_nl_actions()

Returns natural language actions from current model

#### get_pddl_actions()

Returns PDDL actions from current model

#### get_predicates()

Returns predicates from current model

#### get_type_hierarchy()

Returns type hierarchy from current model

#### get_types()

Returns types from current model

#### set_nl_actions(nl_actions: dict[str, str])

Sets NL actions for current model

#### set_pddl_action(pddl_action: Action)

Appends a PDDL action for current model

#### set_predicate(predicate: Predicate)

Appends a predicate for current model

#### set_type_hierarchy(type_hierarchy: dict[str, str])

Sets type hierarchy for current model

#### set_types(types: dict[str, str])

Sets types for current model

## TaskBuilder

### *class* l2p.TaskBuilder(objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None)

#### \_\_init_\_(objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None)

Initializes a task builder object

* **Parameters:**
  * **objects** (*dict* *[**str* *,**str* *]*) – current dictionary of task objects in model
  * **initial** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current initial states in model
  * **goal** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current goal states in model

#### delete_goal_state(state: dict[str, str])

#### delete_initial_state(state: dict[str, str])

#### delete_objects(name)

#### extract_goal_state(model: LLM, problem_desc: str, prompt_template: str, types: dict[str, str] = None, predicates: list[Predicate] = None, objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None, max_retries: int = 3) → tuple[list[dict[str, str]], str]

Extracts goal states with given predicates, objects, and states in current model

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **problem_desc** (*str*) – problem description
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template class
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – current list of predicates in model
  * **objects** (*dict* *[**str* *,**str* *]*) – current dictionary of task objects in model
  * **initial** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current initial states in model
  * **goal** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current goal states in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  list of dictionary of goal states [{predicate,params,neg}]
  llm_response (str): the raw string LLM response
* **Return type:**
  goal (list[dict[str,str]])

#### extract_initial_state(model: LLM, problem_desc: str, prompt_template: str, types: dict[str, str] = None, predicates: list[Predicate] = None, objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None, max_retries: int = 3) → tuple[list[dict[str, str]], str]

Extracts initial states with given predicates, objects, and states in current model

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **problem_desc** (*str*) – problem description
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template class
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – current list of predicates in model
  * **objects** (*dict* *[**str* *,**str* *]*) – current dictionary of task objects in model
  * **initial** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current initial states in model
  * **goal** (*list* *[**dict* *[**str* *,**str* *]* *]*) – current goal states in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  list of dictionary of initial states [{predicate,params,neg}]
  llm_response (str): the raw string LLM response
* **Return type:**
  initial (list[dict[str,str]])

#### extract_nl_conditions(model: LLM, problem_desc: str, prompt_template: [PromptBuilder](#l2p.PromptBuilder), types: dict[str, str] = None, predicates: list[Predicate] = None, actions: list[Action] = None, objects: dict[str, str] = None, max_retries: int = 3) → str

Extracts initial and goal states in natural language

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **problem_desc** (*str*) – problem description
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template class
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – current list of predicates in model
  * **actions** (*list* *[**Action* *]*) – current list of Action instances in model
  * **objects** (*dict* *[**str* *,**str* *]*) – current dictionary of task objects in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  the raw string LLM response
* **Return type:**
  llm_response (str)

#### extract_objects(model: LLM, problem_desc: str, prompt_template: str, types: dict[str, str] = None, predicates: list[Predicate] = None, max_retries: int = 3) → tuple[dict[str, str], str]

Extracts objects with given predicates in current model

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **problem_desc** (*str*) – problem description
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template class
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – list of predicates in current model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  dictionary of object types {name:description}
  llm_response (str): the raw string LLM response
* **Return type:**
  objects (dict[str,str])

#### extract_task(model: LLM, problem_desc: str, prompt_template: str, types: dict[str, str] = None, predicates: list[Predicate] = None, actions: list[Action] = None, max_retries: int = 3) → tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]], str]

Extracts whole task specification in current model

* **Parameters:**
  * **model** (*LLM*) – LLM
  * **problem_desc** (*str*) – problem description
  * **domain_desc** (*str*) – domain description
  * **prompt_template** (*str*) – prompt template class
  * **types** (*dict* *[**str* *,**str* *]*) – current types in model
  * **predicates** (*list* *[**Predicate* *]*) – current list of predicates in model
  * **actions** (*list* *[**Action* *]*) – current list of Action instances in model
  * **max_retries** (*int*) – max # of retries if failure occurs
* **Returns:**
  dictionary of object types {name:description}
  initial (list[dict[str,str]]): list of dictionary of initial states [{predicate,params,neg}]
  goal (list[dict[str,str]]): list of dictionary of goal states [{predicate,params,neg}]
  llm_response (str): the raw string LLM response
* **Return type:**
  objects (dict[str,str])

#### format_action(actions: list[Action]) → str

#### format_goal(goal_states: list[dict[str, str]]) → str

#### format_initial(initial_states: list[dict[str, str]]) → str

#### format_objects(objects: dict[str, str]) → str

#### generate_task(domain: str, problem: str, objects: str, initial: str, goal: str)

#### get_initial() → dict[str, str]

#### get_objects() → str

#### set_goal(goal: str)

#### set_initial(initial: dict[str, str])

#### set_objects(objects: dict[str, str])

## FeedbackBuilder

### *class* l2p.FeedbackBuilder

#### effect_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', parameter: OrderedDict = None, preconditions: str = None, effects: str = None, action_name: str = None, action_desc: str = None, types: dict[str, str] = None, predicates: list[Predicate] = None) → tuple[str, list[Predicate], str]

Makes LLM call using feedback prompt, then parses it into effects format

#### get_feedback(model: LLM, feedback_template: str, feedback_type: str, llm_response: str) → tuple[bool, str]

This retrieves the type of feedback user requests and returns feedack message.
feedback_type takes in either “human” “llm” or “hybrid” which it both

#### goal_state_feedback(model: LLM, problem_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', type_hierarchy: dict[str, str] = None, predicates: list[Predicate] = None, objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None) → tuple[list[dict[str, str]], str]

Makes LLM call using feedback prompt, then parses it into goal states format

#### human_feedback(info: str)

This enables human-in-the-loop feedback mechanism

#### initial_state_feedback(model: LLM, problem_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', type_hierarchy: dict[str, str] = None, predicates: list[Predicate] = None, objects: dict[str, str] = None, initial: list[dict[str, str]] = None) → tuple[list[dict[str, str]], str]

Makes LLM call using feedback prompt, then parses it into initial states format

#### nl_action_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', nl_actions: dict[str, str] = None, type_hierarchy: dict[str, str] = None) → tuple[dict[str, str], str]

Makes LLM call using feedback prompt, then parses it into nl_action format

#### objects_feedback(model: LLM, problem_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', type_hierarchy: dict[str, str] = None, predicates: list[Predicate] = None, objects: dict[str, str] = None) → tuple[dict[str, str], str]

Makes LLM call using feedback prompt, then parses it into objects format

#### parameter_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', parameter: OrderedDict = None, action_name: str = None, action_desc: str = None, types: dict[str, str] = None) → tuple[OrderedDict, OrderedDict, str]

Makes LLM call using feedback prompt, then parses it into parameter format

#### pddl_action_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', action: Action = None, predicates: list[Predicate] = None, types: dict[str, str] = None) → tuple[Action, list[Predicate], str]

Makes LLM call using feedback prompt, then parses it into action format

#### precondition_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', parameter: OrderedDict = None, preconditions: str = None, action_name: str = None, action_desc: str = None, types: dict[str, str] = None, predicates: list[Predicate] = None) → tuple[str, list[Predicate], str]

Makes LLM call using feedback prompt, then parses it into precondition format

#### predicate_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', types: dict[str, str] = None, predicates: list[Predicate] = None, nl_actions: dict[str, str] = None) → tuple[list[Predicate], str]

Makes LLM call using feedback prompt, then parses it into predicates format

#### task_feedback(model: LLM, problem_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', predicates: list[Predicate] = None, types: dict[str, str] = None, objects: dict[str, str] = None, initial: list[dict[str, str]] = None, goal: list[dict[str, str]] = None) → tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]], str]

Makes LLM call using feedback prompt, then parses it into object, initial, and goal format

#### type_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', types: dict[str, str] = None) → tuple[dict[str, str], str]

Makes LLM call using feedback prompt, then parses it into type format

#### type_hierarchy_feedback(model: LLM, domain_desc: str, llm_response: str, feedback_template: str, feedback_type: str = 'llm', type_hierarchy: dict[str, str] = None) → tuple[dict[str, str], str]

Makes LLM call using feedback prompt, then parses it into type hierarchy format

## PromptBuilder

### *class* l2p.PromptBuilder(role: str = None, technique: str = None, examples: list = [], task: str = None)

#### generate_prompt()

Generates the whole prompt in proper format

#### get_examples()

Returns list of n-examples of the prompt given

#### get_role()

Returns role of the prompt given

#### get_task()

Returns dynamic placeholder task prompt

#### get_technique()

Returns prompting technique of the prompt given

#### remove_examples(idx)

Removes specific index of example list

#### remove_role()

Removes role prompt

#### remove_task()

Removes dynamic placeholder task prompt

#### remove_technique()

Removes technique prompt

#### set_examples(example)

Appends a shot examples for LLM to follow

#### set_role(role)

Sets the role for the LLM to perform task

#### set_task(task)

Sets a task for the LLM by providing dynamic placeholders to generate and describe domain components.

The task parameter is a structured input that includes various elements to guide the LLM in understanding
and executing the task. The task may include descriptions, types, actions, and predicates that the LLM
will process to generate appropriate outputs.

Here is an example of a dynamic placeholder:
‘’’
## Domain
{domain_desc} - A placeholder for the description of the domain, explaining the context and purpose.
‘’’

* **Parameters:**
  **task** (*str*) – A structured string or template containing dynamic placeholders to specify the task.

#### set_technique(technique)

Sets the prompting technique for LLM to perform task
