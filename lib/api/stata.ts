import { FindCursor, ObjectId } from "mongodb";
import { log } from "@logtail/next";

import clientPromise from "../mongodb";
import { APILog, APILogStage } from "./types";

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
};

type UserStata = User & {
  rates: Rate[];
  rate_month: number;
  rate_week2: number;
  rate_week: number;
};

type UserYearly = User & {
  mental_rate_yearly: number;
};

type RatesYearly = {
  totalRates: number;
  _id: ObjectId;
};

type Rate = {
  rate: boolean;
  _id: ObjectId;
  id_user: ObjectId;
  id_message: ObjectId;
  time_to_send: string;
};

export type Statistics = {
  _id: ObjectId;
  year: number;
  users_rate_month: number[];
  users_rate_2week: number[];
  users_rate_week: number[];
  users_rate_yearly: number[];
  support_rates_yearly: number[];
};

const logData: APILog = {
  context: {
    stage: APILogStage.STATISTIC,
  },
};

export const updateUserRateStatistics = async (): Promise<void> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const statisticCol = client.db("roger-bot-db").collection("statistic");

  const users: UserStata[] = await usersCol.aggregate([
    {
      $match: {
        is_active: true,
      },
    },
    {
      $lookup: {
        from: "mental_rate",
        localField: "_id",
        foreignField: "id_user",
        pipeline: [{ $match: { rate: { $ne: 0 } } }],
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

  log.info(
    `Retrieved ${users.length} messages from the database to update statistic`,
    {
      ...logData,
    },
  );

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
    },
  );
};

export const updateYearlyStatistics = async (): Promise<void> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const messagesCol = client.db("roger-bot-db").collection("messages");
  const statisticCol = client.db("roger-bot-db").collection("statistic");

  const currentYear = new Date().getFullYear();

  const startDate = new Date(`${currentYear}-01-01T00:00:00.000+00:00`);
  const endDate = new Date(`${currentYear + 1}-01-01T00:00:00.000+00:00`);

  const prepareUsers = usersCol.aggregate([
    {
      $lookup: {
        from: "mental_rate",
        localField: "_id",
        foreignField: "id_user",
        pipeline: [{ $match: { rate: { $ne: 0 } } }],
        as: "rates",
      },
    },
    {
      $addFields: {
        mental_rate_yearly: {
          $size: {
            $filter: {
              input: "$rates",
              cond: {
                $and: [
                  {
                    $gte: ["$$rate.date", startDate],
                  },
                  {
                    $lte: ["$$rate.date", endDate],
                  },
                ],
              },
              as: "rate",
            },
          },
        },
      },
    },
    {
      $unset: ["rates"],
    },
  ]);

  const prepareMessages = messagesCol.aggregate([
    {
      $lookup: {
        from: "rate",
        localField: "_id",
        foreignField: "id_message",
        pipeline: [
          {
            $match: {
              time_to_send: {
                $gte: new Date(`${currentYear}-01-01T00:00:00.000+00:00`),
                $lte: new Date(`${currentYear + 1}-01-01T00:00:00.000+00:00`),
              },
              rate: {
                $eq: true,
              },
            },
          },
        ],
        as: "rates",
      },
    },
    {
      $addFields: {
        total_rates: {
          $size: "$rates",
        },
      },
    },
    {
      $group: {
        _id: "$id_user",
        totalRates: {
          $sum: "$total_rates",
        },
      },
    },
  ]);

  const [cursorUsers, cursorMessages]: [
    FindCursor<UserYearly>,
    FindCursor<RatesYearly>,
  ] = await Promise.all([prepareUsers, prepareMessages]);

  const [users, rates] = await Promise.all([
    cursorUsers.toArray(),
    cursorMessages.toArray(),
  ]);

  log.info(
    `Retrieved ${users.length} users from the database to update ${currentYear} statistic`,
    {
      ...logData,
    },
  );
  log.info(
    `Retrieved ${rates.length} rates from the database to update ${currentYear} statistic`,
    {
      ...logData,
    },
  );

  const statistic: Statistics = await statisticCol.findOne({
    year: currentYear,
  });

  console.log(statistic);

  const users_rate_yearly: number[] = users.map((user) =>
    Number(user.mental_rate_yearly),
  );
  const support_rates_yearly: number[] = rates.map((rate) =>
    Number(rate.totalRates),
  );

  users_rate_yearly.sort((a, b) => b - a);
  support_rates_yearly.sort((a, b) => b - a);

  statisticCol.update(
    {
      _id: statistic._id,
    },
    {
      $set: {
        users_rate_yearly: users_rate_yearly,
        support_rates_yearly: support_rates_yearly,
      },
    },
  );
};

export const getStatistic = async () => {
  const client = await clientPromise;
  const statisticCol = client.db("roger-bot-db").collection("statistic");

  const currentYear = new Date().getFullYear();

  const statistic: Statistics = await statisticCol.findOne({
    year: currentYear,
  });

  return statistic;
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
