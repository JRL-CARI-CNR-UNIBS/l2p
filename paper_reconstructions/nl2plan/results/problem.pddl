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
(on blue_block red_block)
(on red_block yellow_block)
(on yellow_block table)
(on green_block table)
(clear blue_block)
(clear yellow_block)
(clear green_block)
(exists blue_block)
(exists red_block)
(exists yellow_block)
(exists green_block)
   )

   (:goal
(and 
   (on red_block green_block) 
)
   )

)