(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
arm - physical_object
table - physical_object
location - object
   )

   (:predicates 
(at ?o - object ?l - location) ;  true if the object ?o (an arm or a block) is at the location ?l
(clear ?b - block) ;  true if the block ?b is not obstructed by any other object
(empty ?a - arm) ;  true if the arm ?a is not holding any block
(holding ?a - arm ?b - block) ;  true if the arm ?a is currently holding the block ?b
(on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
   )

(:action pickup
   :parameters (
?a - arm
?b - block
?t - table
   )
   :precondition
(and
    (at ?a ?t) ; The arm is at the table
    (clear ?b) ; The block is clear (not obstructed)
    (empty ?a) ; The arm is empty (not holding any block)
)
   :effect
(and
    (not (clear ?b)) ; The block is no longer clear after being picked up
    (not (empty ?a)) ; The arm is no longer empty after picking up the block
    (holding ?a ?b) ; The arm is now holding the block
    (not (at ?b ?t)) ; The block is no longer at the table
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
    (at ?a ?t) ; The arm is at the table
    (holding ?a ?b) ; The arm is holding the block
    (clear ?b) ; The block is clear (not obstructed)
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (on ?b ?t) ; The block is now on the table
    (clear ?t) ; The table is clear (assuming it can hold the block)
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
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the top block
    (not (clear ?b2)) ; The bottom block is no longer clear
    (on ?b1 ?b2) ; The top block is now on top of the bottom block
    (empty ?a) ; The arm is now empty
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
    (empty ?a) ; The arm must be empty
    (clear ?b1) ; The top block must be clear
    (on ?b1 ?b2) ; The top block must be on the bottom block
    (at ?a ?l) ; The arm must be at some location ?l
)
   :effect
(and
    (holding ?a ?b1) ; The arm is now holding the top block
    (not (on ?b1 ?b2)) ; The top block is no longer on the bottom block
    (clear ?b2) ; The bottom block is now clear
    (not (empty ?a)) ; The arm is no longer empty
)
)
)