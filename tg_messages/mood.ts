const messages = [
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