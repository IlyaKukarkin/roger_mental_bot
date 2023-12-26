import React, { memo, useMemo } from "react";
import { Trans, Plural } from "@lingui/macro";

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
      <p>
        <Trans>Самый позитивный месяц</Trans>
      </p>
      <p>
        <b>{mapMonthToText(bestMonth)}</b>
      </p>
      <p>
        <Plural
          value={Object.values(months[bestMonth]).reduce(
            (accum, currValue, index) => accum + (index ? currValue : 0),
            0,
          )}
          one="Ты поставил # оценки"
          other="Ты поставил # оценок"
        />
        <Plural
          value={months[bestMonth][4]}
          one=" — из них # зелёная"
          other=" — из них # зелёных"
        />
        <Plural
          value={months[bestMonth][3]}
          one="и # желтая"
          other="и # желтых"
        />
      </p>
      <br />
      <p>
        <Trans>Самый грустный месяц</Trans>
      </p>
      <p>
        <b>{mapMonthToText(worthMonth)}</b>
      </p>
      <p>
        <Plural
          value={Object.values(months[bestMonth]).reduce(
            (accum, currValue, index) => accum + (index ? currValue : 0),
            0,
          )}
          one="Ты поставил # оценки"
          other="Ты поставил # оценок"
        />
        <Plural
          value={months[worthMonth][1]}
          one=" — из них # красный"
          other=" — из них # красных"
        />
        <Plural
          value={months[worthMonth][2]}
          one="и # оранжевой"
          other="и # оранжевых"
        />
      </p>
    </>
  );
};

export default memo(Months);
