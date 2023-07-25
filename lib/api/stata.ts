import { ObjectId } from "mongodb";

import clientPromise from "../mongodb";

type User = {
  _id: ObjectId;
  timezone: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  telegram_username: string;
  name: string;
  is_volunteer: boolean;
  is_banned_from_volunteering: boolean;
  form_id: ObjectId;
  telegram_id: string;
  time_to_send_messages: number;
  rates: Rate[];
  rate_month: number;
  rate_week2: number;
  rate_week: number;
};

type Rate = {
  rate: boolean;
  _id: ObjectId;
  id_user: ObjectId;
  id_message: ObjectId;
  time_to_send: string;
};

type Statistics = {
  _id: ObjectId;
  users_rate_month: number[];
  users_rate_2week: number[];
  users_rate_week: number[];
};

type RateResponse = {
  banned_users: number;
};

export const updateUserRateStatistics = async (): Promise<void> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const statisticCol = client.db("roger-bot-db").collection("statistic");

  const users: User[] = await usersCol.aggregate([
    {
      $lookup: {
        from: "mental_rate",
        localField: "_id",
        foreignField: "id_user",
        as: "rates",
      },
    },
    {
      $addFields: {
        rate_month: {
          $size: {
            $filter: {
              input: "$rates",
              cond: {
                $gte: ["$$rate.date", subtractMonths(1)],
              },
              as: "rate",
            },
          },
        },
        rate_week2: {
          $size: {
            $filter: {
              input: "$rates",
              cond: {
                $gte: ["$$rate.date", subtractWeeks(2)],
              },
              as: "rate",
            },
          },
        },
        rate_week: {
          $size: {
            $filter: {
              input: "$rates",
              cond: {
                $gte: ["$$rate.date", subtractWeeks(1)],
              },
              as: "rate",
            },
          },
        },
      },
    },
  ]);

  const statistic: Statistics = await statisticCol.findOne();

  const updateMonth: number[] = [];
  const updateWeek2: number[] = [];
  const updateWeek: number[] = [];

  for await (const user of users) {
    updateMonth.push(user.rate_month);
    updateWeek2.push(user.rate_week2);
    updateWeek.push(user.rate_week);
  }

  statisticCol.update(
    {
      _id: statistic._id,
    },
    {
      $set: {
        users_rate_month: updateMonth,
        users_rate_2week: updateWeek2,
        users_rate_week: updateWeek,
      },
    }
  );
};

const subtractMonths = (numOfMonths: number, date = new Date()) => {
  const dateCopy = new Date(date.getTime());

  dateCopy.setMonth(dateCopy.getMonth() - numOfMonths);

  return dateCopy;
};

const subtractWeeks = (numOfWeeks: number, date = new Date()) => {
  const dateCopy = new Date(date.getTime());
  dateCopy.setDate(dateCopy.getDate() - numOfWeeks * 7);

  return dateCopy;
};
