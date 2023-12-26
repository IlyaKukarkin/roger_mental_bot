import React from "react";
import Image from "next/legacy/image";

import { BOT_LINK } from "../../../../utils/constants";

const RogerLink = () => {
  return (
    <>
      <div className="h-6 w-6"></div>
      <div className="absolute bottom-12 z-50 flex items-end gap-2 justify-self-end">
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
          className="hover:cursor-pointer hover:underline"
        >
          <span>@rogermentalbot</span>
        </a>
      </div>
    </>
  );
};

export default RogerLink;
