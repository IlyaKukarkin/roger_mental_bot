import { ObjectId, FindCursor } from "mongodb";
import { log } from "@logtail/next";

import clientPromise from "../mongodb";
import {
  getTelegramId,
  deleteMarkupKeyboard,
  sendHurryUpMessage,
  sendThatsItMessage,
} from "../api/users";
import {
  APILog,
  APILogError,
  APILogErrorName,
  APILogStage,
  APILogUser,
} from "./types";

type MentalHours = {
  id_user: ObjectId;
  date: string;
  id_tg_message: number;
  datetime_now: string;
  date_diff: number;
  _id: ObjectId;
  rate: number;
};

const logData: APILog = {
  context: {
    stage: APILogStage.ASK_MOOD,
  },
};

export const checkAndDeleteMoodKeyboard = async (userId: ObjectId) => {
  const logUser: APILogUser = {
    _id: userId,
  };

  log.info(`Start delete mood keyboard`, {
    ...logData,
    user: logUser,
  });

  const client = await clientPromise;
  const mentalRateCol = client.db("roger-bot-db").collection("mental_rate");

  const cursorMentalHours: FindCursor<MentalHours> =
    await mentalRateCol.aggregate([
      {
        $match: {
          id_user: new ObjectId(userId),
          rate: 0,
        },
      },
      {
        $addFields: {
          date_diff: {
            $dateDiff: {
              startDate: "$date",
              endDate: new Date(),
              unit: "hour",
            },
          },
        },
      },
      {
        $sort: {
          date_diff: 1,
        },
      },
      {
        $limit: 1,
      },
    ]);

  const mentalHours = await cursorMentalHours.toArray();

  if (mentalHours && mentalHours.length !== 0 && mentalHours[0].date_diff) {
    try {
      const dateDiff = mentalHours[0].date_diff;
      const userId = mentalHours[0].id_user;
      const tgMessage = mentalHours[0].id_tg_message;

      log.info(`Hours passed from last unanswered mood message`, {
        ...logData,
        user: logUser,
        details: {
          dateDiff,
          tgMessage,
          userId,
        },
      });

      const currentMinutesUTC = new Date().getUTCMinutes();

      if (dateDiff === 3 && currentMinutesUTC < 15) {
        const telegramId = await getTelegramId(userId);
        await sendHurryUpMessage(telegramId);
      }

      if (dateDiff === 9 && currentMinutesUTC < 15) {
        const telegramId = await getTelegramId(userId);
        await deleteMarkupKeyboard(telegramId, tgMessage);
        // await sendThatsItMessage(telegramId);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      const logError: APILogError = {
        name: APILogErrorName.GENERIC,
        trace: errorMessage,
      };

      log.error("Delete mood keyboard error", {
        ...logData,
        user: logUser,
        error: logError,
      });
    }
  }
};
