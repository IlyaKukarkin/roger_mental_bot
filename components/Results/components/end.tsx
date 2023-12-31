import React, { memo } from "react";
import { Trans } from "@lingui/macro";

import RogerLink from "./rogerLink";

const End = () => {
  return (
    <div className="flex h-full flex-col items-center justify-center font-bold">
      <div>
        <p className="text-[150px]">🎄</p>
        <p className="text-4xl">
          <Trans>С Новым годом!</Trans>
        </p>
        <p className="mt-8 text-xl">
          <Trans>С любовью и хорошим настроением,</Trans>
        </p>
        <p className="mt-2 text-xl">
          <Trans>твой Роджер</Trans>
        </p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(End);
