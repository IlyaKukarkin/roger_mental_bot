import React, { memo, useState } from "react";
import { Trans, Plural } from "@lingui/macro";

import { mapMonthToText } from "../utils";
import { MOOD } from "../../Calendar/utils";
import { UserYearlyStata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<UserYearlyStata, "months">;

const Calendar = ({ months }: Props) => {
  const [showMonth, setShowMonth] = useState<number>(-1);

  const getMoodForMonth = (data: { [mood: number]: number }): MOOD => {
    const [_, ...rates] = Object.values(data);

    if (rates.every((rate) => rate === 0)) {
      return 0;
    }

    const max = rates.reduce((acc, currValue) => {
      if (acc < currValue) {
        return currValue;
      }
      return acc;
    }, 0);

    return rates.lastIndexOf(max) + 1;
  };

  const getMoodEmoji = (mood: MOOD) => {
    switch (mood) {
      case MOOD.SKIP:
        return "⚫";
      case MOOD.RED:
        return "🔴";
      case MOOD.ORANGE:
        return "🟠";
      case MOOD.YELLOW:
        return "🟡";
      case MOOD.GREEN:
        return "🟢";
      default:
        return "⚫";
    }
  };

  const onMonthClick = (index: number) => {
    setShowMonth(index === showMonth ? -1 : index);
  };

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <p className="text-3xl">
        <Trans>Каким тебе запомнился каждый месяц</Trans>
      </p>

      <div className="grid grid-cols-4 grid-rows-3 gap-2 md:gap-6">
        {Object.entries(months).map(([month, data]) => {
          return (
            <div
              key={month}
              onClick={() => onMonthClick(Number(month))}
              className="group relative z-50 flex flex-col items-center"
            >
              <p className="text-4xl">{getMoodEmoji(getMoodForMonth(data))}</p>
              <p className="text-base md:text-xl">
                {mapMonthToText(Number(month))}
              </p>
              <p className="invisible text-xs group-hover:visible">
                <Plural
                  value={Object.values(data).reduce(
                    (acc, currValue, index) => acc + (!index ? 0 : currValue),
                    0,
                  )}
                  one="На основе # оценки"
                  _21="На основе # оценки"
                  _31="На основе # оценки"
                  other="На основе # оценок"
                />
              </p>
            </div>
          );
        })}
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(Calendar);
