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
(at blue_block red_block)
(at red_block yellow_block)
(at yellow_block table)
(at green_block table)
(clear yellow_block)
(clear green_block)
(exists blue_block)
(exists red_block)
(exists yellow_block)
(exists green_block)
   )

   (:goal
(and 
   (at red_block green_block) 
)
   )

)