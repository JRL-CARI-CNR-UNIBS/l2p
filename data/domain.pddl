(define (domain test_domain)
(:requirements
   :strips :typing :equality :negative-preconditions :disjunctive-preconditions
   :universal-preconditions :conditional-effects
)
   (:types 
block - object
arm - object
table - object
   )

   (:predicates 
(empty ?arm - object) ;  true if the arm ?arm is empty
(clear ?block - object) ;  true if the block ?block is clear
(on_table ?block - object ?table - object) ;  true if the block ?block is on the table ?table
   )

(:action pickup
   :parameters (
?arm - object
?block - object
?table - object
   )
   :precondition
(and
    (empty ?arm)
    (clear ?block)
    (on_table ?block ?table)
)
   :effect
(and
    (holding ?arm ?block)
    (not (on_table ?block ?table))
    (not (clear ?block))
)
)

(:action putdown
   :parameters (
?arm - arm
?block - block
?table - table
   )
   :precondition
(and
    (not (empty ?arm)) ; The arm is not empty
)
   :effect
(and
    (empty ?arm) ; The arm is now empty
    (on_table ?block ?table) ; The block is now on the table
    (clear ?block) ; The block is now clear
)
)

(:action stack
   :parameters (
?arm - object
?top - object
?bottom - object
?table - object
   )
   :precondition
(and
    (not (empty ?arm)) ; The arm is not empty
    (clear ?bottom) ; The bottom block is clear
)
   :effect
(and
    (empty ?arm) ; The arm is now empty
    (on ?top ?bottom) ; The top block is now on top of the bottom block
    (not (clear ?bottom)) ; The bottom block is no longer clear
)
)

(:action unstack
   :parameters (
?arm - object
?top - block
?bottom - block
   )
   :precondition
(and
    (empty ?arm) ; The arm is empty
    (clear ?top) ; The top block is clear
)
   :effect
(and
    (holding ?arm ?top) ; The arm is now holding the top block
    (not (on ?top ?bottom)) ; The top block is no longer on top of the bottom block
    (clear ?bottom) ; The bottom block is clear
)
)
)