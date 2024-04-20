import type { NextApiResponse } from "next";
import { withLogtail, LogtailAPIRequest } from "@logtail/next";

import { getBannedUsers } from "../../lib/api/dislike";
import {
  CronLogData,
  CronLogError,
  CronLogEvent,
  CronName,
  LogError,
} from "./types";

const CRON_NAME = CronName.DISLIKE;
const logData: CronLogData = {
  name: CRON_NAME,
};

// This function can run for a maximum of 5 minutes
export const config = {
  maxDuration: 300,
};

async function handler(req: LogtailAPIRequest, res: NextApiResponse) {
  if (req.method === "POST") {
    try {
      req.log.info(`${CronLogEvent.START}${CRON_NAME}`, {
        cron: logData,
      });

      const { authorization } = req.headers;

      if (authorization === `Bearer ${process.env.CRON_API_KEY}`) {
        const updateResult = await getBannedUsers();

        req.log.info(`${CronLogEvent.SUCCESS}${CRON_NAME}`, {
          cron: logData,
        });
        res.status(200).json({ success: true, result: updateResult });
      } else {
        const logError: LogError = {
          name: CronLogError.UNAUTHORIZED,
        };
        req.log.warn(`${CronLogEvent.ERROR}${CRON_NAME}`, {
          cron: { ...logData, error: logError },
        });
        res.status(401).json({ success: false });
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      const logError: LogError = {
        name: CronLogError.GENERIC,
        trace: errorMessage,
      };
      req.log.error(`${CronLogEvent.ERROR}${CRON_NAME}`, {
        cron: { ...logData, error: logError },
      });
      res.status(500).json({ statusCode: 500, message: errorMessage });
    }
  } else {
    res.setHeader("Allow", "POST");
    res.status(405).end("Method Not Allowed");
  }
}

export default withLogtail(handler);
