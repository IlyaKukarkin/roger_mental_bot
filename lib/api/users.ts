import { AggregationCursor, ObjectId, FindCursor } from "mongodb";
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
import { countCreatedMessagesByUserYearly } from "./messages";
import { getAllMoodRatesYearly } from "./ask-mood";
import { getStatistic } from "./stata";
import { getYearlyUsersRates } from "./rate";

export type UserYearlyStata = {
  general: {
    totalRates: number;
    totalRatesWithMood: number;
    totalCreatedMessages: number;
    averageUserTotalRates: number;
    userMentalRating: number;
    userSupportRating: number;
  };
  months: {
    [month: number]: {
      [rate: number]: number;
      0: number;
      1: number;
      2: number;
      3: number;
      4: number;
    };
  };
  messages: {
    [messageId: string]: {
      likes: number;
      dislikes: number;
      shows: number;
    };
  };
  userCreatedAt: Date;
  userId: string;
};

export const getTelegramId = async (userId: ObjectId): Promise<string> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const user = await collection.findOne(
    { _id: userId },
    {
      telegram_id: 1,
    },
  );

  return user.telegram_id;
};

export const getUserById = async (userId: ObjectId): Promise<User> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const user = await collection.findOne({ _id: userId });

  return user;
};

export const getUserByTelegramId = async (
  telegramId: string,
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
    },
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
    },
  );

  const adminUsers = await cursorUsers.toArray();

  await Promise.all(
    adminUsers.map(async (user) => {
      try {
        const apiUrl = `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage`;
        await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            chat_id: user.telegram_id,
            text: message,
          }),
        });
      } catch (e) {
        console.log("Ошибка при отправке сообщения Админам: ", e);
      }
    }),
  );
};

export const sendMessageToUser = async (
  userTelegramId: string,
  message: string,
  removeHTMLpreview = false,
): Promise<void> => {
  const apiUrl = `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage`;
  await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      chat_id: userTelegramId,
      text: message,
      disable_web_page_preview: removeHTMLpreview,
    }),
  });
};

export const sendMessageToUserShard = async (
  bucketHex: string,
): Promise<{ sent: number; sentUsersIds: ObjectId[] }> => {
  const bucket = bucketHex.trim().toLowerCase();

  if (!/^[0-9a-f]$/.test(bucket)) {
    throw new Error("Bucket must be a single hex character (0-9 or a-f)");
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");

  // Match active users whose ObjectId last hex character equals the bucket.
  const cursor = collection.aggregate([
    { $match: { is_active: true } },
    {
      $match: {
        $expr: {
          $eq: [
            { $substrBytes: [{ $toString: "$_id" }, 23, 1] },
            bucket,
          ],
        },
      },
    },
    { $project: { telegram_id: 1, _id: 1 } },
  ]) as AggregationCursor<Pick<User, "telegram_id" | '_id'>>;

  let sent = 0;
  const sentUsersIds: ObjectId[] = [];

  const year = 2025
  const link = `https://rogerbot.tech/${year}/`;

  for await (const user of cursor) {
    const messageText = `Привет, друг! 💙

Я подготовил статистику по твоему настроению в уходящем ${year} году. Переходи по ссылке и узнай:
1. каким цветом можно описать твой год и каждый месяц
2. сколько человек стали счастливее благодаря твоей поддержке
3. каким ты запомнишь этот год

Твоя статистика доступна по ссылке ${link}${user._id}

А если тебе нравится пользоваться Роджером, поделись своей статистикой в соцсетях! Тогда еще больше людей смогут следить за своим настроением вместе со мной 😌

С наступающим Новым годом! Надеюсь, твой следующий год будет только в 🟢 цветах.

Твой новогодний Роджер 🎄
`;
    await sendMessageToUser(user.telegram_id, messageText, true);

    sentUsersIds.push(user._id);
    sent += 1;
  }

  return { sent, sentUsersIds };
};

export const sendHurryUpMessage = async (
  userTelegramId: string,
): Promise<void> => {
  await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getHurryUpMessage()}`,
    { method: "POST" },
  );
};

export const sendThatsItMessage = async (
  userTelegramId: string,
): Promise<void> => {
  await fetch(
    `https://api.telegram.org/bot${
      process.env.ROGER_TOKEN_BOT
    }/sendMessage?chat_id=${userTelegramId}&text=${getThatsItMessage()}`,
    { method: "POST" },
  );
};

export const deleteMarkupKeyboard = async (
  userTelegramId: string,
  messageId: number,
) => {
  return await fetch(
    `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/editMessageReplyMarkup?chat_id=${userTelegramId}&message_id=${messageId}&reply_markup=`,
    { method: "POST" },
  );
};

export const sendMoodMessage = async (
  userTelegramId: string,
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
        buttons,
      )}`,
      { method: "POST" },
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

