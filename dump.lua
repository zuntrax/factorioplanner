-- copy/paste all of the following into the factorio ingame console to perform a dump: /c

dump_recipes = function()
    local out = '{\n  "recipes": {\n    '
    local first = true
    for k, v in pairs(game.player.force.recipes) do
        if first then
            first = false
        else
            out = out .. ',\n    '
        end
        out = out .. '"' .. k .. '": {\n      '
        out = out .. '"items": {'
        local items = {}
        local count = 0
        for _, item in pairs(v.ingredients) do
            local amount = item.amount
            if amount == nil then amount = 1 end
            items[item.name] = -amount
            if item.type ~= "fluid" then
                count = count + 1
            end
        end
        for _, item in pairs(v.products) do
            local amount = item.amount
            if amount == nil then amount = 1 end
            if items[item.name] ~= nil then
                amount = amount + items[item.name]
            end
            items[item.name] = amount
        end
        local firstitem = true
        for name, amount in pairs(items) do
            if firstitem then
                firstitem = false
            else
                out = out .. ', '
            end
            out = out .. '"' .. name .. '": ' .. amount
        end
        out = out .. '},\n      '
        out = out .. '"category": "' .. v.category .. '",\n      '
        out = out .. '"inputCount": ' .. count .. ',\n      '
        out = out .. '"time": ' .. v.energy .. '\n    '
        out = out .. '}'
    end
    out = out .. '\n  },\n  "machines": {\n    '
    first = true
    for k, v in pairs(game.entity_prototypes) do
        local cat = v.crafting_categories
        if cat ~= nil and k ~= "player" then
            if first then
                first = false
            else
                out = out .. ',\n    '
            end

            out = out .. '"' .. k .. '": {'
            out = out .. '\n      "categories": ['
            local firstitem = true
            for category, value in pairs(cat) do
                if value == true then
                    if firstitem then
                        firstitem = false
                    else
                        out = out .. ', '
                    end
                    out = out .. '"' .. category .. '"'
                end
            end
            out = out .. ']'

            out = out .. ',\n      "max_input_items": ' .. v.ingredient_count
            out = out .. ',\n      "speed_multiplier": ' .. v.crafting_speed
            out = out .. ',\n      "power": ' .. (v.energy_usage * 60)

            if v.electric_energy_source_prototype ~= nil then
                out = out .. ',\n      "drain": ' .. (v.electric_energy_source_prototype.drain * 60)
                out = out .. ',\n      "pollution": ' .. (v.electric_energy_source_prototype.emissions * v.energy_usage * 60)
                out = out .. ',\n      "power_type": "electric"'

                if v.burner_prototype ~= nil then
                    error = cannot_be_burner_and_electrical_at_once
                end
            else
                out = out .. ',\n      "drain": 0'
                out = out .. ',\n      "pollution": ' .. (v.burner_prototype.emissions * v.energy_usage * 60)
                out = out .. ',\n      "power_type": "fuel"'
            end
            out = out .. '\n    }'
        end
    end
    out = out .. '\n  }\n}\n'
    return out
end

game.write_file("sft-factorio-planner-export.json", dump_recipes())
