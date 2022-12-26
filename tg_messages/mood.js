"use strict";
exports.__esModule = true;
var utils_1 = require("./utils");
var messages = [
    {
        "id": 0,
        "text": "Как твое настроение сегодня?",
        "frequency": 4
    },
    {
        "id": 1,
        "text": "Как твое моральное состояние под конец дня?",
        "frequency": 2
    },
    {
        "id": 2,
        "text": "Как ты себя чувствуешь?",
        "frequency": 4
    },
    {
        "id": 3,
        "text": "Как прошел твой день?",
        "frequency": 4
    },
    {
        "id": 4,
        "text": "Рассказывай, как ты?",
        "frequency": 4
    },
    {
        "id": 5,
        "text": "Ну что, как день?",
        "frequency": 4
    },
    {
        "id": 6,
        "text": "Как твое настроение под конец дня?",
        "frequency": 4
    },
    {
        "id": 7,
        "text": "Поделишься, как прошел твой день?",
        "frequency": 4
    }
];
exports["default"] = (function () { return (0, utils_1["default"])(messages); });
