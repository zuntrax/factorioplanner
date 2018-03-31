"use strict";

// https://stackoverflow.com/questions/1418050/string-strip-for-javascript
if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

var requestRunning = false;
var newRequest = false;

function parseParameters() {
    var parameterString = location.search.substring(1);
    let parameters = {};

    for (let parameter of parameterString.split("&")) {
        let idx = parameter.indexOf('=');
        if (idx === -1) {
            console.log("bad parameter string", parameter);
            continue;
        }
        let key = decodeURIComponent(parameter.substr(0, idx));
        let value = decodeURIComponent(parameter.substr(idx + 1));
        if (!(key in parameters))
        {
            parameters[key] = [];
        }
        parameters[key].push(value);
    }

    return parameters;
}

function init() {
    var parameters = parseParameters();

    document.getElementById("targets").value = (parameters["target"] || []).join("\n");
    document.getElementById("recipes").value = (parameters["recipe"] || []).join("\n");
    document.getElementById("externals").value = (parameters["external"] || []).join("\n");

    update();

    document.getElementById("targets").addEventListener("input", update);
    document.getElementById("recipes").addEventListener("input", update);
    document.getElementById("externals").addEventListener("input", update);
}

function addExternal(name) {
    document.getElementById("externals").value += "\n" + name;
    update();
}

function addRecipe(name) {
    document.getElementById("recipes").value += "\n" + name;
    update();
}

function replaceExternal(oldName, newName) {
    let externals = [];
    for (let externalLine of document.getElementById("externals").value.split("\n")) {
        if (externalLine.trim() === oldName) {
            externals.push(newName);
        } else {
            externals.push(externalLine);
        }
    }
    document.getElementById("externals").value = externals.join("\n");
    update();
}

function replaceMachine(recipeName, selection) {
    let recipes = [];
    for (let recipeLine of document.getElementById("recipes").value.split("\n")) {
        if (recipeLine.split("@")[0].trim() === recipeName) {
            recipes.push(recipeName + "@" + selection.value);
        } else {
            recipes.push(recipeLine);
        }
    }
    document.getElementById("recipes").value = recipes.join("\n");
    update();
}

function replaceRecipe(oldName, newName) {
    let recipes = [];
    for (let recipeLine of document.getElementById("recipes").value.split("\n")) {
        if (recipeLine.split("@")[0].trim() === oldName) {
            recipes.push(newName);
        } else {
            recipes.push(recipeLine);
        }
    }
    document.getElementById("recipes").value = recipes.join("\n");
    update();
}

function replaceTarget(oldName, newName) {
    let targets = [];
    for (let targetLine of document.getElementById("targets").value.split("\n")) {
        let parsed = targetLine.split(":")
        let name = parsed[0].trim()
        let amount = parsed[1]
        if (name === oldName) {
            if (typeof amount === "string") {
                targets.push(newName + ":" + amount.trim());
            } else {
                targets.push(newName);
            }
        } else {
            targets.push(targetLine);
        }
    }
    document.getElementById("targets").value = targets.join("\n");
    update();
}

function update() {
    if (requestRunning) { newRequest = true; return; }

    recipes = document.getElementById("recipes").value;
    externals = document.getElementById("externals").value;

    var request = new XMLHttpRequest();
    var uri = "";

    for(let target of document.getElementById("targets").value.split("\n")) {
        uri += "&target=" + encodeURIComponent(target);
    }

    for(let recipe of document.getElementById("recipes").value.split("\n")) {
        uri += "&recipe=" + encodeURIComponent(recipe);
    }

    for(let external of document.getElementById("externals").value.split("\n")) {
        uri += "&external=" + encodeURIComponent(external);
    }

    uri = uri.substr(1);

    window.history.replaceState({}, "", "/?" + uri);

    request.open("GET", "/plan?" + uri);
    request.responseType = "text";
    request.onload = () => {
        document.getElementById("plan").innerHTML = request.response;
        requestRunning = false;
        if (newRequest) {
            newRequest = false;
            update();
        }
    };
    request.send();
}
