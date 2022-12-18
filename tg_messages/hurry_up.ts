import getMessage from "./utils";

const messages = [
    {
        "id": 1,
        "text": "День заканчивается! Успевай тыкнуть по кнопкам выше 🙃",
        "frequency": 4
    },
    {
        "id": 2,
        "text": "Ты тут? Пора отметить свое сегодняшнее настроение — до конца опроса осталось мало времени 🙌",
        "frequency": 4
    },
    {
        "id": 3,
        "text": "Hurry up! Тыкай по кнопкам в опросе выше",
        "frequency": 4
    },
    {
        "id": 4,
        "text": "🔥 Замеряй скорее настроение 🔥 Осталось мало времени 🔥 ",
        "frequency": 3
    }
];

export default () => getMessage(messages);