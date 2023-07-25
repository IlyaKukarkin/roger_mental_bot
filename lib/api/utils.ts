import { ObjectId, FindCursor } from "mongodb";

import clientPromise from "../mongodb";
import {
  getTelegramId,
  deleteMarkupKeyboard,
  sendHurryUpMessage,
  sendThatsItMessage,
} from "../api/users";

type MentalHours = {


  id_user: ObjectId;
  date: string;
  id_tg_message: number;
  datetime_now: string;
  date_diff: number;
  _id: ObjectId;
  rate: number;
};


export const checkAndDeleteMoodKeyboard = async (userId: ObjectId) => {
  const client = await clientPromise;
  const mentalRateCol = client.db("roger-bot-db").collection("mental_rate");

  const cursorMentalHours: FindCursor<MentalHours> =
    await mentalRateCol.aggregate([
      {
        $match: {
          id_user: new ObjectId(userId),
        },
      },
      {
        $match: {
          rate: 0,
        },
      },
      {
        $addFields: {
          datetime_now: new Date(),
        },
      },
      {
        $addFields: {
          date_diff: {
            $dateDiff: {
              startDate: "$date",
              endDate: "$datetime_now",
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
    const dateDiff = mentalHours[0].date_diff;
    const userId = mentalHours[0].id_user;
    const tgMessage = mentalHours[0].id_tg_message;

    if (dateDiff === 3) {
      const telegramId = await getTelegramId(userId);
      await sendHurryUpMessage(telegramId);
    }

        if (dateDiff === 9) {
            const telegramId = await getTelegramId(userId);
            await deleteMarkupKeyboard(telegramId, tgMessage);
            //await sendThatsItMessage(telegramId);
        }
    }
  }
};
