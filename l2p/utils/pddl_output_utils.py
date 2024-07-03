from collections import OrderedDict
from copy import deepcopy
from addict import Dict
from .logger import Logger
from .pddl_types import Action, Predicate, ParameterList
import re

def combine_blocks(heading_str: str):
    """Combine the inside of blocks from the heading string into a single string."""
    if heading_str.count("```") % 2 != 0:
        Logger.print("WARNING: Could not find an even number of blocks in the heading string")
        Logger.print("#"*10, "LLM Output", "#"*10)
        Logger.print(heading_str)
        Logger.print("#"*30)
        #raise ValueError("Could not find an even number of blocks in the heading string")
    possible_blocks = heading_str.split("```")
    blocks = [possible_blocks[i] for i in range(1, len(possible_blocks), 2)] # Get the text between the ```s, every other one
    combined = "\n".join(blocks) # Join the blocks together
    return combined.replace("\n\n", "\n").strip() # Remove leading/trailing whitespace and internal empty lines

def parse_params(llm_output, include_internal=False):
    params_info = OrderedDict()
    params_heading = llm_output.split('Parameters')[1].strip().split('##')[0]
    params_str = combine_blocks(params_heading)
    for line in params_str.split('\n'):
        if line.strip() == '' or ('.' not in line and not line.strip().startswith('-')):
            print(f"[WARNING] checking param object types - empty line or not a valid line: '{line}'")
            continue
        if not (line.split('.')[0].strip().isdigit() or line.startswith('-')):
            print(f"[WARNING] checking param object types - not a valid line: '{line}'")
            continue
        try:
            p_info = [e for e in line.split(':')[0].split(' ') if e != '']
            param_name, param_type = p_info[1].strip(" `"), p_info[3].strip(" `")
            params_info[param_name] = param_type
        except Exception:
            print(f'[WARNING] checking param object types - fail to parse: {line}')
            continue
    if include_internal:
        precondition_heading = llm_output.split('Preconditions')[1].strip().split('##')[0]
        preconditions_str = combine_blocks(precondition_heading) # Should just be one, but this extracts it easily
        if "forall" in preconditions_str:
            forall_matches = re.findall(r'forall\s*\((.*?)\)', preconditions_str)
            forall_contents = [match.strip() for match in forall_matches]
            for content in forall_contents:
                sub_params = re.findall(r'\?[a-zA-Z0-9]+\s*-\s*[a-zA-Z0-9]+', content)
                for sub_param in sub_params:
                    param_name, param_type = [e.strip() for e in sub_param.split('-')]
                    params_info[param_name] = param_type
        if "exists" in preconditions_str:
            exists_matches = re.findall(r'exists\s*\((.*?)\)', preconditions_str)
            exists_contents = [match.strip() for match in exists_matches]
            for content in exists_contents:
                sub_params = re.findall(r'\?[a-zA-Z0-9]+\s*-\s*[a-zA-Z0-9]+', content)
                for sub_param in sub_params:
                    param_name, param_type = [e.strip() for e in sub_param.split('-')]
                    params_info[param_name] = param_type

    return params_info

def parse_new_predicates(llm_output) -> list[Predicate]:
    new_predicates = list()
    try:
        predicate_heading = llm_output.split('New Predicates\n')[1].strip().split('##')[0]
    except:
        raise Exception("Could not find the 'New Predicates' section in the output. Provide the entire response, including all headings even if some are unchanged.")
    predicate_output = combine_blocks(predicate_heading)
    #Logger.print(f'Parsing new predicates from: \n---\n{predicate_output}\n---\n', subsection=False)
    for p_line in predicate_output.split('\n'):
        if ('.' not in p_line or not p_line.split('.')[0].strip().isdigit()) and not (p_line.startswith('-') or p_line.startswith('(')):
            if len(p_line.strip()) > 0:
                Logger.print(f'[WARNING] unable to parse the line: "{p_line}"', subsection=False)
            continue
        predicate_info = p_line.split(': ')[0].strip(" 1234567890.(-)`").split(' ')
        predicate_name = predicate_info[0]
        predicate_desc = p_line.split(': ')[1].strip() if ": " in p_line else ''

        # get the predicate type info
        if len(predicate_info) > 1:
            predicate_type_info = predicate_info[1:]
            predicate_type_info = [l.strip(" ()`") for l in predicate_type_info if l.strip(" ()`")]
        else:
            predicate_type_info = []
        params = OrderedDict()
        next_is_type = False
        upcoming_params = []
        for p in predicate_type_info:
            if next_is_type:
                if p.startswith('?'):
                    Logger.print(f"[WARNING] `{p}` is not a valid type for a variable, but it is being treated as one. Should be checked by syntax check later.", subsection=False)
                for up in upcoming_params:
                    params[up] = p
                next_is_type = False
                upcoming_params = []
            elif p == '-':
                next_is_type = True
            elif p.startswith('?'):
                upcoming_params.append(p) # the next type will be for this variable
            else:
                Logger.print(f"[WARNING] `{p}` is not corrrectly formatted. Assuming it's a variable name.", subsection=False)
                upcoming_params.append(f"?{p}")
        if next_is_type:
            Logger.print(f"[WARNING] The last type is not specified for `{p_line}`. Undefined are discarded.", subsection=False)
        if len(upcoming_params) > 0:
            Logger.print(f"[WARNING] The last {len(upcoming_params)} is not followed by a type name for {upcoming_params}. These are discarded", subsection=False)

        # generate a clean version of the predicate
        clean = f"({predicate_name} {' '.join([f'{k} - {v}' for k, v in params.items()])}): {predicate_desc}"

        # drop the index/dot
        p_line = p_line.strip(" 1234567890.-`") 
        new_predicates.append({
            'name': predicate_name, 
            'desc': predicate_desc, 
            'raw': p_line,
            'params': params,
            'clean': clean,
        })
    #Logger.print(f"Parsed {len(new_predicates)} new predicates: {[p['name'] for p in new_predicates]}", subsection=False)
    return new_predicates


