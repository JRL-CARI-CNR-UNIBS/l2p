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
      (package-at ?p - package ?l - location) ;  true if the package ?p is located at location ?l
      (truck-at ?t - truck ?l - location) ;  true if the truck ?t is located at location ?l
      (truck-has-space ?t - truck) ;  true if the truck ?t has space to load more packages
      (truck-has-package ?t - truck ?p - package) ;  true if the truck ?t is carrying the package ?p
      (truck-holding ?t - truck ?p - package) ;  true if the truck ?t is currently holding the package ?p
      (truck-at-location ?t - truck ?l - location) ;  true if the truck ?t is at the location ?l
      (package-at-location ?p - package ?l - location) ;  true if the package ?p is at the location ?l
      (airplane-at-airport ?a - plane) ;  true if the airplane ?a is at the designated airport location
      (airplane-has-space ?a - plane) ;  true if the airplane ?a has space available to load more packages
      (airplane-has-package ?a - plane ?p - package) ;  true if the airplane ?a is carrying the package ?p
      (airplane-holding ?a - plane ?p - package) ;  true if the airplane ?a is holding the package ?p
      (at-airport ?a - plane ?l - location) ;  true if the airplane ?a is at the airport located at ?l
      (location-connected ?l1 - location ?l2 - location ?c - city) ;  true if location ?l1 is directly connected to location ?l2 in city ?c
      (package-on-ground ?p - package) ;  true if the package ?p is on the ground and not loaded onto any vehicle
      (at-airplane ?a - plane ?l - location) ;  true if the airplane ?a is currently at the location ?l
      (airplane-in-city ?plane - plane, ?city - city) ;  true if the airplane ?plane is currently in the city ?city
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
   )
   :precondition
(and
    (package-on-ground ?p)
    (airplane-at-airport ?a)
    (airplane-has-space ?a)
)
   :effect
(and
    (not (package-on-ground ?p))
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
?from_city - city
?to_city - city
   )
   :precondition
(and
    (at-airport ?from_city)
    (at-airport ?to_city)
    (airplane-in-city ?plane ?from_city)
)
   :effect
(and
    (not (airplane-in-city ?plane ?from_city))
    (airplane-in-city ?plane ?to_city)
)
)
)