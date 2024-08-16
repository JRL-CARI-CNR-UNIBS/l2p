(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
arm - tool
table - location
   )

   (:predicates 
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
(on_table ?b - block ?t - table) ;  true if the block ?b is on the table ?t
(clear ?b - block) ;  true if the block ?b is clear (not covered by another block)
(on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
   )

(:action check_clear
   :parameters (
?b - block
?a - arm
   )
   :precondition
(and
    (at ?a ?table) ; The arm is at the table
    (clear ?b) ; The block must be clear
)
   :effect
(and
    (not (clear ?b)) ; The block is no longer clear after the check
)
)

(:action pickup
   :parameters (
?b - block
?a - arm
?t - table
   )
   :precondition
(and
    (at ?b ?t) ; The block is on the table
    (clear ?b) ; The block is clear
    (empty ?a) ; The arm is empty
)
   :effect
(and
    (not (at ?b ?t)) ; The block is no longer on the table
    (not (clear ?b)) ; The block is no longer clear
    (holding ?a ?b) ; The arm is now holding the block
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
    (not (on_table ?b ?t)) ; The block is not already on the table
    (clear ?t) ; The table must be clear to place the block
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (on_table ?b ?t) ; The block is now on the table
    (clear ?b) ; The block is now clear
    (not (clear ?t)) ; The table is no longer clear after placing the block
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
    (on_table ?b2) ; The bottom block is on the table
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the top block
    (not (clear ?b2)) ; The bottom block is no longer clear
    (on ?b1 ?b2) ; The top block is now on top of the bottom block
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
    (not (holding ?a ?b1)) ; The arm is empty
    (clear ?b1) ; The top block is clear
    (on ?b1 ?b2) ; The top block is on the bottom block
)
   :effect
(and
    (holding ?a ?b1) ; The arm is now holding the top block
    (not (on ?b1 ?b2)) ; The top block is no longer on the bottom block
    (clear ?b2) ; The bottom block is now clear
)
)
)