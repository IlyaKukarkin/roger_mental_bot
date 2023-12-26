import React, { memo, useMemo } from "react";
import { Trans, Plural } from "@lingui/macro";

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
        <div>
          <p className="text-[100px]">😱</p>

          <p className="text-lg">
            <Trans>А здесь нет статистики!</Trans>
          </p>
        </div>

        <p className="text-lg">
          <Trans>
            Создай сообщение по команде /fillform, чтобы начать поддерживать
            других пользователей
          </Trans>
        </p>
      </>
    );
  };

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <div>
        <p className="text-xl">
          <Trans>В этом году тебя поддержало</Trans>
        </p>

        <p className="mt-6 text-3xl">
          <Plural
            value={allBadRates}
            one="# пользователь"
            other="# пользователя"
          />
        </p>
      </div>

      {Object.keys(messages).length ? (
        <>
          <p className="text-2xl">
            <Trans>Но ты тоже не отставал!</Trans>
          </p>

          <div className="grid grid-cols-2 grid-rows-2 items-center justify-center gap-y-8">
            <div className="flex flex-col font-semibold">
              <p>
                <Trans>Ты создал</Trans>
              </p>
              <p className="text-3xl font-bold">
                {Object.keys(messages).length}
              </p>
              <p>
                <Plural
                  value={Object.keys(messages).length}
                  one="сообщение для поддержки"
                  other="сообщения для поддержки"
                />
              </p>
            </div>
            <div className="flex flex-col font-semibold">
              <p>
                <Trans>Ты поддержал</Trans>
              </p>
              <p className="text-3xl font-bold">{countMessageShows}</p>
              <p>
                <Plural
                  value={countMessageShows}
                  one="человека с плохим настроением"
                  other="человек с плохим настроением"
                />
              </p>
            </div>
            <div className="flex flex-col font-semibold">
              <p>
                <Trans>Ты получил</Trans>
              </p>
              <p className="text-3xl font-bold">{countMessageLikes}</p>
              <p>
                <Plural
                  value={Object.keys(messages).length}
                  one="лайка на сообщения"
                  other="лайков на сообщения"
                />
              </p>
            </div>
            <div className="flex flex-col font-semibold">
              <p className="text-6xl">{supportRatingEmoji}</p>
              <p className="">
                <Plural
                  value={userSupportRating}
                  one="# место по числу лайков"
                  other="# место по числу лайков"
                />
              </p>
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
