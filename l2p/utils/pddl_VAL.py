"""
This file contains a subprocess based interface for calling the VAL plan validator. It is important to note that as val is not 
a python package, it is expected to be at VAL_PATH, which is set to where it is expected to be built in a git submodule during setup.

Run: python3 -m l2p.utils.pddl_val
"""

import subprocess

VAL_PARSER = "VAL/build/macos64/Release/bin/Parser"


def parse_pddl(val_parser, domain_file=None, problem_file=None) -> str:
    command = [val_parser]
    
    if domain_file:
        command.append(domain_file)
    if problem_file:
        command.append(problem_file)
        
    if not(domain_file or problem_file):
        raise Exception("PDDL files not found. Must have passed at least PDDL domain.")

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check if the process was successful
    if result.returncode == 0:
        output = result.stdout.decode()
        output = extract_errors_warnings(output)
        return output if output else None
    else:
        print("Parsing failed.")
        error = result.stderr.decode()
        raise Exception(error)
          
def extract_errors_warnings(text):
    lines = text.split('\n')
    relevant_lines = []
    capture = False
    
    for line in lines:
        if "Error:" in line or "Warning:" in line:
            capture = True
        if capture:
            relevant_lines.append(line)
    
    return "\n".join(relevant_lines) if relevant_lines else None

if __name__ == '__main__':

    domain = "data/domain.pddl"
    problem = "data/problem.pddl"
    
    output = parse_pddl(VAL_PARSER, domain_file=domain, problem_file=problem)
    
    if output:
        print("ERROR:\n", output)
    else:
        print("SUCCESS")
        


