(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue_block - block
red_block - block
green_block - block
yellow_block - block
arm1 - arm
   )

   (:init
(clear red_block)
(clear yellow_block)
(clear blue_block)
(clear green_block)
(empty arm1)
(on blue_block red_block)
(on green_block yellow_block)
   )

   (:goal
(and 
   (on red_block table) 
   (on green_block red_block) 
   (on blue_block green_block) 
   (on yellow_block blue_block) 
)
   )

)