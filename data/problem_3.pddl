(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
red_block1 - block
red_block2 - block
blue_block1 - block
green_block1 - block
green_block2 - block
   )

   (:init
(on_table red_block1)
(block_clear red_block1)
(on_top blue_block1 red_block1)
(on_top green_block1 blue_block1)
(on_table green_block2)
(block_clear green_block2)
(on_top red_block2 green_block2)
(arm_empty )
   )

   (:goal
(and 
   (on_top blue_block1 red_block1) 
   (on_top green_block1 blue_block1) 
   (on_top red_block2 green_block1) 
   (on_top green_block2 red_block2) 
)
   )

)