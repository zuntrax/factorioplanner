"""
Example test code
"""
from .container import Machine, Recipe
from .server import serve

Machine("assembly", 1, "Assembling machine 1", speed=0.5, power=90, pollution=3, drain=3)
Machine("assembly", 2, "Assembling machine 2", speed=0.75, power=150, pollution=2.4, drain=5)
Machine("assembly", 3, "Assembling machine 3", speed=1.25, power=210, pollution=1.8, drain=7)

Machine("furnace", 1, "Stone furnace", speed=1, power_fuel=180, pollution=1.8)
Machine("furnace", 1, "Steel furnace", speed=2, power_fuel=180, pollution=3.6)
Machine("furnace", 1, "Electric furnace", speed=2, power=180, pollution=0.9, drain=6)

Machine("chemical", 1, "Chemical plant", speed=1.25, power=210, pollution=1.8, drain=7)

Machine("refinery", 1, "Oil refinery", speed=1, power=420, pollution=3.6, drain=14)

Recipe("Iron plate", items={"Iron plate": 1, "Iron ore": -1}, time=3.5, machines={"furnace": 1})
Recipe("Copper plate", items={"Copper plate": 1, "Copper ore": -1}, time=3.5, machines={"furnace": 1})
Recipe("Steel plate", items={"Steel plate": 1, "Iron plate": -5}, time=17.5, machines={"furnace": 1})
Recipe("Copper cable", items={"Copper cable": 2, "Copper plate": -1}, time=0.5, machines={"assembly": 1})
Recipe("Electronic circuit", items={"Electronic circuit": 1, "Copper cable": -3, "Iron plate": -1}, time=0.5, machines={"assembly": 1})
Recipe("Inserter", items={"Inserter": 1, "Electronic circuit": -1, "Iron gear wheel": -1, "Iron plate": -1}, time=0.5, machines={"assembly": 2})
Recipe("Iron gear wheel", items={"Iron gear wheel": 1, "Iron plate": -2}, time=0.5, machines={"assembly": 1})
Recipe("Solar panel", items={"Copper plate": -5, "Steel plate": -5, "Electronic circuit": -15, "Solar panel": 1}, time=10, machines={"assembly": 2})

print("listening on port 8000")
serve(8000)
