(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
block_red1 - block
block_red2 - block
block_blue1 - block
block_green1 - block
block_green2 - block
   )

   (:init
(on block_red1 table)
(on block_blue1 block_red1)
(on block_green1 block_blue1)
(on block_green2 table)
(on block_red2 block_green2)
(empty arm)
(at arm table)
(clear block_red1)
(clear block_blue1)
(clear block_green1)
(clear block_green2)
   )

   (:goal
(and 
   (on block_red1 block_blue1) 
   (on block_red2 block_blue1) 
   (on block_blue1 block_green1) 
   (clear block_green2) 
   (on block_green2 table) 
)
   )

)