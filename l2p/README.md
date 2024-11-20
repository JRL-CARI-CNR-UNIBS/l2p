# L2P
Official documentation for use of functions can be found on our website: [LINK](https://sliding.toys/mystic-square/8-puzzle/daily/) The L2P classes can be split up into the following:
## domain_builder.py
This class is responsible for generating PDDL domain information via LLMs. Currently, it supports generating the following (crossed out are supported features):
- [x] `Types` (PDDL 1.2 and later: Supports defining types for objects, helping to organize and restrict possible object assignments in actions.)
- [x] `Predicates` (PDDL 1.2 and later: Basic predicates represent the truth values of propositions that can be true or false in the planning domain.)
- [x] `Natural Language actions` (A modern extension of PDDL, leveraging LLMs to describe actions in natural language form, then automatically converting them into formal PDDL actions.)
- [x] `Basic Full PDDL action` (PDDL 1.2 and later: Defines a complete action with parameters, preconditions, and effects in a formal, syntactically correct manner.)
- [x] `Basic Action Parameters` (PDDL 1.2 and later: Defines parameters within actions, specifying which objects or types are involved in each action.)
- [x] `Basic Action Preconditions` (PDDL 1.2 and later: Specifies the conditions that must hold for an action to be applicable.)
- [x] `Basic Action Effects` (PDDL 1.2 and later: Defines what changes in the state when an action is executed, including fluent changes and predicate truth values.)
- [x] `Full set of Basic PDDL actions` (PDDL 1.2 and later: Includes the complete specification of actions in the domain, potentially including actions for movement, object manipulation, and other typical operations.)
- [ ] `Action Costs` (PDDL 2.1 and later: Allows for specifying the cost of actions, useful in metric or cost-based planning, to optimize goals like minimizing time or resources.)
- [ ] `Temporal Constraints` (PDDL 2.2 and later: Supports defining temporal planning features, such as specifying time constraints or durations for actions and relationships between actions over time.)
- [ ] `Disjunctive Preconditions` (PDDL 2.2 and later: Allows for specifying alternative conditions in preconditions using "or", enabling more flexibility in defining the requirements for actions.)
- [ ] `Derived Predicates` (PDDL 2.1 and later: Defines predicates whose truth value is inferred by the planner from other predicates, typically expressed through rules or axioms.)
- [ ] `Non-deterministic Actions` (PDDL 2.2 and later: Defines actions that have multiple possible outcomes, useful for modeling uncertainty or probabilistic events in planning.)
- [ ] `Conditional effects / Quantifications` (PDDL 2.2 and later: Supports conditional effects, where the result of an action depends on certain conditions being met, and also the use of quantifiers like "forall" or "exists" to express more complex relationships in action effects.)
- [ ] `Mutex Relations` (PDDL 2.2 and later: Defines mutual exclusion relations between actions or predicates, stating that certain actions or predicates cannot hold true simultaneously in the planning domain.)


## task_builder.py
This class is responsible for generating PDDL task information via LLMs. Currently, it supports generating the following (crossed out are supported features):
- [x] `Objects` (PDDL 1.2 and later: Defines the objects involved in the problem, which can be assigned types and used in actions or predicates.)
- [x] `Initial State` (PDDL 1.2 and later: Specifies the initial configuration of the world, including the truth values of predicates and the state of objects at the beginning of the plan.)
- [x] `Goal State` (PDDL 1.2 and later: Defines the conditions or set of predicates that must be satisfied at the end of the planning process to achieve the goal.)
- [ ] `Action Instances` (PDDL 1.2 and later: Specifies instances of actions that have been applied in the planning process, typically based on the initial state and the actions available in the domain.)
- [ ] `Quantified Goals` (PDDL 2.2 and later: Allows for defining goals that involve quantification, such as "there exists an object x such that..." or "for all objects y, the following must hold...")
- [ ] `Negative Goals` (PDDL 2.2 and later: Defines goals where the state of certain predicates must be false at the goal state.)
- [ ] `Metric Optimization` (PDDL 2.1 and later: Supports optimization of a given metric in the problem, such as minimizing or maximizing a resource like time, cost, or energy used.)
- [ ] `Timeline Constraints` (PDDL 2.2 and later: Involves specifying constraints that govern the sequence or timing of events, useful for temporal planning.)
- [ ] `Temporal Goal Definition` (PDDL 2.2 and later: Defines goals that must be achieved within a certain temporal window or sequence of actions, useful for time-sensitive plans.)
- [ ] `Preferences` (PDDL 3.0 and later: Allows for defining soft goals or preferences that are desirable but not mandatory for achieving the goal state.)
- [ ] `Resource Constraints` (PDDL 2.1 and later: Defines limitations on resources, such as the number of robots available or the amount of fuel in the system.)
- [ ] `Durative Goals` (PDDL 2.2 and later: Specifies goals that span over time, requiring a series of actions to be completed in a specific duration or sequence.)
- [ ] `Conditional Goals` (PDDL 2.2 and later: Defines goals that depend on certain conditions being met, offering more flexibility in expressing complex planning scenarios.)

## feedback_builder.py
This class is responsible for returning feedback information via LLMs. It contains the following functions:

### General Functions:
- **get_feedback()**: Retrieves the type of feedback the user requests and returns the feedback message. Takes in either `"human"`, `"llm"`, or `"hybrid"`, which is both.
- **human_feedback()**: Enables the user to provide human-in-the-loop feedback.

### Domain Feedback:
- **type_feedback()**: Returns feedback on revised types.
- **type_hierarchy_feedback()**: Returns feedback on revised type hierarchy.
- **nl_action_feedback()**: Returns feedback on revised natural language actions.
- **pddl_action_feedback()**: Returns feedback on revised PDDL actions.
- **parameter_feedback()**: Returns feedback on revised parameters of a specific action.
- **precondition_feedback()**: Returns feedback on revised preconditions of a specific action.
- **effect_feedback()**: Returns feedback on revised effects of a specific action.
- **predicate_feedback()**: Returns feedback on revised predicates.
- **task_feedback()**: Returns complete feedback on the revised PDDL task.

### Problem Feedback:
- **objects_feedback()**: Returns feedback on revised objects.
- **initial_state_feedback()**: Returns feedback on revised initial states.
- **goal_state_feedback()**: Returns feedback on revised goal states.

---

## prompt_builder.py
This class is responsible for generating prompt templates for LLMs. Users can utilize this class to assemble their prompts in an organized manner and swap between different prompts. Specifically, it consists of:

### Components:
- **Roles**: Provides an overview task for the LLM to generate.
- **Technique**: Specifies a prompting technique (e.g., CoT, ZPD, etc.).
- **Example**: Provides an in-context example for the LLM to follow.
- **Task**: Defines placeholders. Users should observe examples and extraction functions for proper information extraction.

## llm_builder.py
This class is responsible for extracting LLMs
**API keys**
L2P requires access to an LLM. L2P provides support for OpenAI's GPT-series models. To configure these, provide the necessary API-key in an environment variable.

**OpenAI**
```
export OPENAI_API_KEY='YOUR-KEY' # e.g. OPENAI_API_KEY='sk-123456'
```

Refer to [here](https://platform.openai.com/docs/quickstart) for more information.

**HuggingFace**

Additionally, we have included support for using Huggingface models. One can set up their environment like so:
```
parser = argparse.ArgumentParser(description="Define Parameters")
parser.add_argument('-test_dataset', action='store_true')
parser.add_argument("--temp", type=float, default=0.01, help = "temperature for sampling")
parser.add_argument("--max_len", type=int, default=4e3, help = "max number of tokens in answer")
parser.add_argument("--num_sample", type=int, default=1, help = "number of answers to sample")
parser.add_argument("--model_path", type=str, default="/path/to/model", help = "path to llm")
args = parser.parse_args()    

huggingface_model = HUGGING_FACE(model_path=args.model_path, max_tokens=args.max_len, temperature=args.temp)
```

**llm_builder.py** contains an abstract class and method for implementing any model classes in the case of other third-party LLM uses.

## utils
This parent folder contains other tools necessary for L2P. They consist of:

### pddl_parser.py
Contains tools to parse L2P information extraction

### pddl_types.py
Contains PDDL types 'Action' and 'Predicate' as well as Domain, Problem, and Plan details. These can be utilized to help organize builder method calls easier.

### pddl_validator.py
Contains tools to validate PDDL specifications and returns error feedback.

### pddl_planner.py
For ease of use, our library contains submodule [FastDownward](https://github.com/aibasel/downward/tree/308812cf7315fe896dbcd319493277d82aa36bd2). Fast Downward is a domain-independent classical planning system that users can run their PDDL domain and problem files on. The motivation is that the majority of papers involving PDDL-LLM usage uses this library as their planner.

This planner can be run like:
```python
from l2p.utils.pddl_planner import FastDownward

planner = FastDownward()   
domain = "path/to/domain.pddl"
problem = "path/to/problem.pddl"

pass, plan = planner.run_fast_downward(domain, problem)
```
