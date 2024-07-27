(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - object
arm - object
table - object
   )

   (:predicates 
(clear ?b - block) ;  true if the block ?b has nothing on top of it
(empty ?a - arm) ;  true if the arm ?a is not holding any block
(on-table ?b - block) ;  true if the block ?b is on the table
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
(on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
   )

(:action pickup
   :parameters (
?a - arm
?b - block
   )
   :precondition
(and
    (clear ?b) ; The block ?b is clear
    (empty ?a) ; The arm ?a is empty
    (on-table ?b) ; The block ?b is on the table
)
   :effect
(and
    (holding ?a ?b) ; The arm ?a is holding the block ?b
    (not (on-table ?b)) ; The block ?b is no longer on the table
    (not (clear ?b)) ; The block ?b is no longer clear
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
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (on-table ?b) ; The block is now on the table
    (clear ?b) ; The block is now clear
    (empty ?a) ; The arm is now empty
)
)

(:action stack
   :parameters (
?a - arm
?b_top - block
?b_bottom - block
   )
   :precondition
(and
    (holding ?a ?b_top) ; The arm is holding the top block
    (clear ?b_bottom) ; The bottom block is clear
)
   :effect
(and
    (not (holding ?a ?b_top)) ; The arm is no longer holding the top block
    (on ?b_top ?b_bottom) ; The top block is now on top of the bottom block
    (not (clear ?b_bottom)) ; The bottom block is no longer clear
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
    (on ?b1 ?b2) ; ?b1 is on top of ?b2
)
   :effect
(and
    (holding ?a ?b1) ; The arm is holding the top block
    (not (on ?b1 ?b2)) ; ?b1 is no longer on top of ?b2
    (clear ?b2) ; The bottom block is clear
)
)
)