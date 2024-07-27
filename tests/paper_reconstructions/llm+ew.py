"""
Paper: "Leveraging Environment Interaction for Automated PDDL Generation and Planning with Large Language Models" Mahdavi et al (2024)
Source code: N/A
Run: python3 -m tests.paper_reconstructions.llm+ew

HAVE TO GET BACK TO FIGURING OUT HOW EW method WORKS
"""

"""
Focus: using LLMs and environmental feedback to auto-generate both PDDL domain+problem files w/o human intervention
    - Problem of limited feedback from PDDL plan failures
    - Addresses how brittle PDDL domain are; omitting minor rules lead to cascading plan failures

Assumes the following:
    1. NL domain description
    2. NL task description
    3. Object list from ground-truth task: label recognitiion purposes
    4. Action interface (names and parameters) from ground-truth domain: assumes conduction of API calls
    
Algorithm:
    1. LLM to generate problem PDDL candidates
    2. For each problem candidate:
        - Keep history 'h(i)' of conversation (PDDL problem, NL domain description)
        - Initialize domain empty template as best: 'd(i)'
        
        For however many cycles 'c':
            - LLM to generate domain PDDL candidates 'd(i,1), d(i,2), ... ' given 'h(i)'
            - Calculate (argmax) current best domain PDDL candidate 'd(c)' - evaluate LLM responses using EW
            - Obtain NL feedback from EW on given list of objects and action interface: f(c)
            - Update history with "d(c)" and "f(c)"
            - Update best domain candidate (argmax) between current and overall candidate using EW
            
    3. Obtain (argmax) best pair '(d,p)' of domain candidate corresponding with respective problem candidate using EW
    4. Return 'd, p'
"""

domain_template = \
"""
(define (domain gripper -strips)
    (:requirements :strips :typing)
    (:types room obj robot gripper)
    (:predicates)
    
    (:action move
        :parameters (?r - robot ?from ?to - room)
        :precondition ()
        :effect ())
        
    (:action pick
        :parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        :precondition ()
        :effect ())
        
    (:action drop
        :parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        :precondition ()
        :effect ())
)
"""

problem_template = \
"""
(define (problem gripper -2-3-4)
    (:domain gripper -strips)
    (:objects lgripper1 lgripper2 rgripper1 rgripper2 - gripper 
        ball1 ball2 ball3 ball4 - obj robot1 robot2 - robot 
        room1 room2 room3 - room)
    (:init )
    (:goal (and )) 
)
"""


grippers_domain_example = \
"""
(define 
    (domain gripper -strips)
    (:requirements :strips :typing)
    (:types room obj robot gripper)
    (:predicates (at-robby ?r - robot ?x - room)
        (at ?o - obj ?x - room)
        (free ?r - robot ?g - gripper)
        (carry ?r - robot ?o - obj ?g - gripper))
        
    (:action move
        :parameters (?r - robot ?from ?to - room)
        :precondition (and (at-robby ?r ?from))
        :effect (and (at-robby ?r ?to)
            (not (at-robby ?r ?from))))
            
    (:action pick
        :parameters (?r - robot ?obj - obj ?room - room ?g - gripper)
        :precondition (and (at ?obj ?room ) ( at - robby ?r ?room ) (free ?r ?g))
        :effect (and (carry ?r ?obj ?g ) (not (at ?obj ?room )) (not (free ?r ?g))))
        
    (:action drop
        :parameters (?r - robot ?obj - obj ?room - room ?g - gripper)
        :precondition (and (carry ?r ?obj ?g) (at-robby ?r ?room))
        :effect (and (at ?obj ?room) (free ?r ?g) (not (carry ?r ?obj ?g))))
)
"""

grippers_problem_example = \
"""
(define (problem gripper -2-3-4)
    (:domain gripper -strips)
    (:objects robot1 robot2 - robot
        rgripper1 lgripper1 rgripper2 lgripper2 - gripper
        room1 room2 room3 - room
        ball1 ball2 ball3 ball4 - obj)
        
    (:init 
        (at-robby robot1 room2)
        (free robot1 rgripper1)
        (free robot1 lgripper1)
        (at-robby robot2 room3)
        (free robot2 rgripper2)
        (free robot2 lgripper2)
        (at ball1 room3)
        (at ball2 room1)
        (at ball3 room1)
        (at ball4 room3)
    )    
    
    (:goal 
        (and
            (at ball1 room2)
            (at ball2 room2)
            (at ball3 room3)
            (at ball4 room3)
        )
    )
)
"""

grippers_domain_nl = \
"""
The gripper domain involves a world with multiple rooms, robots, and objects (balls). Each robot has two grippers that can be used to pick up and drop objects. The goal is to move objects from their initial locations to the desired goal locations using the robots and their grippers.

The domain includes three actions:
    1. move: This action allows a robot to move from one room to another. The precondition is that the robot must be in the starting room. The effect is that the robot is no longer in the starting room and is now in the destination room.
    2. pick: This action allows a robot to pick up an object using one of its grippers. The preconditions are that the object and the robot must be in the same room , and the specified gripper must be free (not holding any object). The effect is that the robot is now carrying the object with the specified gripper , the object is no longer in the room , and the gripper is no longer free.
    3. drop: This action allows a robot to drop an object it is carrying in a specific room using one of its grippers. The preconditions are that the robot must be carrying the object with the specified gripper and the robot must be in the specified room. The effect is that the object is now in the room , the gripper is free , and the robot is no longer carrying the object with that gripper.
"""

grippers_problem_nl = \
"""
You control two robots, each equipped with a left and right gripper, capable of moving objects (balls) between different rooms.

Initially:
    - Robot1 is in room2 and both its grippers (rgripper1 and lgripper1) are free.
    - Robot2 is in room3 and both its grippers (rgripper2 and lgripper2) are free.
    - Ball1 and Ball4 are in room3.
    - Ball2 and Ball3 are in room1. 
    
Your goal is to achieve the following configuration:
    - Ball1 must be moved to room2.
    - Ball2 must be moved to room2.
    - Ball3 must remain in room3.
    - Ball4 must remain in room3.
"""

grippers_problem_plan_example = \
"""
(move robot2 room3 room1)
(pick robot2 ball2 room1 lgripper2)
(move robot2 room1 room2)
(drop robot2 ball2 room2 lgripper2)
(move robot1 room2 room1)
(pick robot1 ball3 room1 lgripper1)
(move robot1 room1 room3)
(pick robot1 ball1 room3 rgripper1)
(drop robot1 ball3 room3 lgripper1)
(move robot1 room3 room2)
(drop robot1 ball1 room2 rgripper1)
"""