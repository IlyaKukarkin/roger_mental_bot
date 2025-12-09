import type { NextApiResponse } from "next";
import { withLogtail, LogtailAPIRequest } from "@logtail/next";

import { sendMessageToUserShard } from "../../lib/api/users";
import {
  CronLogData,
  CronLogError,
  CronLogEvent,
  CronName,
  LogError,
} from "./types";

const CRON_NAME = CronName.SEND_LINK_SHARD;
const logData: CronLogData = {
  name: CRON_NAME,
};

// Fixed schedule: 4 slots per day at 14/15/16/17 local time, over Dec 22-25.
// Buckets cover all 16 hex nibbles once, starting with "a" at Dec 22 14:00.
// YEAR is pinned to avoid accidental sends in later years.
const TARGET_YEAR = 2025;
const SCHEDULE: Array<{ month: number; day: number; hour: number; bucket: string }> = [
  { month: 11, day: 22, hour: 14, bucket: "a" },
  { month: 11, day: 22, hour: 15, bucket: "b" },
  { month: 11, day: 22, hour: 16, bucket: "c" },
  { month: 11, day: 22, hour: 17, bucket: "d" },

  { month: 11, day: 23, hour: 14, bucket: "e" },
  { month: 11, day: 23, hour: 15, bucket: "f" },
  { month: 11, day: 23, hour: 16, bucket: "0" },
  { month: 11, day: 23, hour: 17, bucket: "1" },

  { month: 11, day: 24, hour: 14, bucket: "2" },
  { month: 11, day: 24, hour: 15, bucket: "3" },
  { month: 11, day: 24, hour: 16, bucket: "4" },
  { month: 11, day: 24, hour: 17, bucket: "5" },

  { month: 11, day: 25, hour: 14, bucket: "6" },
  { month: 11, day: 25, hour: 15, bucket: "7" },
  { month: 11, day: 25, hour: 16, bucket: "8" },
  { month: 11, day: 25, hour: 17, bucket: "9" },
];

const getBucketHex = (): string | null => {
  const now = new Date();

  if (now.getFullYear() !== TARGET_YEAR) {
    return null;
  }

  const slot = SCHEDULE.find(
    ({ month, day, hour }) =>
      now.getMonth() === month &&
      now.getDate() === day &&
      now.getHours() === hour,
  );

  return slot?.bucket ?? null;
};

async function handler(req: LogtailAPIRequest, res: NextApiResponse) {
  if (req.method === "POST") {
    try {
      req.log.info(`${CronLogEvent.START}${CRON_NAME}`, {
        cron: logData,
      });

      const { authorization } = req.headers;

      if (authorization !== `Bearer ${process.env.CRON_API_KEY}`) {
        const logError: LogError = {
          name: CronLogError.UNAUTHORIZED,
        };
        req.log.warn(`${CronLogEvent.ERROR}${CRON_NAME}`, {
          cron: { ...logData, error: logError },
        });
        res.status(401).json({ success: false });

        return;
      }

      const bucketHex = getBucketHex();

      if (!bucketHex) {
        const logError: LogError = {
          name: CronLogError.GENERIC,
          trace: "Invalid time slot for link broadcast",
        };
        req.log.warn(`${CronLogEvent.ERROR}${CRON_NAME}`, {
          cron: { ...logData, error: logError },
        });
        res.status(400).json({ success: false, error: logError.trace });

        return;
      }

      const { sent, sentUsersIds } = await sendMessageToUserShard(bucketHex);

      req.log.info(`${CronLogEvent.SUCCESS}${CRON_NAME}`, {
        cron: { ...logData, bucketHex, sent, sentUsersIds },
      });
      res.status(200).json({ success: true, bucketHex, sent, sentUsersIds });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
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
