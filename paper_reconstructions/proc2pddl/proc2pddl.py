"""
Paper: "PROC2PDDL: Open-Domain Planning Representations from Texts" Zhang et al. (2024)
Source code: https://github.com/zharry29/proc2pddl
Run: python3 -m paper_reconstructions.proc2pddl.proc2pddl
"""

import os, re
from openai import OpenAI
from l2p.llm_builder import GPT_Chat
from l2p.prompt_builder import PromptBuilder
from l2p.domain_builder import DomainBuilder
from l2p.task_builder import TaskBuilder
from l2p.feedback_builder import FeedbackBuilder
from l2p.utils.pddl_parser import format_dict, format_predicates, extract_types
from tests.planner import FastDownward
from tests.setup import check_parse_domain, check_parse_problem
from pddl.parser.domain import DomainParser


def open_file(file_path):
    with open(file_path, 'r') as file:
        file = file.read().strip()
    return file

# engine = "gpt-4o"
# engine = "gpt-3.5-turbo-0125"
engine = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', None))
model = GPT_Chat(client=client, engine=engine)

domain_builder = DomainBuilder()
task_builder = TaskBuilder()
feedback_builder = FeedbackBuilder()
prompt_builder = PromptBuilder()
planner = FastDownward()

# annotated original domain header
types = {
    "object": "Object is always root, everything is an object",
    "children": [
        {
            "item": "",
            "children": [
                {"water": "", "children": []},
                {"wood": "", "children": []},
                {"fire": "", "children": []},
                {"rock": "", "children": []},
                {"leaves": "", "children": []},
                {"tinder": "", "children": []},
                {"raft": "", "children": []},
                {"vines": "", "children": []},
                {"spear": "", "children": []},
                {"fish": "", "children": []}
            ]
        },
        {
            "location": "", 
            "children": [
                {"beach": "", "children": []},
                {"jungle": "", "children": []},
                {"ocean": "", "children": []},
                {"treetop": "", "children": []}
            ]
        },
        {
            "human": "", 
            "children": [
                {"player": "", "children": []},
                {"survivor": "", "children": []}
            ]
        },
        {
            "direction": "", 
            "children": [
                {"in": "", "children": []},
                {"out": "", "children": []},
                {"north": "", "children": []},
                {"south": "", "children": []},
                {"east": "", "children": []},
                {"west": "", "children": []},
                {"up": "", "children": []},
                {"down": "", "children": []}
            ]
        }
    ]
}
    
predicates = [
    {'name': 'treated', 'desc': 'True if the water has been decontaimated by boiling it', 'raw': '(treated ?water - water) ; True if the water has been decontaimated by boiling it', 'params': ['water'], 'clean': '(treated ?water - water)'},
    {'name': 'groove', 'desc': 'True if a small groove is made in wood to start a fire', 'raw': '(groove ?wood - wood) ; True if a small groove is made in wood to start a fire', 'params': ['wood'], 'clean': '(groove ?wood - wood)'},
    {'name': 'at', 'desc': 'an object is at a location', 'raw': '(at ?obj - object ?loc - location) ; an object is at a location', 'params': ['obj', 'loc'], 'clean': '(at ?obj - object ?loc - location)'},
    {'name': 'inventory', 'desc': "an item is in the player's inventory", 'raw': "(inventory ?player ?item) ; an item is in the player's inventory", 'params': ['player', 'item'], 'clean': '(inventory ?player ?item)'},
    {'name': 'connected', 'desc': 'location 1 is connected to location 2 in the direction', 'raw': '(connected ?loc1 - location ?dir - direction ?loc2 - location) ; location 1 is connected to location 2 in the direction', 'params': ['loc1', 'dir', 'loc2'], 'clean': '(connected ?loc1 - location ?dir - direction ?loc2 - location)'},
    {'name': 'has_water_source', 'desc': 'this location has a source of fresh water.', 'raw': '(has_water_source ?loc - location) ; this location has a source of fresh water.', 'params': ['loc'], 'clean': '(has_water_source ?loc - location)'},
    {'name': 'has_wood', 'desc': 'this location has a wood', 'raw': '(has_wood ?loc - location) ; this location has a wood', 'params': ['loc'], 'clean': '(has_wood ?loc - location)'},
    {'name': 'can_light_fire', 'desc': 'this location is safe for lighting a fire', 'raw': '(can_light_fire ?loc - location); this location is safe for lighting a fire', 'params': ['loc'], 'clean': '(can_light_fire ?loc - location)'},
    {'name': 'has_fire', 'desc': 'this location has a fire going', 'raw': '(has_fire ?loc - location); this location has a fire going', 'params': ['loc'], 'clean': '(has_fire ?loc - location)'},
    {'name': 'has_shelter', 'desc': 'this location has a shelter', 'raw': '(has_shelter ?loc - location); this location has a shelter', 'params': ['loc'], 'clean': '(has_shelter ?loc - location)'},
    {'name': 'drank', 'desc': 'the player drinks water', 'raw': '(drank ?water - water); the player drinks water', 'params': ['water'], 'clean': '(drank ?water - water)'},
    {'name': 'has_friend', 'desc': 'the player has found a survivor', 'raw': '(has_friend ?survivor - survivor); the player has found a survivor', 'params': ['survivor'], 'clean': '(has_friend ?survivor - survivor)'},
    {'name': 'has_escaped', 'desc': 'the player has built a raft and left with his fellow survivors', 'raw': '(has_escaped ?player - player) ; the player has built a raft and left with his fellow survivors', 'params': ['player'], 'clean': '(has_escaped ?player - player)'},
    {'name': 'at_ocean', 'desc': 'see if a location has access to the ocean', 'raw': '(at_ocean ?loc - location) ; see if a location has access to the ocean', 'params': ['loc'], 'clean': '(at_ocean ?loc - location)'},
    {'name': 'is_safe', 'desc': 'see if a location is safe to make shelter on', 'raw': '(is_safe ?loc -location) ; see if a location is safe to make shelter on', 'params': ['loc'], 'clean': '(is_safe ?loc -location)'},
    {'name': 'has_fish', 'desc': 'see if location has fish to catch', 'raw': '(has_fish ?loc - location) ; see if location has fish to catch', 'params': ['loc'], 'clean': '(has_fish ?loc - location)'},
    {'name': 'cooked', 'desc': 'see if item is cooked', 'raw': '(cooked ?item - item) ; see if item is cooked', 'params': ['item'], 'clean': '(cooked ?item - item)'},
]

