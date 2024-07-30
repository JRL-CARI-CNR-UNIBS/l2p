(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue_block - block
red_block - block
yellow_block - block
green_block - block
table1 - table
arm1 - arm
   )

   (:init
(on blue_block red_block)
(on red_block yellow_block)
(on yellow_block table1)
(on green_block table1)
(empty arm1)
(clear red_block)
   )

   (:goal
(and
   (on red_block green_block) 
   (on green_block red_block) 
)
   )

)