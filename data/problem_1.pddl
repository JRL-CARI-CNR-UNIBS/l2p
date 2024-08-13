(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue - block
red - block
yellow - block
green - block
arm1 - arm
table1 - table
   )

   (:init
(on blue red)
(on red yellow)
(on yellow table1)
(on green table1)
(empty arm1)
   )

   (:goal
(and 
   (on red green) 
)
   )

)