(:action unstack
   :parameters (
?a - arm
?b1 - block
?b2 - block
   )
   :precondition
(and
    (empty ?a) ; The arm is empty
    (clear ?b1) ; The top block is clear
    (on ?b1 ?b2) ; ?b1 is on top of ?b2
)
   :effect
(and
    (holding ?a ?b1) ; The arm is holding the top block
    (not (on ?b1 ?b2)) ; ?b1 is no longer on top of ?b2
    (clear ?b2) ; The bottom block is clear
)
)