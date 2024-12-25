import type { NextApiRequest, NextApiResponse } from "next";

import { ObjectId } from "mongodb";

import { getUserYearlyStata } from "../../lib/api/users";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  switch (req.method) {
    case "GET":
      try {
        const stata = await getUserYearlyStata(
          new ObjectId(req.query.user_id as string),
        );

        if (stata) {
          return res.status(200).json(stata.result);
        }
        return res.status(403).json({});
      } catch (e: any) {
        console.log(e);
        return res.status(500).json({
          error: e.toString(),
        });
      }
    default:
      return res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
