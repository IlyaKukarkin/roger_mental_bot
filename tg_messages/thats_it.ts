import getMessage from "./utils";

const messages = [
  {
    id: 0,
    text: "День прошел — настроение ушло спать. Увидимся завтра! До связи 🙃",
    frequency: 4,
  },
  {
    id: 1,
    text: "Похоже, ты уже спишь. Не буду тебя тревожить — напишу еще раз завтра. До встречи 😍",
    frequency: 4,
  },
  {
    id: 2,
    text: "*шепотом* Сегодня больше не потревожу тебя — напишу завтра ❤️",
    frequency: 4,
  },
  {
    id: 3,
    text: "Покеда, дружок-пирожок! 👋 Напишу завтра",
    frequency: 4,
  },
];

export default () => getMessage(messages);
