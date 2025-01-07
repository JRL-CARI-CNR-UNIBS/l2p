(define (domain blocksworld)
   (:requirements
      :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects)

   (:types 
      block - object
      table - object
   )

   (:predicates 
      (on_table ?b - block ?t - table) ;  true if block ?b is on the table ?t
      (on_block ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
      (held ?b - block) ;  true if block ?b is currently being held by the robot arm
   )

   (:action pick_block
      :parameters (
         ?b - block
         ?t - table
         ?b2 - block
      )
      :precondition
         (and
             (or (on_table ?b ?t) (on_block ?b ?b2)) ; The block is either on the table or on another block
             (not (held ?b)) ; The block is not currently being held
         )
      :effect
         (and
             (held ?b) ; The block is now being held by the robot arm
             (not (on_table ?b ?t)) ; The block is no longer on the table
             (not (on_block ?b ?b2)) ; The block is no longer on top of another block
         )
   )

   (:action place_on_table
      :parameters (
         ?b - block
         ?t - table
      )
      :precondition
         (and
             (held ?b) ; The block is currently being held
             (not (on_block ?b ?t)) ; The table must be clear of any blocks directly beneath the block being placed
             (not (on_block ?b1 ?t)) ; The table must not have any blocks directly beneath the block being placed
         )
      :effect
         (and
             (on_table ?b ?t) ; The block is now on the table
             (not (held ?b)) ; The block is no longer being held
         )
   )

   (:action place_on_block
      :parameters (
         ?b1 - block
         ?b2 - block
         ?t - table
      )
      :precondition
         (and
             (held ?b1) ; The block being placed is currently held
             (not (held ?b2)) ; The block being placed on is not currently held
             (not (on_block ?b1 ?b2)) ; The block being placed on is clear of any blocks directly beneath it
             (not (on_table ?b2 ?t)) ; The block being placed on is not on the table
         )
      :effect
         (and
             (on_block ?b1 ?b2) ; The block being placed is now on top of the other block
             (not (held ?b1)) ; The block being placed is no longer held
         )
   )

   (:action release_block
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (held ?b) ; The block is currently being held
             (or (on_table ?b) (not (exists (?b2 - block) (on_block ?b ?b2)))) ; The block is either on the table or not on top of another block
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer held
             (on_table ?b) ; The block is placed on the table after being released
         )
   )
)