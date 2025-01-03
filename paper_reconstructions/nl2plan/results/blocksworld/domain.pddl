(define (domain blocksworld)
   (:requirements
      :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects)

   (:types 
      block - object
      table - object
   )

   (:predicates 
      (on_table ?b - block) ;  true if the block ?b is on the table
      (on_block ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2
      (held ?b - block) ;  true if the block ?b is currently held by the robot arm
      (stability_checked ?b - block) ;  true if the stability of block ?b has been checked by the robot arm
   )

   (:action pick_block
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (or (on_table ?b) (exists (?b2 - block) (on_block ?b ?b2))) ; The block is either on the table or on another block
             (not (held ?b)) ; The block is not currently held by the robot arm
         )
      :effect
         (and
             (held ?b) ; The block is now held by the robot arm
             (not (on_table ?b)) ; The block is no longer on the table
             (not (on_block ?b ?b2)) ; The block is no longer on top of another block (assuming ?b2 is the block it was on)
         )
   )

   (:action place_on_table
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (held ?b) ; The block is currently held by the robot arm
             (not (on_table ?b)) ; The block is not already on the table
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer held by the robot arm
             (on_table ?b) ; The block is now on the table
         )
   )

   (:action stack_block
      :parameters (
         ?b1 - block
         ?b2 - block
      )
      :precondition
         (and
             (held ?b1) ; The block ?b1 is currently held by the robot arm
             (not (held ?b2)) ; The block ?b2 is not currently held by the robot arm
             (or (on_table ?b2) (on_block ?b2 ?b3)) ; The block ?b2 is either on the table or on another block
         )
      :effect
         (and
             (not (held ?b1)) ; The block ?b1 is no longer held by the robot arm
             (on_block ?b1 ?b2) ; The block ?b1 is now on top of block ?b2
         )
   )

   (:action release_block
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (held ?b) ; The block is currently held by the robot arm
             (not (exists (?b2 - block) (on_block ?b ?b2))) ; The block is not on another block
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer held by the robot arm
             (on_table ?b) ; The block is now on the table after being released
         )
   )

   (:action check_stability
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (not (held ?b)) ; The block is not currently held by the robot arm
             (or (on_table ?b) (on_block ?b ?b1)) ; The block is either on the table or on top of another block
         )
      :effect
         (and
             (stability_checked ?b) ; The stability of the block has been checked
         )
   )
)