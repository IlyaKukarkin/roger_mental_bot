import React, { memo, useState } from "react";

import { mapMonthToText } from "../utils";
import { MOOD } from "../../Calendar/utils";
import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<User2023Stata, "months">;

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
    console.log("HERE: ", index);
    setShowMonth(index === showMonth ? -1 : index);
  };

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <p className="text-3xl">Каким тебе запомнился каждый месяц</p>

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
                На основе{" "}
                {Object.values(data).reduce(
                  (acc, currValue, index) => acc + (!index ? 0 : currValue),
                  0,
                )}{" "}
                оценок
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
