import type { NextApiRequest, NextApiResponse } from "next";

import { getBannedUsers } from "../../lib/api/dislike";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "POST") {
    try {
      const { authorization } = req.headers;

      if (authorization === `Bearer ${process.env.CRON_API_KEY}`) {
        const updateResult = await getBannedUsers();

        res.status(200).json({ success: true, result: updateResult });
      } else {
        res.status(401).json({ success: false });
      }
    } catch (err) {
      // @ts-ignore
      res.status(500).json({ statusCode: 500, message: err.message });
    }
  } else {
    res.setHeader("Allow", "POST");
    res.status(405).end("Method Not Allowed");
  }
}
