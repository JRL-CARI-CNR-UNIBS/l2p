(define
   (problem blocksworld_problem)
   (:domain blocksworld)

   (:objects 
      blue_block - block
      red_block - block
      yellow_block - block
      green_block - block
      table1 - table
   )

   (:init
      (on_block red_block yellow_block)
      (on_block blue_block red_block)
      (on_table yellow_block)
      (on_table green_block)
      (held blue_block)
      (stability_checked blue_block)
      (stability_checked red_block)
      (stability_checked yellow_block)
      (stability_checked green_block)
   )

   (:goal
      (and 
         (on_block red_block green_block) 
         (on_table green_block) 
         (on_table yellow_block) 
         (on_block blue_block red_block) 
      )
   )

)