import React, { memo } from "react";

import { mapMonthToText } from "../utils";
import { MOOD } from "../../Calendar/utils";
import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<User2023Stata, "months">;

const Calendar = ({ months }: Props) => {
  const getMoodForMonth = (data: { [mood: number]: number }): MOOD => {
    const rates = Object.values(data);

    const max = rates.reduce((acc, currValue, index) => {
      if (index === 0) {
        return acc;
      }

      if (acc < currValue) {
        return currValue;
      }
      return acc;
    }, 0);

    return rates.indexOf(max);
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

  return (
    <div className="flex h-full flex-col items-center font-bold">
      <p className="mt-56 text-xl md:mt-32">
        Каким тебе запомнился каждый месяц
      </p>

      <div className="mt-12 grid grid-cols-4 grid-rows-3 gap-6">
        {Object.entries(months).map(([month, data]) => {
          return (
            <div key={month} className="group flex flex-col items-center">
              <p className="text-4xl">{getMoodEmoji(getMoodForMonth(data))}</p>
              <p className="mt-2 text-xl">{mapMonthToText(Number(month))}</p>
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
