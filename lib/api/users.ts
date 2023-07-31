import { ObjectId, FindCursor } from "mongodb";
import { log } from "@logtail/next";

import clientPromise from "../mongodb";
import {
  getHurryUpMessage,
  getThatsItMessage,
  getMoodMessage,
} from "../../tg_messages";
import {
  User,
  TgMessage,
  TgResponse,
  APILogUser,
  APILogContext,
  APILogStage,
  APILogError,
  APILogErrorName,
} from "./types";

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

export const getUserByTelegramId = async (
  telegramId: string
): Promise<User | null> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const user = await collection.findOne({ telegram_id: telegramId });

  return user;
};

export const blockUser = async (userId: ObjectId) => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");

  await collection.updateOne(
    { _id: userId },
    {
      $set: {
        is_active: false,
      },
    }
  );
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
): Promise<TgMessage | null> => {
  const context: APILogContext = {
    stage: APILogStage.ASK_MOOD,
  };
  const logUser: APILogUser = {
    telegram_id: userTelegramId,
  };

  log.info(`Start sending mood message with telegram API`, {
    context,
    user: logUser,
  });

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

  // Сообщение приветствие, пока убрали, чтобы бот меньше спамил
  // await fetch(`https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${userTelegramId}&text=${getGreetingsMessage()}&parse_mode=Markdown`, { method: 'POST' })

  try {
    const resp = await fetch(
      `https://api.telegram.org/bot${
        process.env.ROGER_TOKEN_BOT
      }/sendMessage?chat_id=${userTelegramId}&text=${getMoodMessage()}&parse_mode=Markdown&reply_markup=${JSON.stringify(
        buttons
      )}`,
      { method: "POST" }
    );

    const data: TgResponse = await resp.json();

    if (data.ok) {
      log.info(`Send mood message success`, {
        context,
        user: logUser,
        details: data.result,
      });

      return data.result;
    }

    const logError: APILogError = {
      name: APILogErrorName.TELEGRAM_API,
      trace: data.description,
      code: data.error_code,
    };

    if (data.error_code === 403) {
      log.info(`User block the bot`, {
        context,
        user: logUser,
        error: logError,
      });

      const user = await getUserByTelegramId(userTelegramId);

      if (user) {
        await blockUser(user["_id"]);
      }

      return null;
    }

    log.error(`Telegram API error with sending mood message`, {
      context,
      user: logUser,
      error: logError,
    });

    return null;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const logError: APILogError = {
      name: APILogErrorName.GENERIC,
      trace: errorMessage,
    };

    log.error("Send mood error", {
      context,
      user: logUser,
      error: logError,
    });
  }

  return null;
};
