type Message = {
    "id": number,
    "text": string,
    "frequency": number,
}

const getMessage = (messages: Message[]): string => {
    const arrWithFrequency: number[] = []

    messages.forEach(message => {
        for (let i = 0; i < message.frequency; i++) {
            arrWithFrequency.push(message.id)
        }
    })

    return messages[arrWithFrequency[Math.floor(Math.random() * arrWithFrequency.length)]].text
}

export default getMessage