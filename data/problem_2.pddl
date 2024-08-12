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
(on-table blue)
(on-table red)
(on-table green)
(on-table yellow)
(clear blue)
(clear red)
(clear green)
(clear yellow)
(empty arm1)
   )

   (:goal
(and
   (on red green)
   (on green blue)
   (on blue yellow)
   (finalised house1)
)
   )

)