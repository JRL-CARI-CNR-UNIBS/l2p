(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue - block
red - block
yellow - block
green - block
arm - arm
table - table
   )

   (:init
(on blue red)
(on red yellow)
(on yellow table)
(on green table)
(empty )
(clear blue)
(clear red)
(clear yellow)
(clear green)
(on-table blue)
(on-table red)
(on-table green)
   )

   (:goal
(and 
   (on red green) 
)
   )

)