(define
   (problem test_domain_problem)
   (:domain test_domain)

   (:objects 
{'block1': 'block', 'block2': 'block', 'block3': 'block', 'block4': 'block', 'block5': 'block', 'arm1': 'arm', 'table1': 'table'}
   )

   (:init
(on-table block1)
(on-table block2)
(on-table block3)
(on-table block4)
(on-table block5)
(clear block1)
(clear block2)
(clear block3)
(clear block4)
(clear block5)
(empty arm1)
(on block2 block1)
(on block3 block2)
(on block4 block5)
   )

   (:goal
(and 
   (on block3 block1) 
   (on block5 block3) 
)
   )

)