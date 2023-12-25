import React, { memo } from "react";
import Image from "next/image";

import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<User2023Stata, "userCreatedAt">;

const Welcome = ({ userCreatedAt }: Props) => {
  const startDate = (createdAt: Date) => {
    const baseDate = new Date("2023-01-01T00:00:00.000+00:00");
    return createdAt > baseDate ? createdAt : baseDate;
  };

  return (
    <div className="flex h-full flex-col items-center font-bold">
      <div className="mt-24">
        <Image
          src="/android-chrome-512x512.png"
          className="h-32 w-32 rounded-full pt-10 dark:bg-gray-500"
          alt="Roger Bot Logo"
          width="200"
          height="200"
        />
      </div>

      <p className="pt-8 text-3xl">Твоя статистика за год от Роджера</p>

      <p className="pt-2 text-xl">
        {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
        {new Date().toLocaleDateString()}
      </p>

      <p className="pt-24 text-3xl md:pt-32">Смотри, каким был твой год 👉</p>

      <RogerLink />
    </div>
  );
};

export default memo(Welcome);
