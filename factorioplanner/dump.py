from collections import defaultdict

from .container import Machine, Recipe


def read_machines(dump):
    machines = {}
    categories = defaultdict(lambda: [])

    for machinename, machineinfo in dump["machines"].items():
        machine = Machine(
            name=machinename,
            categories=set(machineinfo["categories"]),
            max_input_items=machineinfo["max_input_items"],
            speed=machineinfo["speed_multiplier"],
            pollution=machineinfo["pollution"],
            power=machineinfo["power"],
            drain=machineinfo["drain"],
            power_type=machineinfo["power_type"]
        )
        for category in machine.categories:
            machines[machinename] = machine
            categories[category].append(machine)

    return machines, categories


def filter_items(items, ignored_items):
    result = {}
    for key, value in items.items():
        if key not in ignored_items:
            result[key] = value
    return result


def read_recipes(dump, categories, ignored_items):
    recipes = {}
    products = defaultdict(lambda: [])
    educts = defaultdict(lambda: [])

    for recipename, recipeinfo in dump["recipes"].items():
        machines = []
        for machine in categories[recipeinfo["category"]]:
            if machine.max_input_items >= recipeinfo["inputCount"]:
                machines.append(machine)

        try:
            recipe = Recipe(
                recipename,
                items=filter_items(recipeinfo["items"], ignored_items),
                time=recipeinfo["time"],
                machines=machines
            )
        except ValueError as exc:
            print("\x1b[33m%s\x1b[m" % (exc,))
            continue
        recipes[recipename] = recipe
        for item, amount in recipe.items.items():
            if amount < 0:
                educts[item].append(recipe)
            else:
                products[item].append(recipe)

    return recipes, products, educts


def read_dump(dump, ignored_items):
    machines, categories = read_machines(dump)
    recipes, products, educts = read_recipes(dump, categories, ignored_items)
    return machines, categories, recipes, products, educts
