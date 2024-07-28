(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue_block - block
red_block - block
yellow_block - block
green_block - block
arm - arm
table - table
   )

   (:init
(on blue_block red_block)
(on red_block yellow_block)
(on_table yellow_block)
(on_table green_block)
(clear green_block)
(clear yellow_block)
(empty arm)
(at arm table)
   )

   (:goal
(and 
   (on red_block green_block) 
   (clear red_block) 
   (clear green_block) 
)
   )

)