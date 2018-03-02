"use strict";

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

    window.history.pushState({}, "", "/?" + uri);

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