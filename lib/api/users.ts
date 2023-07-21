import { ObjectId, FindCursor } from "mongodb";

import clientPromise from "../mongodb";
import {
  getHurryUpMessage,
  getThatsItMessage,
  getMoodMessage,
  getGreetingsMessage,
} from "../../tg_messages";
import { User, TgMessage } from "./types";

export const getTelegramId = async (userId: ObjectId): Promise<string> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const user = await collection.findOne(
    { _id: userId },
    {
      telegram_id: 1,
    }
  );

  return user.telegram_id;
};

export const getUserByTelegramId = async (telegramId: string) => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const user = await collection.findOne({ telegram_id: telegramId });

  return user;
};

export const sendMessageToAdmins = async (message: string): Promise<void> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const cursorUsers: FindCursor<User> = await collection.find(
    { is_admin: true, is_active: true },
    {
      _id: 0,
      telegram_id: 1,
    }
  );

  const adminUsers = await cursorUsers.toArray();

  await Promise.all(
    adminUsers.map(async (user) => {
      try {
        await fetch(
          `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${user.telegram_id}&text=${message}`,
          { method: "POST" }
        );
      } catch (e) {
        console.log("Ошибка при отправке сообщения Админам: ", e);
      }
    })
  );
};

export const sendMessageToUser = async (
  userTelegramId: string,
  message: string
): Promise<void> => {
  await fetch(
    `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${userTelegramId}&text=${message}`,
    { method: "POST" }
  );
};

export const sendHurryUpMessage = async (
  userTelegramId: string
): Promise<void> => {
  await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getHurryUpMessage()}`,
    { method: "POST" }
  );
};

export const sendThatsItMessage = async (
  userTelegramId: string
): Promise<void> => {
  await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getThatsItMessage()}`,
    { method: "POST" }
  );
};

export const deleteMarkupKeyboard = async (
  userTelegramId: string,
  messageId: number
) => {
  return await fetch(
    `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/editMessageReplyMarkup?chat_id=${userTelegramId}&message_id=${messageId}&reply_markup=`,
    { method: "POST" }
  );
};

export const sendMoodMessage = async (
  userTelegramId: string
): Promise<TgMessage> => {
  const user = await getUserByTelegramId(userTelegramId);

  const client = await clientPromise;
  const mentalRateCl = client.db("roger-bot-db").collection("mental_rate");

  const options = {
    sort: { date: -1 },
    projection: { id_tg_message: 1 },
  };

  const prevMentalRate = await mentalRateCl.findOne(
    { rate: 0, id_user: user["_id"] },
    options
  );

  if (prevMentalRate) {
    await deleteMarkupKeyboard(userTelegramId, prevMentalRate.id_tg_message);
  }

  const buttons = {
    inline_keyboard: [
      [
        {
          text: "🟢",
          callback_data: "green_button_answer",
        },
        {
          text: "🟡",
          callback_data: "yellow_button_answer",
        },
        {
          text: "🟠",
          callback_data: "orange_button_answer",
        },
        {
          text: "🔴",
          callback_data: "red_button_answer",
        },
      ],
    ],
  };

  await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getGreetingsMessage()}&parse_mode=Markdown`,
    { method: "POST" }
  );

  const resp = await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getMoodMessage()}&parse_mode=Markdown&reply_markup=${JSON.stringify(
      buttons
    )}`,
    { method: "POST" }
  );

  const data = await resp.json();

  return data.result;
};
