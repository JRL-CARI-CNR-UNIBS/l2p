(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue_block - block
red_block - block
yellow_block - block
green_block - block
   )

   (:init
(on_top blue_block red_block)
(on_top red_block yellow_block)
(on_table yellow_block)
(on_table green_block)
(arm_empty )
(block_clear blue_block)
(block_clear green_block)
   )

   (:goal
(and 
   (on_top red_block green_block) 
   (block_clear green_block) 
   (not (block_clear red_block)) 
)
   )

)