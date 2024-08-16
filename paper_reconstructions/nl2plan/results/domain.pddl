(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
arm - mechanism
location - object
table - location
   )

   (:predicates 
(at ?o - object ?l - location) ;  true if the object ?o (a vehicle or a worker) is at the location ?l
(clear ?b - block) ;  true if the block ?b is clear and can be picked up
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
    (clear ?b) ; The block is clear
    (empty ?a) ; The arm is empty
)
   :effect
(and
    (not (clear ?b)) ; The block is no longer clear
    (not (at ?b ?t)) ; The block is no longer at the table
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
    (at ?t ?table) ; The table is the correct location
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (at ?b ?t) ; The block is now on the table
    (clear ?b) ; The block is now clear
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
    (not (holding ?a ?b2)) ; The arm is not holding the bottom block
)
   :effect
(and
    (not (holding ?a ?b1)) ; The arm is no longer holding the top block
    (not (clear ?b2)) ; The bottom block is no longer clear
    (on ?b1 ?b2) ; The top block is now on top of the bottom block
    (clear ?b1) ; The top block is clear after being stacked
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
)
)
)