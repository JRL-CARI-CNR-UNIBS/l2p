(define
   (problem blocksworld_problem)
   (:domain blocksworld)

   (:objects 
      block1 - block
      block2 - block
      block3 - block
      block4 - block
      table1 - table
   )

   (:init
      (on block1 table1)
      (on block2 block1)
      (on block3 table1)
      (on block4 block3)
   )

   (:goal
      (and 
         (on block1 table1) 
         (on block3 block1) 
         (on block2 block3) 
         (on block4 block2) 
      )
   )

)