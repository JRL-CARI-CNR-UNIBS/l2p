(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - object
arm - object
table - location
   )

   (:predicates 
(on_table ?b - block) ;  true if the block ?b is on the table
(clear ?b - block) ;  true if the block ?b has no other block on top of it
(arm_empty ?a - arm) ;  true if the arm ?a is not holding any block
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
(on ?b1 - block ?b2 - block) ;  true if the block ?b1 is on top of the block ?b2
   )

(:action pickup
   :parameters (
?b - block
?a - arm
   )
   :precondition
pddl
(and
    (on_table ?b) ; The block is on the table
    (clear ?b) ; The block is clear
    (arm_empty ?a) ; The arm is empty
)
   :effect
pddl
(and
    (not (on_table ?b)) ; The block is no longer on the table
    (not (arm_empty ?a)) ; The arm is no longer empty
    (holding ?a ?b) ; The arm is now holding the block
)
)

(:action putdown
   :parameters (
?a - arm
?b - block
   )
   :precondition
(and
    (holding ?a ?b) ; The arm is holding the block
)
   :effect
(and
    (on_table ?b) ; The block is now on the table
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (arm_empty ?a) ; The arm is now empty
    (clear ?b) ; The block is clear
)
)

(:action stack
   :parameters (
?a - arm
?b1 - block
?b2 - block
   )
   :precondition
(and
    (holding ?a ?b1) ; The arm is holding the block to be stacked
    (clear ?b2) ; The block on which the other block is being stacked is clear
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the block
    (on ?b1 ?b2) ; The block ?b1 is now on top of the block ?b2
    (not (clear ?b2)) ; The block ?b2 is no longer clear
    (arm_empty ?a) ; The arm is now empty
)
)

(:action unstack
   :parameters (

   )
   :precondition
(and
    (arm_empty ?a) ; The arm is empty
    (clear ?b1) ; The block ?b1 is clear
    (on ?b1 ?b2) ; The block ?b1 is on top of the block ?b2
)
   :effect
(and
    (not (arm_empty ?a)) ; The arm is no longer empty
    (holding ?a ?b1) ; The arm is now holding the block ?b1
    (not (on ?b1 ?b2)) ; The block ?b1 is no longer on top of the block ?b2
    (clear ?b2) ; The block ?b2 is now clear
)
)
)