def parse_predicates(all_predicates):
    """
    This function assumes the predicate definitions adhere to PDDL grammar
    """
    all_predicates = deepcopy(all_predicates)
    for i, pred in enumerate(all_predicates):
        if 'params' in pred:
            continue
        pred_def = pred['raw'].split(': ')[0]
        pred_def = pred_def.strip(" ()`")  # drop any leading/strange formatting
        split_predicate = pred_def.split(' ')[1:]   # discard the predicate name
        split_predicate = [e for e in split_predicate if e != '']

        pred['params'] = OrderedDict()
        for j, p in enumerate(split_predicate):
            if j % 3 == 0:
                assert '?' in p, f'invalid predicate definition: {pred_def}'
                assert split_predicate[j+1] == '-', f'invalid predicate definition: {pred_def}'
                param_name, param_obj_type = p, split_predicate[j+2]
                pred['params'][param_name] = param_obj_type
    return all_predicates

def parse_action(llm_response: str, action_name: str) -> Action:
    """
    Parse an action from a given LLM output.

    Args:
        llm_response (str): The LLM output.
        action_name (str): The name of the action.

    Returns:
        Action: The parsed action.
    """
    #parameters = llm_response.split("Parameters:")[1].split("```")[1].strip()
    parameters = parse_params(llm_response)
    try:
        preconditions = llm_response.split("Preconditions\n")[1].split("##")[0].split("```")[1].strip(" `\n")
    except:
        raise Exception("Could not find the 'Preconditions' section in the output. Provide the entire response, including all headings even if some are unchanged.")
    try:
        effects = llm_response.split("Effects\n")[1].split("##")[0].split("```")[1].strip(" `\n")
    except:
        raise Exception("Could not find the 'Effects' section in the output. Provide the entire response, including all headings even if some are unchanged.")
    return {"name": action_name, "parameters": parameters, "preconditions": preconditions, "effects": effects}


def read_object_types(hierarchy_info):
    obj_types = set()
    for obj_type in hierarchy_info:
        obj_types.add(obj_type)
        if len(hierarchy_info[obj_type]) > 0:
            obj_types.update(hierarchy_info[obj_type])
    return obj_types


def flatten_pddl_output(pddl_str):
    open_parentheses = 0
    old_count = 0
    flat_str = ''
    pddl_lines = pddl_str.strip().split('\n')
    for line_i, pddl_line in enumerate(pddl_lines):
        pddl_line = pddl_line.strip()
        # process parentheses
        for char in pddl_line:
            if char == '(':
                open_parentheses += 1
            elif char == ')':
                open_parentheses -= 1
        if line_i == 0:
            flat_str += pddl_line + '\n'
        elif line_i == len(pddl_lines) - 1:
            flat_str += pddl_line
        else:
            assert open_parentheses >= 1, f'{open_parentheses}'
            leading_space = ' ' if old_count > 1 else '  '
            if open_parentheses == 1:
                flat_str += leading_space + pddl_line + '\n'
            else:
                flat_str += leading_space + pddl_line
        old_count = open_parentheses
    return flat_str


def parse_full_domain_model(llm_output_dict, action_info):
    def find_leftmost_dot(string):
        for i, char in enumerate(string):
            if char == '.':
                return i
        return 0

    parsed_action_info = Dict()
    for act_name in action_info:
        if act_name in llm_output_dict:
            llm_output = llm_output_dict[act_name]['llm_output']
            try:
                # the first part is parameters
                parsed_action_info[act_name]['parameters'] = list()
                params_str = llm_output.split('\nParameters:')[1].strip().split('\n\n')[0]
                for line in params_str.split('\n'):
                    if line.strip() == '' or '.' not in line:
                        continue
                    if not line.split('.')[0].strip().isdigit():
                        continue
                    leftmost_dot_idx = find_leftmost_dot(line)
                    param_line = line[leftmost_dot_idx + 1:].strip()
                    parsed_action_info[act_name]['parameters'].append(param_line)
                # the second part is preconditions
                parsed_action_info[act_name]['preconditions'] = flatten_pddl_output(llm_output.split('Preconditions:')[1].split('```')[1].strip())
                # the third part is effects
                parsed_action_info[act_name]['effects'] = flatten_pddl_output(llm_output.split('Effects:')[1].split('```')[1].strip())
                # include the act description
                parsed_action_info[act_name]['action_desc'] = llm_output_dict[act_name]['action_desc'] if 'action_desc' in llm_output_dict[act_name] else ''
            except:
                print('[ERROR] errors in parsing pddl output')
                print(llm_output)
    return parsed_action_info

