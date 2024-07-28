(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
blue - block
red - block
green - block
yellow - block
   )

   (:init
(on_table red table)
(on_table green table)
(on_table yellow table)
(on blue red)
(clear blue)
(clear green)
(empty arm1)
(at arm1 table)
   )

   (:goal
(and 
   (on red table) 
   (on green red) 
   (on blue green) 
   (on yellow blue) 
   (clear yellow) 
)
   )

)