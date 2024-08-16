# Activate virtual environment: 
# MacOS: source env/bin/activate

# Run file
# Windows: python -m tests.usage.usage
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem
import sys

def check_parse_domain(file_path):
    try:
        domain = parse_domain(file_path)
        pddl_domain = domain_to_string(domain)
        return pddl_domain
    except Exception as e:
        print("------------------")
        print(f"Error parsing domain: {e}", file=sys.stderr)
        print("------------------")
        sys.exit(1)

def check_parse_problem(file_path):
    try:
        problem = parse_problem(file_path)
        pddl_problem = problem_to_string(problem)
        return pddl_problem
    except Exception as e:
        print("------------------")
        print(f"Error parsing domain: {e}", file=sys.stderr)
        print("------------------")
        sys.exit(1)

if __name__ == "__main__":
    
    # domain_file_path = 'tests/domain.pddl'
    # pddl_domain = check_parse_domain(domain_file_path)
    # print("PDDL domain:\n", pddl_domain)
    
    # with open(domain_file_path, "w") as f:
    #     f.write(pddl_domain)

    # print("------------------")

    # problem_file_path_1 = 'tests/problem_1.pddl'
    # problem_file_path_2 = 'tests/problem_2.pddl'
    # problem_file_path_3 = 'tests/problem_3.pddl'
    
    # pddl_problem = check_parse_problem(problem_file_path_1)
    # print("PDDL Problem:\n", pddl_problem)

    # with open(problem_file_path_1, "w") as f:
    #     f.write(pddl_problem)
        
    # pddl_problem = check_parse_problem(problem_file_path_2)
    # print("PDDL Problem:\n", pddl_problem)

    # with open(problem_file_path_2, "w") as f:
    #     f.write(pddl_problem)
        
    # pddl_problem = check_parse_problem(problem_file_path_3)
    # print("PDDL Problem:\n", pddl_problem)

    # with open(problem_file_path_3, "w") as f:
    #     f.write(pddl_problem)
        
    
    
    domain_file_path = 'paper_reconstructions/llm+dm/results/domain.pddl'
    problem_file_path = 'data/problem_1.pddl'
    
    pddl_domain = check_parse_domain(domain_file_path)
    print("PDDL domain:\n", pddl_domain)
    
    with open(domain_file_path, "w") as f:
        f.write(pddl_domain)

    # print("------------------")
    
    # pddl_problem = check_parse_problem(problem_file_path)
    # print("PDDL Problem:\n", pddl_problem)

    # with open(problem_file_path, "w") as f:
    #     f.write(pddl_problem)
        
        
    
    # domain = parse_domain(domain_file_path)
    # problem = parse_problem(problem_file_path)
    
    # problem.check(domain)