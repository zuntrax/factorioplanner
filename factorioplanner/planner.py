"""
This file holds functions which perform the planning, and visualize it.
"""

from math import ceil
from typing import Dict, List

from yattag import Doc

from .solver import solve
from .container import Recipe


def plan(target: Dict[str, float], recipes: List[str], external: List[str]):
    """
    Plans a factory which produces the target items.
    Negative numbers mean the factory disposes of the items.

    Arguments:

    target:
        A dictionary {target item name: amount}
    recipes:
        A list of tuples [recipe name].
        The recipe name may include the '@' character; in this case,
        it is interpreted as recipename@machinename. Otherwise, the lowest-tier
        possible machine is used.
    external:
        A list [item name] of items which are supplied/disposed externally.
        sources.

    Return value:
        (recipes_with_rates, success, b, b_result, A, items)
    """
    # The problem is reduced to a set of linear equations, which are then passed
    # to scipy's nnls solver.
    # If too few resources are marked external, the solver will return a
    # closest-fit attempt, and mark the solution as invalid.

    # the list of recipes, in a further-processed form. contains tuples of (recipe, machine).
    recipelist = []
    # the external items. turn then into a set for logarithmic-time lookups.
    externalset = set(external)
    # the list and set of all item names. the set exists for logarithmic-time lookups.
    items, itemset = [], set()

    if not recipes:
        raise ValueError("No recipes were given")

    # walk through all recipes to fill items and recipelist.
    for recipename in recipes:
        if '@' in recipename:
            recipename, machinename = recipename.split('@', maxsplit=1)
            try:
                recipe = Recipe.registry[recipename]
            except KeyError:
                raise ValueError("Unknown recipe %r" % recipename)
            try:
                machine = recipe.machines[machinename]
            except KeyError:
                raise ValueError("Unknown machine %r" % machinename)
        else:
            try:
                recipe = Recipe.registry[recipename]
            except KeyError:
                raise ValueError("Unknown recipe %r" % recipename)
            machine = next(iter(recipe.machines.values()))

        recipelist.append((recipe, machine))
        for item in recipe.items:
            if item not in itemset:
                items.append(item)
                itemset.add(item)

    # sanity-check target and external
    for item in target:
        if item not in itemset:
            raise ValueError("target item must be in a recipe: %r" % item)
        if item in externalset:
            raise ValueError("target item cannot be an external item: %r" % item)

    for item in externalset:
        if item not in itemset:
            raise ValueError("external item must be in a recipe: %r" % item)

    # prepare A, b and the weights for the solver. they each contain one row per item.
    A = []
    b = []
    item_weights = []
    for item in items:
        A.append([recipe.items.get(item, 0) for (recipe, _) in recipelist])
        b.append(target.get(item, 0))
        item_weights.append(0 if item in externalset else 1 if item not in target else 1024)

    x, success, b_result = solve(A, b, item_weights)

    recipes_with_rates = []
    for idx, rate in enumerate(x):
        recipe, machine = recipelist[idx]
        recipes_with_rates.append((recipe, machine, rate))

    # convert b_result back to a dictionary
    result = {item: b_result[idx] for idx, item in enumerate(items)}

    return recipes_with_rates, success, result, items


def visualize(target: Dict[str, float], recipes: List[str], external: List[str]):
    """
    Internally calls plan() with the given arguments,
    then returns the plan as HTML.
    """
    recipes_with_rates, success, result, items = plan(target, recipes, external)

    # calculate machine info for each recipe
    counts, counts_full, power_el, power_fuel, pollution = [], [], [], [], []
    for recipe, machine, rate in recipes_with_rates:
        counts.append(rate * recipe.time / machine.speed)
        counts_full.append(ceil(counts[-1] - 1e-8))
        power_el.append(machine.power * counts[-1] + machine.drain * (counts_full[-1] - counts[-1]))
        power_fuel.append(machine.power_fuel * counts[-1])
        pollution.append(machine.pollution * counts[-1])

    doc, tag, text = Doc().tagtext()

    with tag("table"):
        with tag("thead"):
            with tag("tr"):
                with tag("th", klass="noborder"): pass
                for recipe, _, _ in recipes_with_rates:
                    with tag("th"): text(recipe.name)
                with tag("th", klass="hfill"): pass
                with tag("th"): text("target")
                with tag("th", klass="hfill"): pass
                with tag("th"): text("result")
        with tag("tbody"):
            def number_cell(number, warning=False):
                """ Adds a table cell that contains the number, if != 0. """
                if number is None or number*number < 1e-10:
                    with tag("td"): pass
                else:
                    if warning:
                        with tag("td", klass="warning"): text("%g" % number)
                    else:
                        with tag("td"): text("%g" % number)

            for item in items:
                with tag("tr"):
                    with tag("th"): text(item)
                    for recipe, _, _ in recipes_with_rates:
                        number_cell(recipe.items.get(item))
                    with tag("td", klass="hfill"): pass
                    if item in external:
                        with tag("td", klass="external"): text("ext")
                    else:
                        number_cell(target.get(item))
                    with tag("td", klass="hfill"): pass
                    number_cell(result.get(item), item not in target and item not in external)

            with tag("tr", klass="vfill"): pass

            with tag("tr"):
                with tag("th"): text("Recipe rate")
                for _, _, rate in recipes_with_rates:
                    number_cell(rate)

            with tag("tr"):
                with tag("th", rowspan=2): text("Machines")
                for _, machine, _ in recipes_with_rates:
                    with tag("td"): text(machine.name)

            with tag("tr"):
                for count in counts:
                    number_cell(count)
                with tag("td", klass="hfill"): pass
                with tag("td", klass="noborder"): pass
                with tag("td", klass="hfill"): pass
                number_cell(sum(counts_full))

            with tag("tr"):
                with tag("th"): text("Electricity (kW)")
                for value in power_el:
                    number_cell(value)
                with tag("td", klass="hfill"): pass
                with tag("td", klass="noborder"): pass
                with tag("td", klass="hfill"): pass
                number_cell(sum(power_el))

            with tag("tr"):
                with tag("th"): text("Fuel (kW)")
                for value in power_fuel:
                    number_cell(value)
                with tag("td", klass="hfill"): pass
                with tag("td", klass="noborder"): pass
                with tag("td", klass="hfill"): pass
                number_cell(sum(power_fuel))
            
            with tag("tr"):
                with tag("th"): text("Pollution")
                for value in pollution:
                    number_cell(value)
                with tag("td", klass="hfill"): pass
                with tag("td", klass="noborder"): pass
                with tag("td", klass="hfill"): pass
                number_cell(sum(pollution))

    if not success:
        with tag("span", klass="warning"):
            text("Could not find an exact solution. Are any recipes or external items missing?")
    
    return doc.getvalue()