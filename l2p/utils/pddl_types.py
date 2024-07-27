"""
This file contains classes of PDDL types
"""

from typing import TypedDict, NewType
from collections import OrderedDict

ParameterList = NewType('ParameterList', OrderedDict[str, str]) # {param_name: param_type}
ObjectList = NewType('ObjectList', dict[str, str]) # {obj_name: obj_type}

class Predicate(TypedDict):
    name: str
    desc: str
    raw: str
    params: ParameterList
    clean: str

class Action(TypedDict):
    name: str
    raw: str
    parameters: ParameterList
    preconditions: str
    effects: str