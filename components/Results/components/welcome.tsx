import React, { memo } from "react";
import Image from 'next/image'

import { User2023Stata } from "../../../lib/api/users";
import { BOT_LINK } from "../../../utils/constants";

type Props = Pick<User2023Stata, "userCreatedAt">;

const Welcome = ({ userCreatedAt }: Props) => {
  const startDate = (createdAt: Date) => {
    const baseDate = new Date("2023-01-01T00:00:00.000+00:00");
    return createdAt > baseDate ? createdAt : baseDate;
  };

  return (
    <div className="flex flex-col items-center justify-center gap-10">
      <Image src="/android-chrome-192x192.png" className="h-32 w-32 rounded-full dark:bg-gray-500" alt="Roger Bot Logo" width="128" height="128" />

      <div>
        <p>
          Твоя стата за год от{" "}
          <a
            rel="noopener noreferrer"
            href={BOT_LINK}
            target="_blank"
            className="underline dark:text-violet-400"
          >
            <span>Roger Mental Bot</span>
          </a>
          <br />
          за {/* // ToDo: make dynamic/animated numbers for Date here */}
          {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
          {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default memo(Welcome);
