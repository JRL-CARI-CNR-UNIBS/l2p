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
(holding ?b - block) ;  true if the arm is holding the block ?b
(on-table ?b - block) ;  true if the block ?b is on the table
(clear ?b - block) ;  true if the block ?b is clear and not stacked on another block
(empty ) ;  true if the arm is empty and not holding any block
(on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
   )

(:action pickup
   :parameters (
?b - block
   )
   :precondition
(and
    (on-table ?b) ; The block is on the table
    (clear ?b) ; The block is clear
    (empty) ; The arm is empty
)
   :effect
(and
    (holding ?b) ; The arm is holding the block
    (not (on-table ?b)) ; The block is no longer on the table
    (not (clear ?b)) ; The block is no longer clear
)
)

(:action putdown
   :parameters (
?b - block
   )
   :precondition
(and
    (holding ?b) ; The arm is holding the block ?b
)
   :effect
(and
    (not (holding ?b)) ; The arm is no longer holding the block ?b
    (on-table ?b) ; The block ?b is now on the table
    (clear ?b) ; The block ?b is now clear
)
)

(:action stack
   :parameters (
?b1 - block
?b2 - block
   )
   :precondition
(and
    (holding ?b1) ; The arm is holding the top block
    (clear ?b2) ; The bottom block is clear
)
   :effect
(and
    (not (holding ?b1)) ; The arm is no longer holding the top block
    (on ?b1 ?b2) ; The top block is on top of the bottom block
    (not (clear ?b2)) ; The bottom block is no longer clear
)
)

(:action unstack
   :parameters (
?b1 - block
?b2 - block
   )
   :precondition
(and
    (empty) ; The arm is empty
    (clear ?b1) ; The top block is clear
    (on ?b1 ?b2) ; The top block is on top of the bottom block
)
   :effect
(and
    (holding ?b1) ; The arm is holding the top block
    (not (on ?b1 ?b2)) ; The top block is no longer on top of the bottom block
    (clear ?b2) ; The bottom block is clear
)
)
)