nl_actions = [
    {'go': 'navigate to an adjacent location'},
    {'get': 'pick up an item and put it in the inventory'},
    {'get_water': 'get water from a location that has a water source like a lake.'},
    {'chop_wood': 'chop down wood from a nearby tree.'},
    {'carve_groove': 'create a grove in wood to light flint.'},
    {'light_fire': 'light a fire'},
    {'build_shelter': 'create a grove in wood to light flint.'},
    {'clean_water': 'boil water to clean it'},
    {'drink_water': 'drink water'},
    {'find_other_survivors': 'find other survivors on the deserted island'},
    {'build_raft': 'build a raft to escape the deserted island'},
    {'make_weapon': 'create a spear to hunt fish'},
    {'hunt_fish': 'catch fish with spear'},
    {'cook_fish': 'cook fish'}
]

if __name__ == "__main__":
    
    unsupported_keywords = ['object', 'pddl', 'lisp']
    
    # retrieve wikihow text
    domain_desc = open_file('paper_reconstructions/proc2pddl/prompts/wikihow.txt')

    # ZPD prompt
    role = open_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/role.txt')
    technique = open_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/technique.txt')
    example = open_file('paper_reconstructions/proc2pddl/prompts/zpd_prompt/example.txt')
    task = "here are the actions I want:\n" + (str(nl_actions)) + "\n\nhere are the types I have:\n" + format_dict(types) \
        + "\n\nhere are the predicates I have:\n" + format_predicates(predicates)
    ZPD_prompt = PromptBuilder(role=role, technique=technique, examples=[example], task=task)

    # (1) query LLM for ZPD information
    action_descriptions = model.get_output(prompt=ZPD_prompt.generate_prompt())
    
    # PDDL extraction prompt
    role = open_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/role.txt')
    example = open_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/example.txt')
    task = open_file('paper_reconstructions/proc2pddl/prompts/pddl_translate_prompt/task.txt')
    task += "\n\nhere are the action descriptions to use:\n" + action_descriptions
    pddl_extract_prompt = PromptBuilder(role=role, examples=[example], task=task)
    
    # (2) extract PDDL requirements
    actions, _, llm_response = domain_builder.extract_pddl_actions(
        model=model,
        domain_desc=domain_desc,
        prompt_template=pddl_extract_prompt.generate_prompt(),
        nl_actions=nl_actions,
        predicates=predicates,
        types=types
        )

    types = extract_types(types) # retrieve types
    pruned_types = {name: description for name, description in types.items() if name not in unsupported_keywords} # remove unsupported words
    
    # format strings
    predicate_str = "\n".join([pred["clean"] for pred in predicates])
    types_str = "\n".join(pruned_types)

    requirements = [':strips',':typing',':equality',':negative-preconditions',':disjunctive-preconditions',':universal-preconditions',':conditional-effects']

    # generate domain
    pddl_domain = domain_builder.generate_domain(
        domain="test_domain", 
        requirements=requirements,
        types=types_str,
        predicates=predicate_str,
        actions=actions
        )

    domain_file = "paper_reconstructions/proc2pddl/results/domain.pddl"
    with open(domain_file, "w") as f:
        f.write(pddl_domain)
    
    
    