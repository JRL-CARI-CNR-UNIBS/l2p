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
        
    (: action pick
        : parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        : precondition ()
        : effect ())
        
    (: action drop
        : parameters (?r - robot ?o - obj ?room - room ?g - gripper)
        : precondition ()
        : effect ())
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