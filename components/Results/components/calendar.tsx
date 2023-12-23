import React, { memo } from "react";

import { mapMonthToText } from "../utils";
import { MOOD, getRateBgColor } from "../../Calendar/utils";
import { User2023Stata } from "../../../lib/api/users";

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

  return (
    <>
      <p>Как тебе запомнился каждый месяц</p>
      <br />
      <div className="grid grid-cols-4 grid-rows-3 gap-6">
        {Object.entries(months).map(([month, data]) => {
          return (
            <div key={month} className="flex flex-col items-center">
              <div
                className={`h-10 w-10 rounded-full opacity-80 ${
                  getRateBgColor[getMoodForMonth(data)]
                }`}
              />
              <p>
                <b>{mapMonthToText(Number(month))}</b>
              </p>
              <p className="text-xs">
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
    </>
  );
};

export default memo(Calendar);
