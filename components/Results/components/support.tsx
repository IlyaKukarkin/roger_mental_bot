import React, { memo, useMemo } from "react";

import { User2023Stata } from "../../../lib/api/users";

type Props = Pick<User2023Stata, "months" | "messages"> &
  Pick<User2023Stata["general"], "userSupportRating">;

const Support = ({ messages, months, userSupportRating }: Props) => {
  const allBadrates = useMemo(() => {
    let badRates = 0;

    for (let i = 0; i < 12; i++) {
      badRates += months[i][1];
      badRates += months[i][2];
    }

    return badRates;
  }, [months]);

  const countMessageLikes = useMemo(
    () =>
      Object.values(messages).reduce(
        (acc, currValue) => acc + currValue.likes,
        0,
      ),
    [messages],
  );

  const countMessageShows = useMemo(
    () =>
      Object.values(messages).reduce(
        (acc, currValue) => acc + currValue.rates,
        0,
      ),
    [messages],
  );

  return (
    <>
      <p>Поддержка</p>
      <br />

      <p>За год тебя поддержало {allBadrates} человек</p>
      <br />

      <p>Ты создал {Object.keys(messages).length} сообщения</p>
      <p>И получил {countMessageLikes} лайка за год</p>
      <p>За год ты поддержал {countMessageShows} человека.</p>

      <br />
      <p>
        Ты в топ-{userSupportRating} по всему боту по поддержке других
        пользователей!
      </p>
    </>
  );
};

export default memo(Support);
