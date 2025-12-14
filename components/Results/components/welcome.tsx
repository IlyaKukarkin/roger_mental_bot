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
      <div className="">
        <Image
          src="/android-chrome-512x512.png"
          className="h-32 w-32 rounded-full pt-10 dark:bg-gray-500"
          alt="Roger Bot Logo"
          width="200"
          height="200"
        />
      </div>

      <div>
        <p className="-mt-6 text-3xl">
          <Trans>Твоя статистика за год от Роджера</Trans>
        </p>

        <p className="mt-4 text-xl">
          {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
          {new Date().toLocaleDateString()}
        </p>
      </div>

      <p className="text-3xl">
        <Trans>Смотри, каким был твой год 👉</Trans>
      </p>

      <RogerLink />
    </div>
  );
};

export default memo(Welcome);
