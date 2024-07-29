(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue - block
red - block
green - block
yellow - block
arm1 - arm
table1 - table
   )

   (:init
(on_table blue)
(on_table red)
(on_table green)
(on_table yellow)
(on_top blue red)
(on_top green yellow)
(arm_empty )
(block_clear blue)
(block_clear green)
(block_clear red)
(block_clear yellow)
   )

   (:goal
(and 
   (on_top red green) 
   (on_top green blue) 
   (on_top blue yellow) 
   (block_clear yellow) 
)
   )

)