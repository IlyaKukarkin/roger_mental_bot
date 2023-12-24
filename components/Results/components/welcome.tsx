import React, { memo } from "react";
import Image from "next/image";

import { User2023Stata } from "../../../lib/api/users";
import { BOT_LINK } from "../../../utils/constants";

type Props = Pick<User2023Stata, "userCreatedAt">;

const Welcome = ({ userCreatedAt }: Props) => {
  const startDate = (createdAt: Date) => {
    const baseDate = new Date("2023-01-01T00:00:00.000+00:00");
    return createdAt > baseDate ? createdAt : baseDate;
  };

  return (
    <div className="flex h-full flex-col items-center gap-16 font-bold">
      <div className="mt-20 md:mt-0">
        <Image
          src="/android-chrome-512x512.png"
          className="h-32 w-32 rounded-full pt-10 dark:bg-gray-500"
          alt="Roger Bot Logo"
          width="200"
          height="200"
        />
      </div>

      <p className="text-3xl">Твоя статистика за год от Роджера</p>

      <p className="text-xl">
        {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
        {new Date().toLocaleDateString()}
      </p>

      <p className="text-3xl">Смотри, каким был твой год 👉</p>

      <div className="flex grow items-end gap-2 pb-4">
        <Image
          src="/telegram.png"
          className="h-32 w-32 rounded-full dark:bg-gray-500"
          alt="Roger Bot Logo"
          width="24"
          height="24"
        />
        <a
          rel="noopener noreferrer"
          href={BOT_LINK}
          target="_blank"
          className=""
        >
          <span>@rogermentalbot</span>
        </a>
      </div>
    </div>
  );
};

export default memo(Welcome);
