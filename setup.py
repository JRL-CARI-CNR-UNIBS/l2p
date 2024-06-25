"""
Activate virtual environment: source env/bin/activate

L2P Checklist

- [ ] Integrate action-construction architecture into work
    - [ ] Implement add_predicates
- [ ] Distribute each component into its separate class, let domain_builder be the coordinating class
- [ ] Implement auto-feedback checklist
- [ ] Implement LLM-generated feedback checklist
- [ ] Implement PDDL generator — parser to assemble everything together

- The action_construction pipeline consists of:
    - Action extraction loop
        - For each action description, construct singular action (parameter, precondition, effects) based on current predicts and put into a list
        - Update list of new predicates 
        - Prune unused predicates and types
    - Once all actions generated, add actions (iteratively) and predicates to PDDLGenerator

PDDLGenerator is essentially domain_builder / task_builder — CHANGE THINGS AROUND TO PERFORM SAME FUNCTION

- [ ] Implement add_type — run through 
- [ ] Implement add_action — run through whole pipeline

- [ ] Implement task_builder
    - [ ] extract_object
    - [ ] extract_initial_state
    - [ ] extract_goal_state
    - [ ] Implement get functions
    - [ ] Implement add functions — pipelines

- [ ] Implement external planner tool


"""
