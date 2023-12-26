import React, { memo } from "react";
import RogerLink from "./rogerLink";

const End = () => {
  return (
    <div className="flex h-full flex-col items-center justify-center font-bold">
      <div>
        <p className="text-[150px]">🎄</p>
        <p className="text-4xl">С Новым годом!</p>
        <p className="mt-8 text-xl">С любовью и хорошим настроением,</p>
        <p className="mt-2 text-xl">твой Роджер</p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(End);
