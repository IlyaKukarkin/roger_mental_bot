import React, { memo } from "react";
import Image from "next/legacy/image";
import { Trans } from "@lingui/macro";

import { UserYearlyStata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<UserYearlyStata, "userCreatedAt">;

const Welcome = ({ userCreatedAt }: Props) => {
  const startDate = (createdAt: Date) => {
    const currentYear = new Date().getFullYear();
    const baseDate = new Date(`${currentYear}-01-01T00:00:00.000+00:00`);
    return createdAt > baseDate ? createdAt : baseDate;
  };

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <div className="flex flex-col items-center">
        <Image
          src="/android-chrome-512x512.png"
          className="h-32 w-32 rounded-full shadow-lg dark:bg-gray-500"
          alt="Roger Bot Logo"
          width="140"
          height="140"
        />
      </div>

      <div className="text-center">
        <p className="-mt-6 text-4xl leading-tight">
          <Trans>Твоя статистика за год от Роджера ✨</Trans>
        </p>

        <div className="mt-6 inline-block rounded-lg bg-gray-700/30 px-6 py-3">
          <p className="text-lg font-semibold text-gray-200">
            {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
            {new Date().toLocaleDateString()}
          </p>
        </div>
      </div>

      <div className="text-2xl">
        <p>
          <Trans>Смотри, каким был твой год</Trans>{" "}
          <span className="animate-pulse text-4xl">👉</span>
        </p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(Welcome);
