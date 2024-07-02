(define (domain test_domain)
   (:requirements
      :strips :typing :equality :negative-preconditions :disjunctive-preconditions
      :universal-preconditions :conditional-effects
   )

   (:types 
      object ; Object is always root, everything is an object
      block - movable_object ; An object that can be picked up and placed on the table or on top of another block.
      location - object ; A type of object consisting of places where objects can be placed.
      table - location ; A surface where blocks can be placed.
   )

   (:predicates 
      (at ?o - object ?l - location) ;  true if the object ?o is at the location ?l
      (held ?o - object) ;  true if the object ?o is being held
   )

   (:action pick_up_block
      :parameters (
         ?robot_arm - object
         ?block - object
         ?current_location - location
      )
      :precondition
         (and
             (at ?robot_arm ?current_location) ; The robot arm is at the current location of the block
             (not (held ?block)) ; The block is not already being held
         )
      :effect
         (and
             (held ?block) ; The block is now held by the robot arm
             (not (at ?block ?current_location)) ; The block is no longer at its current location
         )
   )

   (:action place_on_table
      :parameters (
         ?robot_arm - object
         ?block - object
      )
      :precondition
         (and
             (held ?block) ; The block is being held by the robot arm
             (not (at ?block table)) ; The block is not already on the table
         )
      :effect
         (and
             (not (held ?block)) ; The block is no longer held
             (at ?block table) ; The block is now on the table
         )
   )

   (:action place_on_block
      :parameters (
         ?robot_arm - object
         ?block_to_place - object
         ?block_below - object
      )
      :precondition
         (and
             (held ?block_to_place) ; The robot arm is holding the block to be placed
             (at ?robot_arm ?block_below) ; The robot arm is at the same location as the block below
             (not (held ?block_below)) ; The block below is clear
         )
      :effect
         (and
             (not (held ?block_to_place)) ; The block to be placed is no longer held
             (at ?block_to_place ?block_below) ; The block to be placed is now at the same location as the block below
         )
   )

   (:action move_block
      :parameters (
         ?robot_arm - object
         ?block - object
         ?from - location
         ?to - location
      )
      :precondition
         (and
             (at ?robot_arm ?from) ; The robot arm is at the location where the block is being moved from
             (at ?block ?from) ; The block is at the location where it is being moved from
             (not (held ?block)) ; The robot arm is not holding any other object
             (not (= ?from ?to)) ; The locations are different
         )
      :effect
         (and
             (not (at ?block ?from)) ; The block is no longer at the location it was moved from
             (at ?block ?to) ; The block is now at the location it was moved to
         )
   )

   (:action clear_block
      :parameters (
         ?b - block
      )
      :precondition
         (and
             (not (held ?b)) ; The block is not being held
             (not (exists (?other_block - block) (and (on ?other_block ?b)))) ; The block is not under any other block
         )
      :effect
         (and
             (not (held ?b)) ; The block is no longer being held
             (clear ?b) ; The block is now clear and not under any other block
         )
   )
)