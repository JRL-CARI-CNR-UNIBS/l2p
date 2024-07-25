(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
arm - physical_object
table - location
   )

   (:predicates 
(empty ?a - arm) ;  true if the arm ?a is empty
(on_table ?b - block ?t - table) ;  true if the block ?b is on the table ?t
(clear ?b - block) ;  true if the block ?b is clear (not covered by another block)
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
   )

(:action pickup
   :parameters (
?a - arm
?b - block
?t - table
   )
   :precondition
(and
    (empty ?a) ; The arm is empty
    (on_table ?b ?t) ; The block is on the table
    (clear ?b) ; The block is clear (not covered by another block)
)
   :effect
(and
    (not (empty ?a)) ; The arm is no longer empty
    (not (on_table ?b ?t)) ; The block is no longer on the table
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
    (on_table ?b ?t) ; The block is on the table
    (clear ?b) ; The block is clear
    (empty ?a) ; The arm is empty
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (on_table ?b ?t) ; The block is still on the table
    (clear ?b) ; The block remains clear
    (empty ?a) ; The arm becomes empty
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
    (on_table ?b2 ?t) ; The bottom block is on the table
    (not (equal ?b1 ?b2)) ; The top block and bottom block must be different
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the top block
    (not (clear ?b2)) ; The bottom block is no longer clear
    (on_table ?b1 ?b2) ; The top block is now on top of the bottom block
    (clear ?b1) ; The top block is clear (no block on top of it)
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
    (holding ?b2) ; The bottom block is being held by the arm
)
   :effect
(and
    (not (holding ?b2)) ; The arm is no longer holding the bottom block
    (holding ?b1) ; The arm is now holding the top block
    (not (clear ?b2)) ; The bottom block is no longer clear (since it has a block on top of it)
)
)
)