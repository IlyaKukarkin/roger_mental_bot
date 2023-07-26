import { ObjectId, FindCursor } from "mongodb";

import clientPromise from "../mongodb";
import { sendMessageToAdmins, sendMoodMessage } from "./users";
import { checkAndDeleteMoodKeyboard } from "./utils";
import { User } from "./types";

type RateToday = {
  current_date: string;
  dateComp: number;
  _id: ObjectId;
  rate: number;
  id_user: ObjectId;
  date: string;
  id_tg_message: number;
};

export const askMood = async (): Promise<Boolean> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const mentalRateCl = client.db("roger-bot-db").collection("mental_rate");

  const cursorUsers: FindCursor<User> = await usersCol.aggregate([
    {
      $match: {
        is_active: true,
      },
    },
    {
      $addFields: {
        current_time: {
          $toDouble: {
            $dateToString: {
              date: new Date(),
              format: "%H",
            },
          },
        },
      },
    },
    {
      $addFields: {
        user_time: {
          $toDouble: "$timezone",
        },
      },
    },
    {
      $addFields: {
        current_user_time: {
          $add: ["$user_time", "$current_time"],
        },
      },
    },
    {
      $addFields: {
        result: {
          $lte: ["$time_to_send_messages", "$current_user_time"],
        },
      },
    },
    {
      $match: {
        result: true,
      },
    },
  ]);

  const users = await cursorUsers.toArray();

  await Promise.all(
    users.map(async (user) => {
      try {
        await checkAndDeleteMoodKeyboard(user._id);

        const sentToday = await checkAlreadySendToday(user._id);

        if (!sentToday) {
          const message = await sendMoodMessage(user.telegram_id);

          await mentalRateCl.insertOne({
            rate: 0,
            id_user: user["_id"],
            date: new Date(),
            id_tg_message: message.message_id,
          });
        }
      } catch (e) {
        console.log("Ошибка при отправке настроения: ", e);
        sendMessageToAdmins(`
          Ошибка при отправке настроения
          Пользователь: ${user.telegram_id}
          Время: ${new Date()}
          Ошибка: ${e}
          `);
      }
    })
  );

  return true;
};

const checkAlreadySendToday = async (userId: ObjectId) => {
  const client = await clientPromise;
  const mentalRateCol = client.db("roger-bot-db").collection("mental_rate");

  const cursorRates: FindCursor<RateToday> = await mentalRateCol.aggregate([
    {
      $match: {
        id_user: new ObjectId(userId),
      },
    },
    {
      $addFields: {
        current_date: {
          $dateToParts: {
            date: new Date(),
          },
        },
      },
    },
    {
      $addFields: {
        current_date: {
          $dateFromParts: {
            year: "$current_date.year",
            month: "$current_date.month",
            day: "$current_date.day",
          },
        },
      },
    },
    {
      $addFields: {
        dateComp: {
          $cmp: ["$current_date", "$date"],
        },
      },
    },
    {
      $match: {
        dateComp: -1,
      },
    },
  ]);

  const rates = await cursorRates.toArray();

  return rates.length !== 0;
};
