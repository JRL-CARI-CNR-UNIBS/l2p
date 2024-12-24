(define (domain logistics)
      (:requirements
        :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects
      )
         (:types 
      truck
      plane
      package
      city
      location
   )

   (:predicates 
      (truck-at ?t - truck ?l - location) ;  true if the truck ?t is located at location ?l
      (package-at ?p - package ?l - location) ;  true if the package ?p is located at location ?l
      (truck-has-space ?t - truck) ;  true if the truck ?t has space to load more packages
      (truck-has-package ?t - truck ?p - package) ;  true if the truck ?t is carrying the package ?p
      (truck-holding ?t - truck ?p - package) ;  true if the truck ?t is holding the package ?p
      (airplane-at ?a - plane ?l - location) ;  true if the airplane ?a is located at location ?l
      (airplane-full ?a - plane) ;  true if the airplane ?a cannot carry more packages
      (airplane-has-package ?a - plane ?p - package) ;  true if the airplane ?a is carrying the package ?p
      (airplane-holding ?a - plane ?p - package) ;  true if the airplane ?a is currently holding the package ?p
      (at-airplane ?a - plane ?l - location) ;  true if the airplane ?a is located at the location ?l
      (location-connected ?l1 - location ?l2 - location ?c - city) ;  true if location ?l1 is directly connected to location ?l2 in city ?c
      (at-airport ?plane - plane ?city - city) ;  true if the airplane ?plane is at the airport in city ?city
      (truck-at-location ?t - truck ?l - location) ;  true if the truck ?t is at the location ?l
      (package-at-location ?p - package ?l - location) ;  true if the package ?p is at the location ?l
   )

(:action load_truck
   :parameters (
?p - package
?t - truck
?l - location
   )
   :precondition
(and
    (truck-at ?t ?l)
    (package-at ?p ?l)
    (truck-has-space ?t)
)
   :effect
(and
    (not (package-at ?p ?l))
    (truck-has-package ?t ?p)
)
)

(:action unload_truck
   :parameters (
?p - package
?t - truck
?l - location
   )
   :precondition
(and
    (truck-holding ?t ?p)
    (truck-at-location ?t ?l)
)
   :effect
(and
    (not (truck-holding ?t ?p))
    (package-at-location ?p ?l)
)
)

(:action load_airplane
   :parameters (
?p - package
?a - plane
?l - location
   )
   :precondition
(and
    (package-at ?p ?l)
    (airplane-at ?a ?l)
    (not (airplane-full ?a))
)
   :effect
(and
    (not (package-at ?p ?l))
    (airplane-has-package ?a ?p)
)
)

(:action unload_airplane
   :parameters (
?p - package
?a - plane
?l - location
   )
   :precondition
(and
    (airplane-holding ?a ?p)
    (at-airplane ?a ?l)
)
   :effect
(and
    (not (airplane-holding ?a ?p))
    (package-at ?p ?l)
)
)

(:action drive_truck
   :parameters (
?t - truck
?from - location
?to - location
?c - city
   )
   :precondition
(and
    (truck-at ?t ?from ?c)
    (location-connected ?from ?to ?c)
)
   :effect
(and
    (not (truck-at ?t ?from ?c))
    (truck-at ?t ?to ?c)
)
)

(:action fly_airplane
   :parameters (
?plane - plane
?from_airport - location
?to_airport - location
?from_city - city
?to_city - city
   )
   :precondition
(and
    (at-airport ?from_airport ?from_city)
    (at-airport ?to_airport ?to_city)
    (airplane-at ?plane ?from_airport)
)
   :effect
(and
    (not (airplane-at ?plane ?from_airport))
    (airplane-at ?plane ?to_airport)
)
)
)