export const getUserYearlyStata = async (userId: ObjectId) => {
  const [totalCreatedMessages, messagesRates, moodRates, statistic, user] =
    await Promise.all([
      countCreatedMessagesByUserYearly(userId),
      getYearlyUsersRates(userId),
      getAllMoodRatesYearly(userId),
      getStatistic(),
      getUserById(userId),
    ]);

  const result: Omit<UserYearlyStata, "userId"> = {
    general: {
      totalRates: 0,
      totalRatesWithMood: 0,
      totalCreatedMessages,
      averageUserTotalRates: 0,
      userMentalRating: 0,
      userSupportRating: 0,
    },
    months: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].reduce(
      (accum, currValue) => {
        return {
          ...accum,
          [currValue]: {
            0: 0, // No rate
            1: 0, // Red mood rate
            2: 0, // Orange mood rate
            3: 0, // Yellow mood rate
            4: 0, // Green mood rate
          },
        };
      },
      {},
    ),
    messages: {},
    userCreatedAt: new Date(user.created_at),
  };

  result.messages = messagesRates.reduce((accum, currValue) => {
    return {
      ...accum,
      [currValue._id.toString()]: {
        likes: currValue.likes,
        dislikes: currValue.dislikes,
        shows: currValue.show,
      },
    };
  }, {});

  moodRates.forEach((rate) => {
    // Count by month
    result.months[new Date(rate.date).getMonth()][rate.rate] += 1;

    // Count global
    result.general.totalRates += 1;

    if (rate.rate) {
      result.general.totalRatesWithMood += 1;
    }
  });

  if (statistic.users_rate_yearly) {
    result.general.averageUserTotalRates =
      statistic.users_rate_yearly.reduce(
        (accum, currValue) => accum + currValue,
        0,
      ) / statistic.users_rate_yearly.length;

    const getValidIndex = ([left, curr, right]: [number, number, number]) => {
      if (curr !== -1) {
        return curr;
      }
      if (left !== -1) {
        return left;
      }

      return right;
    };

    // Fallback values
    const mentalFallbacks: [number, number, number] = [
      statistic.users_rate_yearly.lastIndexOf(
        result.general.totalRatesWithMood - 1,
      ),
      statistic.users_rate_yearly.lastIndexOf(
        result.general.totalRatesWithMood,
      ),
      statistic.users_rate_yearly.lastIndexOf(
        result.general.totalRatesWithMood + 1,
      ),
    ];
    result.general.userMentalRating = getValidIndex(mentalFallbacks) + 1;

    // Fallback values
    const rates = Object.values(messagesRates).reduce(
      (acc, currValue) => acc + currValue.likes,
      0,
    );

    const ratesFallbacks: [number, number, number] = [
      statistic.support_rates_yearly.lastIndexOf(rates - 1),
      statistic.support_rates_yearly.lastIndexOf(rates),
      statistic.support_rates_yearly.lastIndexOf(rates + 1),
    ];
    result.general.userSupportRating = getValidIndex(ratesFallbacks) + 1;
  }

  return {
    result,
  };
};
