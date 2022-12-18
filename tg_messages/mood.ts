import getMessage from "./utils";

const messages = [
    {
        "id": 1,
        "text": "Как твое настроение сегодня?",
        "frequency": 4
    },
    {
        "id": 2,
        "text": "Как твое моральное состояние под конец дня?",
        "frequency": 2
    },
    {
        "id": 3,
        "text": "Как ты себя чувствуешь?",
        "frequency": 4
    },
    {
        "id": 4,
        "text": "Как прошел твой день?",
        "frequency": 4
    },
    {
        "id": 5,
        "text": "Рассказывай, как ты?",
        "frequency": 4
    },
    {
        "id": 6,
        "text": "Ну что, как день?",
        "frequency": 4
    },
    {
        "id": 7,
        "text": "Как твое настроение под конец дня?",
        "frequency": 4
    },
    {
        "id": 8,
        "text": "Поделишься, как прошел твой день?",
        "frequency": 4
    }
];

export default () => getMessage(messages);