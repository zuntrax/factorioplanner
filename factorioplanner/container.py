"""
Dataclass container types.

Objects of these classes from this module self-register in class.registry,
from where they can be used later.
"""

from collections import defaultdict, OrderedDict
from typing import Dict


class Machine:
    """
    A machine, such as "Liquifier Mk2".

    Constructor arguments:

    name is the name of the machine.
    level is the level of capability of the machine.
    speed is the crafting speed of the machine.
    powerconsumption is the power consumption, in kW, of the machine.
    pollution is the pollution level of the machine, as given.
    """
    registry = defaultdict(lambda: [])

    def __init__(self, cat, level, name, speed, pollution, power=0, drain=0, power_fuel=0):
        self.registry[cat].append(self)

        self.name = name
        self.cat = cat
        self.level = level
        self.speed = speed
        self.pollution = pollution
        self.power = power
        self.drain = drain
        self.power_fuel = power_fuel

    @classmethod
    def get(cls, cat: str, min_level: int):
        """
        Returns all machines of the given name which meet or exceed the level, as a list.
        """
        result = []
        for machine in cls.registry[cat]:
            if machine.level >= min_level:
                result.append(machine)
        return result

    def __repr__(self):
        return "Machine(%r)" % self.name


class Recipe:
    """
    One individual recipe.

    Constructor arguments:

    name is the name of the recipe.
    """
    registry = {}

    def __init__(self, name, items: Dict[str, int], time: float, machines: Dict[str, int]):
        self.registry[name] = self

        self.name = name
        self.items = items
        self.time = time
        self.machines = OrderedDict()
        self.defaultmachine = None
        for cat, min_level in machines.items():
            for machine in Machine.get(cat, min_level):
                self.machines[machine.name] = machine
                if self.defaultmachine is None:
                    self.defaultmachine = machine
        if not self.machines:
            raise ValueError("no known machine for recipe %r" % name)

    def __repr__(self):
        return "Recipe(%r)" % self.name
