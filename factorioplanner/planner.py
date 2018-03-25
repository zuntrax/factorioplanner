"""
This file holds functions which perform the planning, and visualize it.
"""

from json import dumps
from math import ceil
from traceback import format_exc
from typing import Dict, List

from yattag import Doc

from .solver import solve
from .dump import read_dump


MACHINES, CATEGORIES, RECIPES, PRODUCTS, EDUCTS, ITEMS = None, None, None, None, None, None

def initialize(dump, ignored_items):
    global MACHINES, CATEGORIES, RECIPES, PRODUCTS, EDUCTS, ITEMS
    MACHINES, CATEGORIES, RECIPES, PRODUCTS, EDUCTS = read_dump(dump, ignored_items)
    ITEMS = set(EDUCTS).union(PRODUCTS)


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
        if recipename.startswith("#"):
            continue
        if '@' in recipename:
            recipename, machinename = recipename.split('@', maxsplit=1)
            try:
                recipe = RECIPES[recipename]
            except KeyError:
                raise ValueError("Unknown recipe %r" % recipename)
            try:
                machine = MACHINES[machinename]
            except KeyError:
                raise ValueError("Unknown machine %r" % machinename)
            if machine not in recipe.machines:
                raise ValueError("Machine %r can't craft %r" % (recipename, machinename))
        else:
            try:
                recipe = RECIPES[recipename]
            except KeyError:
                raise ValueError("Unknown recipe %r" % recipename)
            machine = recipe.machines[0]

        recipelist.append((recipe, machine))
        for item in recipe.items:
            if item not in itemset:
                items.append(item)
                itemset.add(item)

    # sanity-check target and external
    for item in target:
        if item.startswith("#"):
            continue
        if item not in itemset:
            raise ValueError("target item must be in a recipe: %r" % item)
        if item in externalset:
            raise ValueError("target item cannot be an external item: %r" % item)

    for item in externalset:
        if item.startswith("#"):
            continue
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
    def clean(string):
        """ for typo suggestions """
        return "".join(x for x in string if x.isalnum()).lower()

    # the generated HTML document
    doc, tag, text = Doc().tagtext()

    # preprocessing step - gather some helpful aux info
    educt_set, educt_list = set(), []
    product_set, product_list = set(), []
    external_set = set(external)

    for item in external:
        if item not in ITEMS:
            with tag("div", klass="warning"):
                text("Unknown item %r given as external. Did you mean:" % (item,))
            with tag("ul"):
                count = 0
                cleaned = clean(item)
                for i in ITEMS:
                    if cleaned in clean(i):
                        if count >= 5:
                            with tag("li"):
                                text("too many suggestions.")
                            break
                        with tag("li"):
                            with tag("button", onclick="replaceExternal(%s, %s);return false;" % (dumps(item), dumps(i))):
                                text(i)
                        count += 1
                if count == 0:
                    with tag("li"):
                        text("no suggestions found. you suck.")

    for target_item, target_amount in target.items():
        if target_item not in ITEMS:
            with tag("div", klass="warning"):
                text("Unknown item %r given as target. Did you mean:" % (target_item,))
            with tag("ul"):
                count = 0
                cleaned = clean(target_item)
                for i in ITEMS:
                    if cleaned in clean(i):
                        if count >= 5:
                            with tag("li"):
                                text("too many suggestions.")
                            break
                        with tag("li"):
                            with tag("button", onclick="replaceTarget(%s, %s);return false;" % (dumps(target_item), dumps(i))):
                                text(i)
                        count += 1
                if count == 0:
                    with tag("li"):
                        text("no suggestions found. you suck.")
            continue

        if target_amount > 0:
            if target_item not in educt_set:
                educt_set.add(target_item)
                educt_list.append(target_item)
        elif target_amount < 0:
            if target_item not in product_set:
                product_set.add(target_item)
                product_list.append(target_item)
    
    for recipe in recipes:
        if recipe not in RECIPES:
            with tag("div", klass="warning"):
                text("Unknown recipe %r. Did you mean:" % (recipe,))
            with tag("ul"):
                count = 0
                cleaned = clean(recipe)
                for r in RECIPES:
                    if cleaned in clean(r):
                        if count >= 5:
                            with tag("li"):
                                text("too many suggestions.")
                            break
                        with tag("li"):
                            with tag("button", onclick="replaceRecipe(%s, %s);return false;" % (dumps(recipe), dumps(r))):
                                text(r)
                        count += 1
                if count == 0:
                    with tag("li"):
                        text("no suggestions found. you suck.")
            continue
        
        for target_item, target_amount in RECIPES[recipe].items.items():
            if target_amount > 0:
                if target_item not in product_set:
                    product_set.add(target_item)
                    product_list.append(target_item)
            elif target_amount < 0:
                if target_item not in educt_set:
                    educt_set.add(target_item)
                    educt_list.append(target_item)

    educt_set = educt_set.union(external)
    product_set = product_set.union(external)
    
    for educt in educt_list:
        if educt not in product_set:
            with tag("div", klass="warning"):
                text("Cannot produce item %r" % (educt,))

            with tag("ul"):
                with tag("li"):
                    with tag("button", onclick="addExternal(%s);return false;" % (dumps(educt),)):
                        text("Add as external")
                for recipe in PRODUCTS.get(educt, []):
                    with tag("li"):
                        with tag("button", onclick="addRecipe(%s);return false;" % (dumps(recipe.name),)):
                            text("Add recipe %r" % (recipe.name,))

    for product in product_list:
        if product not in educt_set:
            with tag("div", klass="warning"):
                text("Unused item %r" % (product,))

            with tag("ul"):
                with tag("li"):
                    with tag("button", onclick="addExternal(%s);return false;" % (dumps(product),)):
                        text("Add as external")
                for recipe in EDUCTS.get(product, []):
                    with tag("li"):
                        with tag("button", onclick="addRecipe(%s);return false;" % (dumps(recipe.name),)):
                            text("Add recipe %r" % (recipe.name,))

    # actual NNLS step
    try:
        recipes_with_rates, success, result, items = plan(target, recipes, external)
    except BaseException:
        with tag("div", klass="warning"):
            text("Could not plan")
        with tag("pre"):
            text(format_exc())
    else:
        if not success:
            with tag("div", klass="warning"):
                text("No exact solution was found. Linear dependencies between products?")

        # calculate machine info for each recipe
        counts, counts_full, power_el, power_fuel, pollution = [], [], [], [], []
        for recipe, machine, rate in recipes_with_rates:
            counts.append(rate * recipe.time / machine.speed)
            counts_full.append(ceil(counts[-1] - 1e-8))
            if machine.power_type == "electric":
                power_el.append(machine.power * counts[-1] + machine.drain * (counts_full[-1] - counts[-1]))
                power_fuel.append(0)
            else:
                power_el.append(0)
                power_fuel.append(machine.power * counts[-1])

            pollution.append(machine.pollution * counts[-1])

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

                with tag("tr"):
                    with tag("th"): text("Recipe rate")
                    for _, _, rate in recipes_with_rates:
                        number_cell(rate)

                with tag("tr"):
                    with tag("th", rowspan=2): text("Machines")
                    for recipe, machine, _ in recipes_with_rates:
                        with tag("td"):
                            with tag("select", onchange="replaceMachine(%s, e); return false;" % (dumps(recipe.name),)):
                                for m in recipe.machines:
                                    if m is machine:
                                        with tag("option", value=m.name, selected="selected"):
                                            text(m.name)
                                    else:
                                        with tag("option", value=m.name):
                                            text(m.name)

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
                        number_cell(value / 10**3)
                    with tag("td", klass="hfill"): pass
                    with tag("td", klass="noborder"): pass
                    with tag("td", klass="hfill"): pass
                    number_cell(sum(power_el) / 10**3)

                with tag("tr"):
                    with tag("th"): text("Fuel (kW)")
                    for value in power_fuel:
                        number_cell(value / 10**3)
                    with tag("td", klass="hfill"): pass
                    with tag("td", klass="noborder"): pass
                    with tag("td", klass="hfill"): pass
                    number_cell(sum(power_fuel) / 10**3)
                
                with tag("tr"):
                    with tag("th"): text("Pollution")
                    for value in pollution:
                        number_cell(value)
                    with tag("td", klass="hfill"): pass
                    with tag("td", klass="noborder"): pass
                    with tag("td", klass="hfill"): pass
                    number_cell(sum(pollution))

                with tag("tr", klass="vfill"): pass

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
    
    return doc.getvalue()
