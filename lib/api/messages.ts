import { ObjectId } from "mongodb";
import { Asset, Link, Space } from "contentful-management";
import { ContentfulEnvironmentAPI } from "contentful-management/dist/typings/create-environment-api";

const contentful = require("contentful-management");

import clientPromise from "../mongodb";

export type User = {
  name: string;
  user_id: string;
};

export type ImageData = {
  filename: string;
  type: string;
  name: string;
  data: Uint8Array;
};

export type FormDataType = {
  id_user: string;
  text: string;
  media_link?: string;
  image_ids?: string[];
  is_approved: boolean;
  is_anonymous: boolean;
};

export const checkFormId = async (form_id: string): Promise<User | null> => {
  if (!form_id) {
    return null;
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.findOne({ form_id });
  if (results) {
    return { name: results.name, user_id: results._id };
  } else {
    return null;
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

export const submitForm = async (form: FormDataType): Promise<void> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("messages");
  return collection.insertOne({ ...form, id_user: new ObjectId(form.id_user) });
};
