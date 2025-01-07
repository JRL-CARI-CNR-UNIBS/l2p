(define (domain blocksworld)
   (:requirements
      :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects)

   (:types 
      movable_object - object
      block - movable_object
      table - object
   )

   (:predicates 
      (on_table ?b - block) ;  true if the block ?b is on the table.
      (held ?b - block) ;  true if the block ?b is currently held by the robot arm.
      (on ?b1 - block ?b2 - block) ;  true if block ?b1 is on top of block ?b2.
   )

   (:action pick_block
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (or (on_table ?b) (exists (?b2 - block) (on ?b ?b2))) ; The block is either on the table or on another block
             (not (held ?b)) ; The block is not currently held by the arm
         )
      :effect
         (and
             (held ?b) ; The block is now held by the robot arm
             (not (on_table ?b)) ; The block is no longer on the table
             (not (on ?b ?b2)) ; The block is no longer on top of another block (for all blocks ?b2)
         )
   )

   (:action place_on_table
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (held ?b) ; The block is currently held by the robot arm
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer held by the robot arm
             (on_table ?b) ; The block is now on the table
         )
   )

   (:action place_on_block
      :parameters (
         ?b1 - block
         ?b2 - block
         ?b3 - block
      )
      :precondition
         (and
             (held ?b1) ; The block being placed is currently held by the robot arm.
             (or (on_table ?b2) (on ?b2 ?b3)) ; The target block must be on the table or already stacked.
             (not (held ?b2)) ; The target block must not be held by the arm.
         )
      :effect
         (and
             (not (held ?b1)) ; The block being placed is no longer held by the robot arm.
             (on ?b1 ?b2) ; The block being placed is now on top of the target block.
         )
   )

   (:action release_block
      :parameters (
         ?b - block
         ?b2 - block
      )
      :precondition
         (and
             (held ?b) ; The block is currently held by the robot arm
             (or (on_table ?b) (exists (?b2 - block) (on ?b ?b2))) ; The block is being released onto the table or onto another block
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer held by the robot arm
             (or (on_table ?b) (exists (?b2 - block) (on ?b ?b2))) ; The block is now on the table or on another block
         )
   )

   (:action pick_and_place_on_table
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (or (on_table ?b) (on ?b ?b2)) ; The block is either on the table or on another block
             (not (held ?b)) ; The block is not currently held by the robot arm
         )
      :effect
         (and
             (held ?b) ; The block is now held by the robot arm
             (not (on_table ?b)) ; The block is no longer on the table
             (not (on ?b ?b2)) ; The block is no longer on top of another block (if it was)
         )
   )

   (:action pick_and_place_on_block
      :parameters (
         ?b1 - block
         ?b2 - block
         ?b3 - block
      )
      :precondition
         (and
             (or (on_table ?b1) (on ?b1 ?b2)) ; ?b1 must be on the table or on another block
             (not (held ?b1)) ; ?b1 must not be currently held by the robot arm
             (or (on_table ?b2) (on ?b2 ?b3)) ; ?b2 must be on the table or on another block
         )
      :effect
         (and
             (held ?b1) ; ?b1 is now held by the robot arm
             (not (on_table ?b1)) ; ?b1 is no longer on the table
             (on ?b1 ?b2) ; ?b1 is now on top of ?b2
         )
   )
)