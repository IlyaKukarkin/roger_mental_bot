"use strict";
exports.__esModule = true;
var getMessage = function (messages) {
    var arrWithFrequency = [];
    messages.forEach(function (message) {
        for (var i = 0; i < message.frequency; i++) {
            arrWithFrequency.push(message.id);
        }
    });
    return messages[arrWithFrequency[Math.floor(Math.random() * arrWithFrequency.length)]].text;
};
exports["default"] = getMessage;
