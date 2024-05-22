import pprint

def get_input(prompt):
    return input(prompt)

def display_current_state(state):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(state)

def create_pddl_domain():
    domain = {
        'name': '',
        'requirements': [],
        'types': [],
        'predicates': [],
        'actions': []
    }

    domain['name'] = get_input("Enter domain name: ")

    while True:
        display_current_state(domain)
        requirement = get_input("Enter a requirement (or 'done' to finish): ")
        if requirement.lower() == 'done':
            break
        domain['requirements'].append(requirement)

    while True:
        display_current_state(domain)
        _type = get_input("Enter a type (or 'done' to finish): ")
        if _type.lower() == 'done':
            break
        domain['types'].append(_type)

    while True:
        display_current_state(domain)
        predicate = get_input("Enter a predicate (or 'done' to finish): ")
        if predicate.lower() == 'done':
            break
        domain['predicates'].append(predicate)

    while True:
        display_current_state(domain)
        action_name = get_input("Enter action name (or 'done' to finish): ")
        if action_name.lower() == 'done':
            break
        action_parameters = get_input("Enter action parameters: ")
        action_preconditions = get_input("Enter action preconditions: ")
        action_effects = get_input("Enter action effects: ")
        action = {
            'name': action_name,
            'parameters': action_parameters,
            'preconditions': action_preconditions,
            'effects': action_effects
        }
        domain['actions'].append(action)

    return domain

def create_pddl_problem(domain_name):
    problem = {
        'name': '',
        'domain': domain_name,
        'objects': [],
        'init': [],
        'goal': []
    }

    problem['name'] = get_input("Enter problem name: ")

    while True:
        display_current_state(problem)
        obj = get_input("Enter an object (or 'done' to finish): ")
        if obj.lower() == 'done':
            break
        problem['objects'].append(obj)

    while True:
        display_current_state(problem)
        init_state = get_input("Enter an initial state predicate (or 'done' to finish): ")
        if init_state.lower() == 'done':
            break
        problem['init'].append(init_state)

    while True:
        display_current_state(problem)
        goal_state = get_input("Enter a goal state predicate (or 'done' to finish): ")
        if goal_state.lower() == 'done':
            break
        problem['goal'].append(goal_state)

    return problem

def main():
    print("Creating PDDL Domain File")
    domain = create_pddl_domain()
    display_current_state(domain)

    proceed = get_input("Do you want to proceed to creating the problem file? (yes/no): ")
    if proceed.lower() != 'yes':
        print("Exiting...")
        return

    print("Creating PDDL Problem File")
    problem = create_pddl_problem(domain['name'])
    display_current_state(problem)

if __name__ == "__main__":
    main()
