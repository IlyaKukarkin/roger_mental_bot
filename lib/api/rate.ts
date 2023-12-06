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
    }
  );

  for await (const message of messages) {
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

        try {
          await sendMessageToUser(
            message.user_telegram_id,
            `Твоё сообщение «${message.text.slice(0, 60)}${
              message.text.length > 60 ? "..." : ""
            }» прошло модерацию и будет показываться тем, кому это важно.%0A%0AСпасибо ❤️%0A%0AСоздать новое сообщение можно через команду /fillform`
          );
        } catch (e) {
          log.error(
            `Error sending "Message was approved" message to the user`,
            {
              ...logData,
              user: {
                telegram_id: message.user_telegram_id,
              },
            }
          );
        }
      } else {
        log.info(`Message send back to review`, logCalculatedResult);

        updateToReview.push(calculatedMessage._id);
      }
    }
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
      docToApproved
    );

    log.info(
      `Updated ${resultApprove.modifiedCount} messages to status "Approve"`,
      { ...logData }
    );
  } else {
    log.info(`Updated 0 messages to status "Approve"`, { ...logData });
  }

  if (updateToReview.length !== 0) {
    const resultReview = await messagesCol.updateMany(
      filterToReview,
      docToReview
    );

    log.info(
      `Updated ${resultReview.modifiedCount} messages to status "Review"`,
      { ...logData }
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
  settings: Settings
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
