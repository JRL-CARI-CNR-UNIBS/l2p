(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
table - physical_object
arm - tool
   )

   (:predicates 
(at ?b - block ?t - table) ;  true if the block ?b is on the table ?t
(clear ?b - block) ;  true if the block ?b is clear (not obstructed)
(empty ?a - arm) ;  true if the arm ?a is empty (not holding any block)
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
(on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
(exists ?b - block) ;  true if the block ?b exists in the environment
(checked ?b - block) ;  true if the block ?b has been checked
   )

(:action pickup
   :parameters (
?a - arm
?b - block
?t - table
   )
   :precondition
(and
    (at ?b ?t) ; The block is on the table
    (clear ?b) ; The block is clear (not obstructed)
    (empty ?a) ; The arm is empty (not holding any block)
)
   :effect
(and
    (not (at ?b ?t)) ; The block is no longer on the table
    (not (clear ?b)) ; The block is no longer clear (it is being held)
    (holding ?a ?b) ; The arm is now holding the block
    (empty ?a) ; The arm is still empty after the action
)
)

(:action putdown
   :parameters (
?a - arm
?b - block
?t - table
   )
   :precondition
(and
    (holding ?a ?b) ; The arm is holding the block
    (clear ?t) ; The table must be clear to put down the block
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (at ?b ?t) ; The block is now on the table
    (not (clear ?b)) ; The block is no longer clear after being placed
    (empty ?a) ; The arm is now empty
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
    (holding ?a ?b1) ; The arm is holding the top block
    (clear ?b2) ; The bottom block is clear
    (not (on ?b1 ?b2)) ; The top block is not already on the bottom block
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the top block
    (on ?b1 ?b2) ; The top block is now on the bottom block
    (not (clear ?b2)) ; The bottom block is no longer clear
    (clear ?b1) ; The top block is clear after being placed
)
)

(:action unstack
   :parameters (
?a - arm
?b1 - block
?b2 - block
   )
   :precondition
(and
    (empty ?a) ; The arm is empty
    (clear ?b1) ; The top block is clear
    (on ?b1 ?b2) ; The top block is on the bottom block
)
   :effect
(and
    (holding ?a ?b1) ; The arm is now holding the top block
    (not (on ?b1 ?b2)) ; The top block is no longer on the bottom block
    (clear ?b2) ; The bottom block is now clear
    (not (clear ?b1)) ; The top block is no longer clear
    (not (empty ?a)) ; The arm is no longer empty
)
)

(:action check_clear
   :parameters (
?a - arm
?b - block
   )
   :precondition
(and
    (exists ?b) ; The block must exist in the environment
    (clear ?b)   ; The block must be clear before checking
)
   :effect
(and
    (checked ?b) ; The block has been checked
    (clear ?b)   ; The block is now clear after being checked
)
)
)