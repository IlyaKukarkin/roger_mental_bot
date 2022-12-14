const messages = [
    {
        "id": 0,
        "text": "День прошел — настроение ушло спать. Увидимся завтра! До связи 🙃",
        "frequency": 4
    },
    {
        "id": 1,
        "text": "Похоже, ты уже спишь. Не буду тебя тревожить — напишу еще раз завтра. До встречи 😍",
        "frequency": 4
    },
    {
        "id": 2,
        "text": "*шепотом* Сегодня больше не потревожу тебя — напишу завтра ❤️",
        "frequency": 4
    },
    {
        "id": 3,
        "text": "Покеда, дружок-пирожок! 👋 Напишу завтра",
        "frequency": 4
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