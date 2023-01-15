import { ObjectId } from "mongodb";

import clientPromise from "../mongodb";
import { sendMessageToAdmins } from "./users";

type MessageToRate = {
  _id: ObjectId;
  text: string;
  is_anonymous: boolean;
  is_approved: boolean;
  media_link: string;
  image_ids: string[];
  created_date: string;
  id_user: string;
  rates: unknown[];
  admin_good_rates: number;
  admin_bad_rates: number;
  user_good_rates: number;
  user_bad_rates: number;
}

type Settings = {
  _id: ObjectId;
  approve_number: number;
  disaprove_percent: number;
  admin_rate_number: number;
  volunteer_rate_number: number;
  volunteer_messages_in_day: number;
  user_ban_dislikes_in_a_row: number;
  volunteer_ban_dislikes_in_a_row: number;
}

type User = {
  _id: ObjectId;
  telegram_username: string;
  name: string;
  timezone: string;
  is_volunteer: boolean;
  is_banned_from_volunteering: boolean;
  form_id: ObjectId;
  telegram_id: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  time_to_send_messages: number;
}

type RateResponse = {
  update_to_approve: number;
  update_to_review: number;
}

export const getCalculatedRates = async (): Promise<RateResponse> => {
  const client = await clientPromise;
  const messagesCol = client.db("roger-bot-db").collection("messages");
  const settingsCol = client.db("roger-bot-db").collection("app_settings");
  const usersCol = client.db("roger-bot-db").collection("users");

  const messages: MessageToRate[] = await messagesCol.aggregate([
    {
      '$lookup': {
        'from': 'rate',
        'localField': '_id',
        'foreignField': 'id_message',
        'pipeline': [
          {
            '$lookup': {
              'from': 'users',
              'localField': 'id_user',
              'foreignField': '_id',
              'as': 'user'
            }
          }, {
            '$addFields': {
              'user': {
                '$first': '$user'
              }
            }
          }
        ],
        'as': 'rates'
      }
    }, {
      '$addFields': {
        'admin_good_rates': {
          '$filter': {
            'input': '$rates',
            'cond': {
              '$and': [
                {
                  '$eq': [
                    '$$item.user.is_admin', true
                  ]
                }, {
                  '$eq': [
                    '$$item.rate', true
                  ]
                }
              ]
            },
            'as': 'item'
          }
        },
        'admin_bad_rates': {
          '$filter': {
            'input': '$rates',
            'cond': {
              '$and': [
                {
                  '$eq': [
                    '$$item.user.is_admin', true
                  ]
                }, {
                  '$eq': [
                    '$$item.rate', false
                  ]
                }
              ]
            },
            'as': 'item'
          }
        },
        'user_good_rates': {
          '$filter': {
            'input': '$rates',
            'cond': {
              '$and': [
                {
                  '$eq': [
                    '$$item.user.is_admin', false
                  ]
                }, {
                  '$eq': [
                    '$$item.rate', true
                  ]
                }
              ]
            },
            'as': 'item'
          }
        },
        'user_bad_rates': {
          '$filter': {
            'input': '$rates',
            'cond': {
              '$and': [
                {
                  '$eq': [
                    '$$item.user.is_admin', false
                  ]
                }, {
                  '$eq': [
                    '$$item.rate', false
                  ]
                }
              ]
            },
            'as': 'item'
          }
        }
      }
    }, {
      '$addFields': {
        'admin_good_rates': {
          '$size': '$admin_good_rates'
        },
        'admin_bad_rates': {
          '$size': '$admin_bad_rates'
        },
        'user_good_rates': {
          '$size': '$user_good_rates'
        },
        'user_bad_rates': {
          '$size': '$user_bad_rates'
        }
      }
    }
  ]);

  const settings: Settings = await settingsCol.findOne();
  
  const updateToApproved: ObjectId[] = [];
  const updateToReview: ObjectId[] = [];
  //потом убрать
  //await sendMessageToAdmins("Сорри, тут тестово выведу, кому бы написал бот, что его сообщение прошло модерацию 😘")

  for await (const message of messages) {
    const calculatedMessage = calculateRate(message, settings);

    if (message.is_approved !== calculatedMessage.is_approved) {
      if (calculatedMessage.is_approved) {
        updateToApproved.push(calculatedMessage._id)
      //   //тут уведомление пользака, что его сообщение прошло модерацию
      //   const user: User = await usersCol.findOne([
      //     {
      //         '$match': {
      //             '_id': message.id_user
      //         }
      //     }
      // ]);
      //   await sendMessageToAdmins("To: " + user.telegram_id + "\nMessage: " + "Привет! Твое сообщение прошло модерацию и будет показываться пользователям. Спасибо за вклад, обнимаю 😍\n\nТут вывести текст, ссылку и картинку сообщения. " + message.text)
      } else {
        updateToReview.push(calculatedMessage._id)
      }
    }
  }

  // create a filter to update all movies with a 'G' rating
  const filterToApproved = {
    _id: {
      "$in": updateToApproved
    }
  };
  const filterToReview = {
    _id: {
      "$in": updateToReview
    }
  };
  // increment every document matching the filter with Approved state
  const docToApproved = {
    $set: {
      is_approved: true,
    },
  };
  const docToReview = {
    $set: {
      is_approved: false,
    },
  };

  if (updateToApproved.length !== 0) {
    const resultApprove = await messagesCol.updateMany(filterToApproved, docToApproved);

    const resString = `Обновил ${resultApprove.modifiedCount} сообщение(ий) на статус "Аппрув"`

    console.log(resString);
    await sendMessageToAdmins(resString)
  } else {
    const resString = `Нечего обновлять на статус "Аппрув"`
    
    console.log(resString);
    await sendMessageToAdmins(resString)
  }

  if (updateToReview.length !== 0) {
    const resultReview = await messagesCol.updateMany(filterToReview, docToReview);
    
    const resString = `Обновил ${resultReview.modifiedCount} сообщение(ий) на статус "Модерация"`;
    
    console.log(resString);
    await sendMessageToAdmins(resString)
  } else {
    const resString = `Нечего обновлять на статус "Модерация"`
    
    console.log(resString);
    await sendMessageToAdmins(resString)
  }

  return { update_to_approve: updateToApproved.length, update_to_review: updateToReview.length }
};

const calculateRate = (message: MessageToRate, settings: Settings): MessageToRate => {
  const { approve_number, admin_rate_number, volunteer_rate_number, disaprove_percent } = settings;

  const { admin_bad_rates, admin_good_rates, user_bad_rates, user_good_rates } = { ...message }

  const total = (admin_bad_rates + admin_good_rates) * admin_rate_number + (user_bad_rates + user_good_rates) * volunteer_rate_number;

  const rate = (admin_good_rates * admin_rate_number) + (user_good_rates * volunteer_rate_number) - (admin_bad_rates * admin_rate_number) - (user_bad_rates * volunteer_rate_number)

  if (total < approve_number) {
    return {
      ...message,
      is_approved: false
    }
  }

  if (rate / total > disaprove_percent / 100) {
    return {
      ...message,
      is_approved: true
    }
  }

  return {
    ...message,
    is_approved: false
  }
}