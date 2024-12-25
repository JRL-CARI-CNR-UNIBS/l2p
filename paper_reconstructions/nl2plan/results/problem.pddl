(define
   (problem test_problem)
   (:domain test_domain)

   (:objects 
      blue_block - block
      red_block - block
      yellow_block - block
      green_block - block
      table1 - table
   )

   (:init
      (on blue_block red_block)
      (on red_block yellow_block)
      (at yellow_block table1)
      (at green_block table1)
      (clear blue_block)
      (clear green_block)
      (clear red_block)
      (and )
      (on red_block green_block)
   )

   (:goal
      (and 
         (on red_block green_block) 
      )
   )

)