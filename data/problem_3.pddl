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
(on_table red_block1 table)
(on_table blue_block1 table)
(on_table green_block1 table)
(on_table green_block2 table)
(clear red_block1)
(clear blue_block1)
(clear green_block1)
(clear green_block2)
(holding arm1)
(on_table green_block1 blue_block1)
(on_table blue_block1 red_block1)
(on_table red_block2 green_block2)
   )

   (:goal
(and 
   (on_table red_block1 table) 
   (on_table red_block2 table) 
   (on_table blue_block1 table) 
   (on_table green_block1 table) 
   (on_table green_block2 table) 
   (clear green_block1) 
   (clear green_block2) 
   (clear blue_block1) 
   (clear red_block1) 
   (clear red_block2) 
   (holding arm1 red_block1) 
   (holding arm1 blue_block1) 
   (holding arm1 green_block1) 
   (holding arm1 red_block2) 
)
   )

)