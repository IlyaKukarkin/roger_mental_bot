import { type Rate } from "./dislike";
import { type Message } from "./messages";

import { FindCursor, ObjectId } from "mongodb";
import { log } from "@logtail/next";

import clientPromise from "../mongodb";
import { sendMessageToUser } from "./users";
import { APILog, APILogStage } from "./types";

type MessageToRate = Message & {
  rates: unknown[];
  admin_good_rates: number;
  admin_bad_rates: number;
  user_good_rates: number;
  user_bad_rates: number;
  user_telegram_id: string;
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
  update_to_approve: number;
  update_to_review: number;
};

export type User2023Rates = {
  // message ID
  _id: ObjectId;
  show: number;
  dislikes: number;
  likes: number;
};

const logData: APILog = {
  context: {
    stage: APILogStage.RATE,
  },
};

export const getCalculatedRates = async (): Promise<RateResponse> => {
  const client = await clientPromise;
  const messagesCol = client.db("roger-bot-db").collection("messages");
  const settingsCol = client.db("roger-bot-db").collection("app_settings");

  const messages: FindCursor<MessageToRate> = await messagesCol.aggregate([
    {
      $lookup: {
        from: "rate",
        localField: "_id",
        foreignField: "id_message",
        pipeline: [
          {
            $lookup: {
              from: "users",
              localField: "id_user",
              foreignField: "_id",
              as: "user",
            },
          },
          {
            $addFields: {
              user: {
                $first: "$user",
              },
            },
          },
        ],
        as: "rates",
      },
    },
    {
      $addFields: {
        admin_good_rates: {
          $filter: {
            input: "$rates",
            cond: {
              $and: [
                {
                  $eq: ["$$item.user.is_admin", true],
                },
                {
                  $eq: ["$$item.rate", true],
                },
              ],
            },
            as: "item",
          },
        },
        admin_bad_rates: {
          $filter: {
            input: "$rates",
            cond: {
              $and: [
                {
                  $eq: ["$$item.user.is_admin", true],
                },
                {
                  $eq: ["$$item.rate", false],
                },
              ],
            },
            as: "item",
          },
        },
        user_good_rates: {
          $filter: {
            input: "$rates",
            cond: {
              $and: [
                {
                  $eq: ["$$item.user.is_admin", false],
                },
                {
                  $eq: ["$$item.rate", true],
                },
              ],
            },
            as: "item",
          },
        },
        user_bad_rates: {
          $filter: {
            input: "$rates",
            cond: {
              $and: [
                {
                  $eq: ["$$item.user.is_admin", false],
                },
                {
                  $eq: ["$$item.rate", false],
                },
              ],
            },
            as: "item",
          },
        },
      },
    },
    {
      $addFields: {
        admin_good_rates: {
          $size: "$admin_good_rates",
        },
        admin_bad_rates: {
          $size: "$admin_bad_rates",
        },
        user_good_rates: {
          $size: "$user_good_rates",
        },
        user_bad_rates: {
          $size: "$user_bad_rates",
        },
      },
    },
    {
      $lookup: {
        from: "users",
        localField: "id_user",
        foreignField: "_id",
        as: "user",
      },
    },
    {
      $unwind: {
        path: "$user",
      },
    },
    {
      $addFields: {
        user_telegram_id: "$user.telegram_id",
      },
    },
    {
      $project: {
        user: 0,
      },
    },
  ]);

  const settings: Settings = await settingsCol.findOne();

  const updateToApproved: ObjectId[] = [];
  const updateToReview: ObjectId[] = [];

  const messagesArray = await messages.toArray();

  log.info(
    `Retrieved ${messagesArray.length} messages from the database to check ratings`,
    {
      ...logData,
    },
  );

  const notifyUsers: { userId: string; messageText: string }[] = [];

  messagesArray.forEach((message) => {
    const calculatedMessage = calculateRate(message, settings);

    const logCalculatedResult = {
      ...logData,
      message,
      details: {
        calculatedMessage,
      },
    };

    if (message.is_approved !== calculatedMessage.is_approved) {
      if (calculatedMessage.is_approved) {
        updateToApproved.push(calculatedMessage._id);

        log.info(`Message approved`, logCalculatedResult);

        notifyUsers.push({
          userId: message.user_telegram_id,
          messageText: message.text,
        });
      } else {
        log.info(`Message send back to review`, logCalculatedResult);

        updateToReview.push(calculatedMessage._id);
      }
    }
  });

  try {
    await Promise.all([
      ...notifyUsers.map(({ userId, messageText }) =>
        sendMessageToUser(
          userId,
          `Твоё сообщение «${messageText.slice(0, 60)}${
            messageText.length > 60 ? "..." : ""
          }» прошло модерацию и будет показываться тем, кому это важно.%0A%0AСпасибо ❤️%0A%0AСоздать новое сообщение можно через команду /fillform`,
        ),
      ),
    ]);
  } catch (e) {
    log.error(`Error sending "Message was approved" message to the users`, {
      ...logData,
    });
  }

  // create a filter to update all messages to "Approve"
  const filterToApproved = {
    _id: {
      $in: updateToApproved,
    },
  };
  // create a filter to update all messages to "Review"
  const filterToReview = {
    _id: {
      $in: updateToReview,
    },
  };
  // increment every document matching the filter with "Approved" state
  const docToApproved = {
    $set: {
      is_approved: true,
    },
  };
  // increment every document matching the filter with "Review" state
  const docToReview = {
    $set: {
      is_approved: false,
    },
  };

  if (updateToApproved.length !== 0) {
    const resultApprove = await messagesCol.updateMany(
      filterToApproved,
      docToApproved,
    );

    log.info(
      `Updated ${resultApprove.modifiedCount} messages to status "Approve"`,
      { ...logData },
    );
  } else {
    log.info(`Updated 0 messages to status "Approve"`, { ...logData });
  }

  if (updateToReview.length !== 0) {
    const resultReview = await messagesCol.updateMany(
      filterToReview,
      docToReview,
    );

    log.info(
      `Updated ${resultReview.modifiedCount} messages to status "Review"`,
      { ...logData },
    );
  } else {
    log.info(`Updated 0 messages to status "Review"`, { ...logData });
  }

  return {
    update_to_approve: updateToApproved.length,
    update_to_review: updateToReview.length,
  };
};

