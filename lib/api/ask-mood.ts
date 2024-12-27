import { ObjectId, FindCursor } from "mongodb";
import { log } from "@logtail/next";

import clientPromise from "../mongodb";
import { sendMoodMessage } from "./users";
import { checkAndDeleteMoodKeyboard } from "./utils";
import {
  UserSendMessage,
  APILog,
  APILogStage,
  APILogError,
  APILogErrorName,
} from "./types";

type MentalRate = {
  _id: ObjectId;
  rate: number;
  id_user: ObjectId;
  date: string;
  id_tg_message: number;
};

type MentalRateToday = MentalRate & {
  current_date: string;
  dateComp: number;
};

const logData: APILog = {
  context: {
    stage: APILogStage.ASK_MOOD,
  },
};

export const askMood = async (): Promise<Boolean> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const mentalRateCl = client.db("roger-bot-db").collection("mental_rate");

  const cursorUsers: FindCursor<UserSendMessage> = await usersCol.aggregate([
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
        current_user_time_negative: {
          $add: ["$user_time", "$current_time", 24],
        },
      },
    },
    {
      $addFields: {
        result: {
          $or: [
            {
              $lte: ["$time_to_send_messages", "$current_user_time"],
            },
            {
              $lte: ["$time_to_send_messages", "$current_user_time_negative"],
            },
          ],
        },
      },
    },
  ]);

  const users = await cursorUsers.toArray();
  const usersToSend = users.filter((user) => user.result);

  log.info(
    `Retrieved ${users.length} users from the database, time has come for ${usersToSend.length} users`,
    {
      ...logData,
    },
  );

  await Promise.all(
    users.map(async (user) => {
      try {
        log.info(`Start sending mood process`, {
          ...logData,
          user,
        });

        await checkAndDeleteMoodKeyboard(user._id);

        // Проверка, что время для отправки опроса настало
        if (user.result) {
          const sentToday = await checkAlreadySendToday(user._id);

          if (!sentToday) {
            const message = await sendMoodMessage(user.telegram_id);

            if (message) {
              await mentalRateCl.insertOne({
                rate: 0,
                id_user: user["_id"],
                date: new Date(),
                id_tg_message: message.message_id,
              });
            }
          }
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        const logError: APILogError = {
          name: APILogErrorName.GENERIC,
          trace: errorMessage,
        };

        log.error("Send mood error", {
          ...logData,
          user,
          error: logError,
        });
      }
    }),
  );

  return true;
};

const checkAlreadySendToday = async (userId: ObjectId) => {
  const client = await clientPromise;
  const mentalRateCol = client.db("roger-bot-db").collection("mental_rate");

  const cursorRates: FindCursor<MentalRateToday> =
    await mentalRateCol.aggregate([
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

export const getAllMoodRatesYearly = async (userId: ObjectId) => {
  const client = await clientPromise;
  const rateCol = client.db("roger-bot-db").collection("mental_rate");

  const currentYear = new Date().getFullYear();

  const mentalRatesCursor: FindCursor<MentalRate> = await rateCol.aggregate([
    {
      $match: {
        $and: [
          {
            date: {
              $gte: new Date(`${currentYear}-01-01T00:00:00.000+00:00`),
              $lte: new Date(`${currentYear + 1}-01-01T00:00:00.000+00:00`),
            },
          },
          {
            id_user: userId,
          },
        ],
      },
    },
  ]);

  const mentalRates = await mentalRatesCursor.toArray();

  return mentalRates;
};
