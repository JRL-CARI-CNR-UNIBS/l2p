from pddl.parser.domain import DomainParser
from textwrap import dedent

"""
PDDL parser does not catch
    - If there is a variable being used in action, but is missing in parameter
    - 
"""

def test_hierarchical_types() -> None:
    """Test correct parsing of hierarchical types (see https://github.com/AI-Planning/pddl/issues/70)."""
    domain_str = dedent(
        """
    (define (domain test_domain)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types arm block table - object)
    (:predicates (arm_empty ?a - arm)  (clear ?b - block)  (holding ?a - arm ?b - block)  (on ?b1 - block ?b2 - block)  (on_table ?b - block))
    (:action pickup
        :parameters (?a - arm ?b - block)
        :precondition (and (clear ?b) (on_table ?b) (arm_empty ?a))
        :effect (and (not (on_table ?b)) (not (clear ?b)) (not (arm_empty ?a)) (holding ?a ?b))
    )
     (:action putdown
        :parameters (?a - arm ?b - block)
        :precondition (holding ?a ?b)
        :effect (and (not (holding ?a ?b)) (arm_empty ?a) (on_table ?b) (clear ?b))
    )
     (:action stack
        :parameters (?a - arm ?b1 - block ?b2 - block)
        :precondition (and (holding ?a ?b1) (clear ?b2) (not (= ?b1 ?b2)))
        :effect (and (not (holding ?a ?b1)) (arm_empty ?a) (on ?b1 ?b2) (not (clear ?b2)) (clear ?b1))
    )
     (:action unstack
        :parameters (?a - arm ?b1 - block ?b2 - block)
        :precondition (and (clear ?b1) (on ?b1 ?b2) (arm_empty ?a) (not (= ?b1 ?b2)))
        :effect (and (holding ?a ?b1) (not (on ?b1 ?b2)) (clear ?b2) (not (clear ?b1)) (not (arm_empty ?a)))
    )
)
    """
    )
    
    domain = DomainParser()(domain_str)

    requirements = domain.requirements
    types = domain.types
    predicates = domain.predicates
    actions = domain.actions
    
    
    print(requirements, "\n")
    print(types, "\n")
    print(predicates, "\n")
    print(actions, "\n")
    
    
if __name__ == "__main__":
    test_hierarchical_types()