const calculateRate = (
  message: MessageToRate,
  settings: Settings,
): MessageToRate => {
  const {
    approve_number,
    admin_rate_number,
    volunteer_rate_number,
    disaprove_percent,
  } = settings;

  const { admin_bad_rates, admin_good_rates, user_bad_rates, user_good_rates } =
    { ...message };

  const total =
    (admin_bad_rates + admin_good_rates) * admin_rate_number +
    (user_bad_rates + user_good_rates) * volunteer_rate_number;

  const rate =
    admin_good_rates * admin_rate_number +
    user_good_rates * volunteer_rate_number -
    admin_bad_rates * admin_rate_number -
    user_bad_rates * volunteer_rate_number;

  if (total < approve_number) {
    return {
      ...message,
      is_approved: false,
    };
  }

  if (rate / total > disaprove_percent / 100) {
    return {
      ...message,
      is_approved: true,
    };
  }

  return {
    ...message,
    is_approved: false,
  };
};

export const get2023UsersRates = async (userId: ObjectId) => {
  const client = await clientPromise;
  const rateCol = client.db("roger-bot-db").collection("user_messages");

  const rates2023Cursor: FindCursor<User2023Rates> = await rateCol.aggregate([
    {
      $match: {
        time_to_send: {
          $gte: new Date("2023-01-01T00:00:00.000+00:00"),
          $lte: new Date("2024-01-01T00:00:00.000+00:00"),
        },
      },
    },
    {
      $lookup: {
        from: "messages",
        localField: "id_message",
        foreignField: "_id",
        pipeline: [
          {
            $match: {
              id_user: userId,
            },
          },
        ],
        as: "message",
      },
    },
    {
      $match: {
        message: {
          $ne: [],
        },
      },
    },
    {
      $addFields: {
        message: {
          $arrayElemAt: ["$message", 0],
        },
      },
    },
    {
      $group: {
        _id: "$id_message",
        show: {
          $sum: 1,
        },
      },
    },
    {
      $lookup: {
        from: "rate",
        localField: "_id",
        pipeline: [
          {
            $match: {
              time_to_send: {
                $gte: new Date("Sun, 01 Jan 2023 00:00:00 GMT"),
                $lte: new Date("Mon, 01 Jan 2024 00:00:00 GMT"),
              },
            },
          },
        ],
        foreignField: "id_message",
        as: "rates",
      },
    },
    {
      $addFields: {
        dislikes: {
          $size: {
            $filter: {
              input: "$rates",
              as: "item",
              cond: {
                $eq: ["$$item.rate", false],
              },
            },
          },
        },
        likes: {
          $size: {
            $filter: {
              input: "$rates",
              as: "item",
              cond: {
                $eq: ["$$item.rate", true],
              },
            },
          },
        },
      },
    },
    {
      $project: {
        rates: 0,
      },
    },
  ]);

  const rates2023 = await rates2023Cursor.toArray();

  return rates2023;
};
