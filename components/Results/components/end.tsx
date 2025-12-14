import React, { memo } from "react";
import { Trans } from "@lingui/macro";

import RogerLink from "./rogerLink";

const End = () => {
  return (
    <div className="flex h-full flex-col items-center justify-center font-bold">
      <div className="-mt-12 text-center">
        <div className="flex items-center justify-center gap-2">
          <p className="text-[120px]">🎄</p>
          <p className="animate-pulse text-6xl">✨</p>
        </div>

        <p className="mt-4 text-5xl leading-tight">
          <Trans>С Новым 2025 годом!</Trans>
        </p>

        <div className="mx-auto mt-8 max-w-md rounded-lg bg-gray-700/30 px-6 py-4">
          <p className="text-2xl leading-relaxed text-gray-100">
            <Trans>Береги себя и свое настроение</Trans>
          </p>
        </div>

        <p className="mt-8 text-3xl text-gray-300">
          <Trans>Роджер</Trans> <span className="text-red-400">♥</span>
        </p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(End);
