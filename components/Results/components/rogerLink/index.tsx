import React from "react";
import Image from "next/image";

import { BOT_LINK } from "../../../../utils/constants";

const RogerLink = () => {
  return (
    <div className="flex grow items-end gap-2 pb-4 pt-8">
      <Image
        src="/telegram.png"
        className="h-32 w-32 rounded-full dark:bg-gray-500"
        alt="Roger Bot Logo"
        width="24"
        height="24"
      />
      <a rel="noopener noreferrer" href={BOT_LINK} target="_blank" className="">
        <span>@rogermentalbot</span>
      </a>
    </div>
  );
};

export default RogerLink;