def prune_types(types: dict[str,str], predicates: list[Predicate], actions: list[Action]) -> dict[str,str]:
        """
        Prune types that are not used in any predicate or action.

        Args:
            types (list[str]): A list of types.
            predicates (list[Predicate]): A list of predicates.
            actions (list[Action]): A list of actions.

        Returns:
            list[str]: The pruned list of types.
        """

        used_types = {}
        for type in types:
            for pred in predicates:
                if type.split(' ')[0] in pred['params'].values():
                    used_types[type] = types[type]
                    break
            else:
                for action in actions:
                    if type.split(' ')[0] in action['parameters'].values():
                        used_types[type] = types[type]
                        break
                    if type.split(' ')[0] in action['preconditions'] or type.split(' ')[0] in action['effects']: # If the type is included in a "forall" or "exists" statement
                        used_types[type] = types[type]
                        break
        return used_types

def prune_predicates(predicates: list[Predicate], actions: list[Action]) -> list[Predicate]:
    """
    Remove predicates that are not used in any action.

    Args:
        predicates (list[Predicate]): A list of predicates.
        actions (list[Action]): A list of actions.

    Returns:
        list[Predicate]: The pruned list of predicates.
    """
    used_predicates = []
    seen_predicate_names = set()

    for pred in predicates:
        for action in actions:
            # Add a space or a ")" to avoid partial matches 
            names = [f"{pred['name']} ", f"{pred['name']})"]
            for name in names:
                if name in action['preconditions'] or name in action['effects']:
                    if pred['name'] not in seen_predicate_names:
                        used_predicates.append(pred)
                        seen_predicate_names.add(pred['name'])
                    break

    return used_predicates


def extract_types(type_hierarchy: dict[str,str]) -> dict[str,str]:
    def process_node(node, parent_type=None):
        current_type = list(node.keys())[0]
        description = node[current_type]
        parent_type = parent_type if parent_type else current_type

        name = f"{current_type} - {parent_type}" if current_type != parent_type else f"{current_type}"
        desc = f"; {description}"
        
        result[name] = desc

        for child in node.get("children", []):
            process_node(child, current_type)

    result = {}
    process_node(type_hierarchy)
    return result

def shorten_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Only keep the latest LLM output and correction feedback
    """
    if len(messages) == 1:
        return [messages[0]]
    else:
        short_message = [messages[0]] + messages[-2:]
        assert short_message[1]['role'] == 'assistant'
        assert short_message[2]['role'] == 'user'
        return short_message


def mirror_action(action: Action, predicates: list[Predicate]):
    """
    Mirror any symmetrical predicates used in the action preconditions. 

    Example:
        Original action:
        (:action drive
            :parameters (
                ?truck - truck
                ?from - location
                ?to - location
            )
            :precondition
                (and
                    (at ?truck ?from)
                    (connected ?to ?from)
                )
            :effect
                (at ?truck ?to )
            )
        )
        
        Mirrored action:
        (:action drive
            :parameters (
                ?truck - truck
                ?from - location
                ?to - location
            )
            :precondition
                (and
                    (at ?truck ?from)
                    ((connected ?to ?from) or (connected ?from ?to))
                )
            :effect
                (at ?truck ?to )
            )
        )
    """
    mirrored = copy.deepcopy(action)
    for pred in predicates:
        if pred["name"] not in action["preconditions"]:
            continue # The predicate is not used in the preconditions
        param_types = list(pred["params"].values())
        for type in set(param_types): 
            # For each type
            if not param_types.count(type) > 1:
                continue # The type is not repeated
            # The type is repeated
            occs = [i for i, x in enumerate(param_types) if x == type]
            perms = list(itertools.permutations(occs))
            if len(occs) > 2:
                Logger.print(f"[WARNING] Mirroring predicate with {len(occs)} occurences of {type}.", subsection=False)
            uses = re.findall(f"\({pred['name']}.*\)", action["preconditions"]) # Find all occurrences of the predicate used in the preconditions
            for use in uses:
                versions = [] # The different versions of the predicate
                args = [use.strip(" ()").split(" ")[o+1] for o in occs] # The arguments of the predicate
                template = use
                for i, arg in enumerate(args): # Replace the arguments with placeholders
                    template = template.replace(arg, f"[MIRARG{i}]", 1)
                for perm in perms:
                    ver = template
                    for i, p in enumerate(perm):
                        # Replace the placeholders with the arguments in the permutation
                        ver = ver.replace(f"[MIRARG{i}]", args[p])
                    if ver not in versions:
                        versions.append(ver) # In case some permutations are the same (repeated args)
                combined = "(" + " or ".join(versions) + ")"
                mirrored["preconditions"] = mirrored["preconditions"].replace(use, combined)
    return mirrored