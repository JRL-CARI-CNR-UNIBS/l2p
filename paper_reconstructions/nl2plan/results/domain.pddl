(define (domain test_domain)
   (:requirements
     :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects)

   (:types 
      block - physical_object
      table - physical_object
      arm - tool
   )

   (:predicates 
      (at ?b - block ?t - table) ;  true if the block ?b is at the table ?t
      (clear ?b - block) ;  true if the block ?b is clear (not covered by another block)
      (empty ?a - arm) ;  true if the arm ?a is empty (not holding any block)
      (holding ?a - arm ?b - block) ;  true if the arm ?a is holding the block ?b
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
             (at ?b ?t) ; The block is at the table
             (clear ?b) ; The block is clear (not covered by another block)
             (empty ?a) ; The arm is empty (not holding any block)
         )
      :effect
         (and
             (not (at ?b ?t)) ; The block is no longer at the table
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
             (clear ?t) ; The location on the table is clear
         )
      :effect
         (and
             (not (holding ?a ?b)) ; The arm is no longer holding the block
             (at ?b ?t) ; The block is now on the table
             (clear ?b) ; The block is now clear
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

   (:action check_clear
      :parameters (
         ?b - block
         ?a - arm
      )
      :precondition
         (and
             (at ?b ?t) ; The block is at the table
             (empty ?a) ; The arm is empty
         )
      :effect
         (and
             (clear ?b) ; The block is confirmed to be clear
         )
   )
)