import React, { memo, useMemo } from "react";

import { User2023Stata } from "../../../lib/api/users";
import { mapMonthToText } from "../utils";

type Props = Pick<User2023Stata, "months">;

const Months = ({ months }: Props) => {
  const bestMonth = useMemo(() => {
    let bestMonth = 0;
    let currGoodRatesCount = months[bestMonth][3] + months[bestMonth][4];

    for (let i = 1; i < 12; i++) {
      if (currGoodRatesCount < months[i][3] + months[i][4]) {
        bestMonth = i;
        currGoodRatesCount = months[i][3] + months[i][4];
      }
    }

    return bestMonth;
  }, [months]);

  const worthMonth = useMemo(() => {
    let worthMonth = 0;
    let currBadRatesCount = months[worthMonth][1] + months[worthMonth][2];

    for (let i = 1; i < 12; i++) {
      if (currBadRatesCount < months[i][1] + months[i][2]) {
        worthMonth = i;
        currBadRatesCount = months[i][1] + months[i][2];
      }
    }

    return worthMonth;
  }, [months]);

  return (
    <>
      <p>Самый позитивный месяц</p>
      <p>
        <b>{mapMonthToText(bestMonth)}</b>
      </p>
      <p>
        Ты поставил{" "}
        {Object.values(months[bestMonth]).reduce(
          (accum, currValue, index) => accum + (index ? currValue : 0),
          0,
        )}{" "}
        оценки — из них {months[bestMonth][4]} зелёных и {months[bestMonth][3]}{" "}
        желтых
      </p>
      <br />
      <p>Самый грустный месяц</p>
      <p>
        <b>{mapMonthToText(worthMonth)}</b>
      </p>
      <p>
        Ты поставил{" "}
        {Object.values(months[worthMonth]).reduce(
          (accum, currValue, index) => accum + (index ? currValue : 0),
          0,
        )}{" "}
        оценки — из них {months[worthMonth][1]} красных и{" "}
        {months[worthMonth][2]} оранжевых
      </p>
    </>
  );
};

export default memo(Months);
