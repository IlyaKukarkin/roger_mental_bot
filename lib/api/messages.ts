import { ObjectId } from "mongodb";
import { Asset, Link, Space } from "contentful-management";
import { ContentfulEnvironmentAPI } from "contentful-management/dist/typings/create-environment-api";

const contentful = require("contentful-management");

import clientPromise from "../mongodb";
import { ADMIN_USER } from "../../utils/constants";

export type ImageData = {
  filename: string;
  type: string;
  name: string;
  data: Uint8Array;
};

export type FormDataType = {
  form_id: string;
  text: string;
  media_link?: string;
  image_ids?: string[];
  is_anonymous: boolean;
};

export const checkFormId = async (form_id: string = ""): Promise<string> => {
  if (!form_id || !ObjectId.isValid(form_id)) {
    return "";
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.findOne({ form_id: new ObjectId(form_id) });

  if (results && results.is_admin) {
    return ADMIN_USER;
  }

  if (results && results.name) {
    return results.name;
  }

  return "";
};

export const uploadImage = async (image: ImageData): Promise<any> => {
  if (
    process.env.CONTENTFUL_SPACE_ID &&
    process.env.CONTENTFUL_MANAGMENT_TOKEN
  ) {
    const client = contentful.createClient({
      accessToken: process.env.CONTENTFUL_MANAGMENT_TOKEN,
    });

    return client
      .getSpace(process.env.CONTENTFUL_SPACE_ID)
      .then((space: Space) => space.getEnvironment("master"))
      .then((environment: ContentfulEnvironmentAPI) =>
        environment.createAssetFromFiles({
          fields: {
            title: {
              "en-US": `${image.filename}-${new Date().getTime()}`,
            },
            description: {
              "en-US": 'Image from "new message" form',
            },
            file: {
              "en-US": {
                contentType: image.type,
                fileName: image.name,
                file: image.data.buffer,
              },
            },
          },
        })
      )
      .then((asset: Asset) => {
        const link: Link<"Tag"> = {
          sys: {
            type: "Link",
            linkType: "Tag",
            id: "messages",
          },
        };

        asset.metadata?.tags.push(link);
        return asset.update();
      })
      .then((asset: Asset) => asset.processForAllLocales())
      .then((asset: Asset) => asset.publish());
  } else {
    throw new Error("Invalid contentful credentials");
  }
};

export const submitForm = async ({
  form_id,
  ...form
}: FormDataType): Promise<void> => {
  const client = await clientPromise;

  const usersCollection = client.db("roger-bot-db").collection("users");
  const user = await usersCollection.findOne({
    form_id: new ObjectId(form_id),
  });

  if (!user) {
    throw new Error("User not found");
  }

  let textToSend =
    "Спасибо, что заполнил форму! Продолжай замерять свое настроение 🙃";
  let textToSend2 = "Скоро я пришлю тебе первый опрос. До встречи!";

  const messages = await usersCollection.aggregate([
    {
      $match: {
        _id: new ObjectId(user._id),
      },
    },
    {
      $lookup: {
        from: "messages",
        localField: "_id",
        foreignField: "id_user",
        as: "messages",
      },
    },
    {
      $addFields: {
        messages: {
          $size: "$messages",
        },
      },
    },
  ]);

  let messageCount = 0;

  for await (const message of messages) {
    messageCount = message.messages;
  }

  if (messageCount === 0) {
    textToSend =
      "Спасибо, что заполнил форму! Я начну показывать сообщение другим пользователям, когда оно пройдет модерацию%0A%0AЧерез 7 дней сможешь увидеть, сколько раз я его показал и какие оценки оно получило. Не забывай каждый день замерять свое настроение, иначе магии не случится 😌";
  }

  const { media_link } = form;
  let short_link = media_link;
  let original_link = media_link;

  if (media_link) {
    const params = new URLSearchParams();
    params.append("key", process.env.CUTTLY_API_KEY || "");
    params.append("short", media_link);
    params.append("userDomain", "0"); // Change to 1 when custom domain is ready

    try {
      const url = new URL(`http://cutt.ly/api/api.php?${params.toString()}`);

      const resp = await fetch(url);
      const linkResp = await resp.json();

      if (linkResp.url.status === 7) {
        short_link = linkResp.url.shortLink;
      }
    } catch (e) {
      throw new Error("Error with URL shortifier");
    }
  }

  if (user && !user.is_admin) {
    await usersCollection.updateOne(
      { _id: new ObjectId(user._id) },
      {
        $set: {
          form_id: new ObjectId(),
        },
      }
    );
  }

  const messageCollection = client.db("roger-bot-db").collection("messages");
  await messageCollection.insertOne({
    ...form,
    is_approved: false,
    media_link: short_link,
    original_media_link: original_link,
    created_date: new Date(),
    id_user: new ObjectId(user._id),
  });

  await fetch(
    `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${user.telegram_id}&text=${textToSend}`,
    { method: "POST" }
  );

  if (messageCount === 0) {
    await fetch(
      `https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${user.telegram_id}&text=${textToSend2}`,
      { method: "POST" }
    );
  }
};
