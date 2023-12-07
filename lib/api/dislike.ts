import { ObjectId } from "mongodb";

import clientPromise from "../mongodb";
import { sendMessageToAdmins } from "./users";

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
};

export type Rate = {
  rate: boolean;
  _id: ObjectId;
  id_user: ObjectId;
  id_message: ObjectId;
  time_to_send: string;
};

type Settings = {
  _id: ObjectId;
  approve_number: number;
  disaprove_percent: number;
  admin_rate_number: number;
  volunteer_rate_number: number;
  volunteer_messages_in_day: number;
  user_ban_dislikes_in_a_row: number;
  volunteer_ban_dislikes_in_a_row: number;
};

type RateResponse = {
  banned_users: number;
};

export const getBannedUsers = async (): Promise<RateResponse> => {
  const client = await clientPromise;
  const usersCol = client.db("roger-bot-db").collection("users");
  const settingsCol = client.db("roger-bot-db").collection("app_settings");

  const users: User[] = await usersCol.aggregate([
    {
      $lookup: {
        from: "rate",
        localField: "_id",
        foreignField: "id_user",
        pipeline: [
          {
            $sort: {
              time_to_send: 1,
            },
          },
        ],
        as: "rates",
      },
    },
    {
      $match: {
        rates: {
          $ne: [],
        },
        is_banned_from_volunteering: false,
      },
    },
  ]);

  const settings: Settings = await settingsCol.findOne();

  const updateToBlocked: ObjectId[] = [];

  for await (const user of users) {
    const updatedUser = calculateBan(user, settings);

    if (updatedUser.is_banned_from_volunteering) {
      updateToBlocked.push(updatedUser._id);
    }
  }

  // create a filter to update all movies with a 'G' rating
  const filterToBan = {
    _id: {
      $in: updateToBlocked,
    },
  };

  // increment every document matching the filter with Approved state
  const docToBan = {
    $set: {
      is_banned_from_volunteering: true,
    },
  };

  if (updateToBlocked.length !== 0) {
    const resultBan = await usersCol.updateMany(filterToBan, docToBan);

    const resString = `Забанил ${resultBan.modifiedCount} пользователя(ей)`;

    console.log(resString);
    await sendMessageToAdmins(resString);
  } else {
    const resString = `Никого не забанил ;)`;

    console.log(resString);
  }

  return { banned_users: updateToBlocked.length };
};

const calculateBan = (user: User, settings: Settings): User => {
  const { user_ban_dislikes_in_a_row, volunteer_ban_dislikes_in_a_row } =
    settings;

  const { rates } = user;

  const { is_volunteer } = { ...user };

  let countBadRatesInARow = 0;
  let currentBadCount = 0;

  rates.forEach((rate) => {
    if (rate.rate) {
      if (countBadRatesInARow < currentBadCount) {
        countBadRatesInARow = currentBadCount;
      }
      currentBadCount = 0;
    } else {
      currentBadCount += 1;
    }
  });

  if (countBadRatesInARow < currentBadCount) {
    countBadRatesInARow = currentBadCount;
  }

  if (is_volunteer && countBadRatesInARow >= volunteer_ban_dislikes_in_a_row) {
    return {
      ...user,
      is_banned_from_volunteering: true,
    };
  }

  if (!is_volunteer && countBadRatesInARow >= user_ban_dislikes_in_a_row) {
    return {
      ...user,
      is_banned_from_volunteering: true,
    };
  }

  return {
    ...user,
  };
};
