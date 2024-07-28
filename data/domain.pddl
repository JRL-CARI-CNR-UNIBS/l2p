(define (domain test_domain)
(:requirements
  :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
)
   (:types 
block - physical_object
arm - physical_object
table - physical_object
   )

   (:predicates 
(on_table ?b - block ?t - table) ;  true if the block ?b is on the table ?t
(clear ?b - block) ;  true if the block ?b is clear (not obstructed)
(empty ?a - arm) ;  true if the arm ?a is empty (not holding anything)
(holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
(at ?a - arm ?t - table) ;  true if the arm ?a is at the table ?t
(on ?b_top - block ?b_bottom - block) ;  true if the block ?b_top is on top of the block ?b_bottom
   )

(:action pickup
   :parameters (
?a - arm
?b - block
?t - table
   )
   :precondition
(and
    (on_table ?b ?t) ; The block is on the table
    (clear ?b)       ; The block is clear (not obstructed)
    (empty ?a)       ; The arm is empty (not holding anything)
    (at ?a ?t)       ; The arm is at the table
)
   :effect
(and
    (not (on_table ?b ?t)) ; The block is no longer on the table
    (not (clear ?b))       ; The block is no longer clear (it is now being held)
    (holding ?a ?b)        ; The arm is now holding the block
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
    (holding ?a ?b) ; The arm is currently holding the block
    (at ?a ?t) ; The arm is at the table
    (clear ?b) ; The block is clear (not obstructed)
    (on_table ?b ?t) ; The block is not already on the table
)
   :effect
(and
    (not (holding ?a ?b)) ; The arm is no longer holding the block
    (on_table ?b ?t) ; The block is now on the table
    (clear ?b) ; The block remains clear after being put down
    (empty ?a) ; The arm is now empty
)
)

(:action stack
   :parameters (
?a - arm
?b_top - block
?b_bottom - block
?t - table
   )
   :precondition
(and
    (holding ?a ?b_top) ; The arm is holding the top block
    (clear ?b_bottom)    ; The bottom block is clear (not obstructed)
    (at ?a ?t)           ; The arm is at the table
)
   :effect
(and
    (not (holding ?a ?b_top)) ; The arm is no longer holding the top block
    (on ?b_top ?b_bottom)      ; The top block is now on top of the bottom block
    (not (clear ?b_bottom))    ; The bottom block is no longer clear
    (empty ?a)                 ; The arm is now empty
)
)

(:action unstack
   :parameters (
?a - arm
?b_top - block
?b_bottom - block
   )
   :precondition
(and
    (empty ?a) ; The arm is empty
    (clear ?b_top) ; The top block is clear
    (on ?b_top ?b_bottom) ; The top block is on the bottom block
    (at ?a ?t) ; The arm is at the table
)
   :effect
(and
    (not (empty ?a)) ; The arm is no longer empty
    (holding ?a ?b_top) ; The arm is now holding the top block
    (not (on ?b_top ?b_bottom)) ; The top block is no longer on the bottom block
    (clear ?b_bottom) ; The bottom block is now clear
)
)
)