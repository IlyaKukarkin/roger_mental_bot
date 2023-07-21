import type { NextApiRequest, NextApiResponse } from "next";

const multipart = require("parse-multipart-data");

import {
  checkFormId,
  FormDataType,
  ImageData,
  submitForm,
  uploadImage,
} from "../../lib/api/messages";
import { Asset } from "contentful-management";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  switch (req.method) {
    case "GET":
      try {
        const result = await checkFormId(req.query.form_id as string);

        if (result) {
          return res.status(200).json({ name: result });
        }
        return res.status(403).json({});
      } catch (e: any) {
        console.log(e);
        return res.status(500).json({
          error: e.toString(),
        });
      }
    case "PUT":
      try {
        const contentType = req.headers["content-type"];
        const boundary = contentType?.slice(
          contentType?.indexOf("boundary=") + 9
        );

        const chunks: Uint8Array[] = [];
        req.on("data", (chunk) => {
          chunks.push(chunk);
        });
        req.on("end", async () => {
          const body = Buffer.concat(chunks);

          if (body && boundary) {
            const parts = multipart.parse(body, boundary);

            try {
              const uploadArr = await Promise.all([
                ...parts.map((img: ImageData) => uploadImage(img)),
              ]);

              return res
                .status(200)
                .json([...uploadArr.map((asset: Asset) => asset.sys.id)]);
            } catch (e) {
              return res.status(422).json({});
            }
          }

          return res.status(422).json({});
        });
      } catch (e) {
        console.log(e);
        return res.status(422).json({});
      }
      break;
    case "POST":
      try {
        let body = "";
        req.on("data", (data) => {
          body += data;
        });
        req.on("end", async () => {
          try {
            await submitForm(JSON.parse(body) as FormDataType);

            return res.status(200).json({});
          } catch (e) {
            console.log(e);
            return res.status(403).json({ error: "User not found" });
          }
        });
      } catch (e) {
        console.log(e);
        return res.status(422).json({});
      }
      break;
    default:
      return res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
