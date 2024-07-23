import subprocess
import os
import re

def run_fast_downward(domain_file, problem_file, plan_file="sas_plan"):
    try:
        downward_path = os.path.expanduser("~/Downloads/downward/fast-downward.py")

        # lmcut() = landmark-cut heuristic - refer to: https://www.fast-downward.org/PlannerUsage
        result = subprocess.run(
            [downward_path, domain_file, problem_file, "--search", "astar(lmcut())"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # planning succeeded
            with open(plan_file, 'w') as f:
                f.write(result.stdout)
            print("Planning succeeded!")
            
            # extract the plan steps from the output
            plan_output = extract_plan_steps(result.stdout)
            if plan_output:
                print("Plan output:")
                print(plan_output)
            else:
                print("No plan found in the output.")
        else:
            # planning failed
            print("Planning failed!")
            print(result.stderr)
    except Exception as e:
        print("An error occurred while running the planner.")
        print(e)

def extract_plan_steps(output):
    plan_steps = re.findall(r'^\w+.*\(.*\)', output, re.MULTILINE)
    return "\n".join(plan_steps)

if __name__ == "__main__":
    domain_file_path = "data/domain.pddl"
    problem_file_path = "data/problem_3.pddl"
    run_fast_downward(domain_file_path, problem_file_path)