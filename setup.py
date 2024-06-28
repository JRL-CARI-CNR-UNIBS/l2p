"""
Activate virtual environment: source env/bin/activate

L2P Checklist

- [ ] Integrate action-construction architecture into work
    - [ ] Implement add_predicates
- [ ] Distribute each component into its separate class, let domain_builder be the coordinating class
- [ ] Implement auto-feedback checklist
- [ ] Implement LLM-generated feedback checklist
- [ ] Implement PDDL generator — parser to assemble everything together

- The action_construction pipeline consists of:
    - Action extraction loop
        - For each action description, construct singular action (parameter, precondition, effects) based on current predicts and put into a list
        - Update list of new predicates 
        - Prune unused predicates and types
    - Once all actions generated, add actions (iteratively) and predicates to PDDLGenerator

PDDLGenerator is essentially domain_builder / task_builder — CHANGE THINGS AROUND TO PERFORM SAME FUNCTION

- [ ] Implement add_type — run through 
- [ ] Implement add_action — run through whole pipeline

- [ ] Implement task_builder
    - [ ] extract_object
    - [ ] extract_initial_state
    - [ ] extract_goal_state
    - [ ] Implement get functions
    - [ ] Implement add functions — pipelines

- [ ] Implement external planner tool


"""

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements

# set up variables and constants
x, y, z = variables("x y z", types=["type_1"])
a, b, c = constants("a b c", type_="type_1")

# define predicates
p1 = Predicate("p1", x, y, z)
p2 = Predicate("p2", x, y)

# define actions
a1 = Action(
    "action-1",
    parameters=[x, y, z],
    precondition=p1(x, y, z) & ~p2(y, z),
    effect=p2(y, z)
)

# define the domain object.
requirements = [Requirements.STRIPS, Requirements.TYPING]
domain = Domain("my_domain",
                requirements=requirements,
                types={"type_1": None},
                constants=[a, b, c],
                predicates=[p1, p2],
                actions=[a1])

print(domain_to_string(domain))

"""
(define (domain my_domain)
    (:requirements :strips :typing)
    (:types type_1)
    (:constants a b c - type_1)
    (:predicates (p1 ?x - type_1 ?y - type_1 ?z - type_1)  (p2 ?x - type_1 ?y - type_1))
    (:action action-1
        :parameters (?x - type_1 ?y - type_1 ?z - type_1)
        :precondition (and (p1 ?x ?y ?z) (not (p2 ?y ?z)))
        :effect (p2 ?y ?z)
    )
)
"""

problem = Problem(
    "problem-1",
    domain=domain,
    requirements=requirements,
    objects=[a, b, c],
    init=[p1(a, b, c), ~p2(b, c)],
    goal=p2(b, c)
)
print(problem_to_string(problem))

"""
(define (problem problem-1)
    (:domain my_domain)
    (:requirements :strips :typing)
    (:objects a b c - type_1)
    (:init (not (p2 b c)) (p1 a b c))
    (:goal (p2 b c))
)
"""