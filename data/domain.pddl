(define (domain test_domain)
   (:requirements
      :strips :typing :equality :negative-preconditions :disjunctive-preconditions
      :universal-preconditions :conditional-effects
   )

   (:types 
      robot - object
      tool - object
      wrench - tool
      jack - tool
      pump - tool
      flat_tire - object
      car - object
      hub - car
      nut - hub
   )

   (:predicates 
      (has_tool ?robot - robot ?wrench - wrench) ;  true if the robot ?robot has the tool ?wrench in its possession
      (has_nut ?tire - flat_tire) ;  true if the flat tire ?tire has a nut that needs to be undone
      (car_lifted ?car - car ?hub - hub) ;  true if the car ?car is lifted at the hub ?hub
      (tire_on_hub ?tire - flat_tire ?hub - hub) ;  true if the flat tire ?tire is mounted on the hub ?hub
      (inflated ) ;  true if the spare tire ?tire has been inflated
   )

   (:action fetch_tool
      :parameters (
         ?robot - object
         ?tool - object
      )
      :precondition
         (and
             (at ?robot ?car_location) ; The robot is at the location of the car
             (in_boot ?tool) ; The tool is in the car's boot
         )
      :effect
         (and
             (not (in_boot ?tool)) ; The tool is no longer in the car's boot
             (holding ?robot ?tool) ; The robot is now holding the tool
         )
   )

   (:action undo_nut
      :parameters (
         ?robot - robot
         ?wrench - wrench
         ?tire - flat_tire
      )
      :precondition
         (and
             (has_tool ?robot ?wrench) ; The robot has the wrench
             (has_nut ?tire) ; The flat tire has a nut that needs to be undone
         )
      :effect
         (and
             (not (has_nut ?tire)) ; The nut on the flat tire is undone
         )
   )

   (:action jack_up
      :parameters (
         ?robot - robot
         ?car - car
         ?hub - hub
         ?jack - tool
      )
      :precondition
         (and
             (has_tool ?robot ?jack) ; The robot has the jack tool
             (valid_hub ?car ?hub) ; The hub specified is a valid hub of the car
         )
      :effect
         (and
             (car_lifted ?car ?hub) ; The car is lifted at the specified hub
         )
   )

   (:action remove_tire
      :parameters (
         ?robot - robot
         ?tire - flat_tire
         ?hub - hub
         ?wrench - wrench
      )
      :precondition
         (and
             (has_tool ?robot ?wrench) ; The robot has the tool to remove the tire
             (has_nut ?tire) ; The flat tire has a nut that needs to be undone
             (car_lifted ?car ?hub) ; The car is lifted at the hub where the tire is being removed
         )
      :effect
         (and
             (not (has_nut ?tire)) ; The flat tire no longer has a nut
             (not (tire_on_hub ?tire ?hub)) ; The hub is now without a tire
         )
   )

   (:action inflate_spare_tire
      :parameters (
         ?robot - robot
         ?tire - flat_tire
         ?pump - pump
      )
      :precondition
         (and
             (has_tool ?robot ?pump) ; The robot has the pump
             (tire_on_hub ?tire ?hub) ; The tire is mounted on the hub
             (car_lifted ?car ?hub) ; The car is lifted at the hub
         )
      :effect
         (and
             (inflated ?tire) ; The spare tire is now inflated
             (not (has_tool ?robot ?pump)) ; The robot no longer has the pump
         )
   )

   (:action put_on_spare_tire
      :parameters (
         ?robot - robot
         ?tire - flat_tire
         ?hub - hub
         ?wrench - wrench
      )
      :precondition
         (and
             (has_tool ?robot ?wrench) ; The robot has the necessary tool
             (has_nut ?tire) ; The flat tire has a nut that needs to be undone
             (car_lifted ?car ?hub) ; The car is lifted at the hub where the spare tire is being mounted
         )
      :effect
         (and
             (tire_on_hub ?tire ?hub) ; The spare tire is mounted on the hub
             (inflated ?tire) ; The spare tire is inflated
         )
   )
)