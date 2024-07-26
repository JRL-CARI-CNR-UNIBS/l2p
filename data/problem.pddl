(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue_block - block
red_block - block
yellow_block - block
green_block - block
arm1 - arm
table1 - table
   )

   (:init
(on blue_block red_block)
(on red_block yellow_block)
(clear yellow_block)
(clear green_block)
(empty arm1)
(at arm1 table1)
   )

   (:goal
(and 
   (on red_block green_block) 
)
   )

)