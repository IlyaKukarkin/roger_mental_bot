import React, { memo, useMemo } from "react";

import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<User2023Stata, "months" | "messages"> &
  Pick<User2023Stata["general"], "userSupportRating">;

const Support = ({ messages, months, userSupportRating }: Props) => {
  const allBadRates = useMemo(() => {
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

  const supportRatingEmoji = useMemo(() => {
    if (userSupportRating <= 20) {
      return "🏆";
    }

    if (userSupportRating <= 50) {
      return "🥇";
    }

    if (userSupportRating <= 100) {
      return "🥈";
    }

    return "🥉";
  }, [userSupportRating]);

  const renderNoSupport = () => {
    return (
      <>
        <p className="mt-32 text-[100px]">😱</p>

        <p className="mt-6 text-lg">А здесь нет статистики!</p>

        <p className="mt-6 text-lg">
          Создай сообщение по команде /fillform, чтобы начать поддерживать
          других пользователей
        </p>
      </>
    );
  };

  return (
    <div className="flex h-full flex-col items-center font-bold">
      <p className="mt-56 text-xl md:mt-24">В этом году тебя поддержало</p>
      <p className="mt-6 text-3xl">{allBadRates} пользователя</p>

      {Object.keys(messages).length ? (
        <>
          <p className="mt-24 text-2xl">Но ты тоже не отставал!</p>

          <div className="mt-4 grid grid-cols-2 grid-rows-2 items-center justify-center gap-y-8">
            <div className="flex flex-col font-semibold">
              <p>Ты создал</p>
              <p className="text-3xl font-bold">
                {Object.keys(messages).length}
              </p>
              <p>сообщения для поддержки</p>
            </div>
            <div className="flex flex-col font-semibold">
              <p>Ты поддержал</p>
              <p className="text-3xl font-bold">{countMessageShows}</p>
              <p>человека с плохим настроением</p>
            </div>
            <div className="flex flex-col font-semibold">
              <p>Ты получил</p>
              <p className="text-3xl font-bold">{countMessageLikes}</p>
              <p>лайков на сообщения</p>
            </div>
            <div className="flex flex-col font-semibold">
              <p className="text-6xl">{supportRatingEmoji}</p>
              <p className="">{userSupportRating} место по числу лайков</p>
            </div>
          </div>
        </>
      ) : (
        renderNoSupport()
      )}

      <RogerLink />
    </div>
  );
};

export default memo(Support);
