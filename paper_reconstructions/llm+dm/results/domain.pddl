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
(truck-at ?t - truck ?l - location) ;  true if the truck ?t is currently located at location ?l
(package-at ?p - package ?l - location) ;  true if the package ?p is currently located at location ?l
(truck-has-space ?t - truck) ;  true if the truck ?t has space to load more packages
(truck-holding ?t - truck ?p - package) ;  true if the truck ?t is currently holding the package ?p
(at-airport ?a - plane ?l - location) ;  true if the airplane ?a is at the airport located at ?l
(location-connected ?from - location ?to - location, ?c - city) ;  true if location ?from is directly connected to location ?to in city ?c
(connected-cities ?from_city - city ?to_city - city) ;  true if there is a direct connection between city ?from_city and city ?to_city
(package-on-ground ?p - package) ;  true if the package ?p is on the ground and ready to be loaded
(airplane-at-airport ?a - plane) ;  true if the airplane ?a is at the designated airport location
(airplane-has-space ?a - plane) ;  true if the airplane ?a has space available to load more packages
(airplane-has-package ?a - plane ?p - package) ;  true if the airplane ?a is carrying the package ?p
(plane-at ?a - plane ?c - city) ;  true if the airplane ?a is located in city ?c
(package-on-plane ?p - package ?a - plane) ;  true if the package ?p is currently on airplane ?a
(location-in-city ?l - location ?c - city) ;  true if the location ?l is situated in city ?c
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
    (truck-holding ?t ?p)
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
    (truck-at ?t ?l)
)
   :effect
(and
    (not (truck-holding ?t ?p))
    (package-at ?p ?l)
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
?c - city
   )
   :precondition
(and
    (plane-at ?a ?c)
    (package-on-plane ?p ?a)
    (location-in-city ?l ?c)
)
   :effect
(and
    (not (package-on-plane ?p ?a))
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
    (at-airport ?plane ?from_city)
    (connected-cities ?from_city ?to_city)
)
   :effect
(and
    (not (at-airport ?plane ?from_city))
    (at-airport ?plane ?to_city)
)
)
)