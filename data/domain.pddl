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
(arm_empty ) ;  
(block_clear ?b - block) ;  
(on_table ?b - block) ;  
(holding ?b - block) ;  true if the arm is currently holding the block ?b.
(on_top ?b1 - block ?b2 - block) ;  true if the block ?b1 is on top of the block ?b2.
   )

(:action pickup
   :parameters (

   )
   :precondition
(arm_empty)
(block_clear ?b - block)
(on_table ?b - block)
   :effect
- (not (arm_empty))
- (not (block_clear ?b - block))
- (not (on_table ?b - block))
- (holding ?b - block)
)

(:action putdown
   :parameters (

   )
   :precondition
(arm_empty)
(block_clear ?b - block)
(on_table ?b - block)
   :effect
- (arm_empty): true if the arm is empty after the action.
- (not (block_clear ?b - block)): true if the block ?b is no longer clear after the action.
- (on_table ?b - block): true if the block ?b is on the table after the action.
)

(:action stack
   :parameters (

   )
   :precondition
(arm_empty)
(block_clear)
(on_table)
   :effect
- (arm_empty): false
- (block_clear): false
- (on_table): false
- (on ?top_block - block ?bottom_block - block): true
)

(:action unstack
   :parameters (

   )
   :precondition
(arm_empty)
(block_clear ?top_block)
   :effect
- (arm_empty): false
- (block_clear ?top_block): false
- (block_clear ?bottom_block): true
- (holding ?top_block): true
- (on_top ?top_block ?bottom_block): false
)
)