"""
Dataclass container types.

Objects of these classes from this module self-register in class.registry,
from where they can be used later.
"""

from collections import defaultdict, OrderedDict
from typing import Dict, Set, List


class Machine:
    """
    A machine, such as "Liquifier Mk2".
    """
    def __init__(self, name: str, categories: Set[str], max_input_items: int, speed: float, pollution: float, power: float, drain: float, power_type: str):
        self.name = name
        self.categories = categories
        self.max_input_items = max_input_items
        self.speed = speed
        self.pollution = pollution
        self.power = power
        self.drain = drain
        self.power_type = power_type

    def __repr__(self):
        return "Machine(%r)" % (self.name,)


class Recipe:
    """
    One individual recipe.

    Constructor arguments:

    name is the name of the recipe.
    """
    registry = {}

    def __init__(self, name: str, items: Dict[str, float], time: float, machines: List[Machine]):
        self.registry[name] = self

        self.name = name
        self.items = items
        self.time = time
        self.machines = machines
        if not self.machines:
            raise ValueError("no known machine for recipe %r" % name)

    def __repr__(self):
        return "Recipe(%r)" % self.name
