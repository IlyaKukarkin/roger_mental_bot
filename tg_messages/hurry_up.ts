const messages = [
    {
        "id": 0,
        "text": "Осталось меньше часа, чтобы замерять свое настроение! Успевай тыкнуть по кнопкам выше 🙃",
        "frequency": 4
    },
    {
        "id": 1,
        "text": "Ты тут? Пора отметить свое сегодняшнее настроение — до конца опроса осталось мало времени 🙌",
        "frequency": 4
    },
    {
        "id": 2,
        "text": "Hurry up! Тыкай по кнопкам в опросе выше — иначе они магически пропадут",
        "frequency": 4
    },
    {
        "id": 3,
        "text": "🔥 Замеряй скорее настроение 🔥 Осталось мало времени 🔥",
        "frequency": 2
    }
];

const getMessage = (): string => {
    const arrWithFrequency: number[] = []

    messages.forEach(message => {
        for (let i = 0; i < message.frequency; i++) {
            arrWithFrequency.push(message.id)
        }
    })

    return messages[arrWithFrequency[Math.floor(Math.random() * arrWithFrequency.length)]].text
}

export default getMessage;