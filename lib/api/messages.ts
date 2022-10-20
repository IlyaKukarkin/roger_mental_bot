import { ObjectId } from "mongodb";
import { Asset, Link, Space } from "contentful-management";
import { ContentfulEnvironmentAPI } from "contentful-management/dist/typings/create-environment-api";

const contentful = require("contentful-management");

import clientPromise from "../mongodb";

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
  is_approved: boolean;
  is_anonymous: boolean;
};

export const checkFormId = async (form_id: string = ""): Promise<string> => {
  if (!form_id || !ObjectId.isValid(form_id)) {
    return "";
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.findOne({ form_id: new ObjectId(form_id) });

  if (results && results.name) {
    return results.name;
  } else {
    return "";
  }
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
  return messageCollection.insertOne({
    ...form,
    created_date: new Date(),
    id_user: new ObjectId(user._id),
  });
};
