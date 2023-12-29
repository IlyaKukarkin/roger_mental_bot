import React, { useMemo, memo } from "react";
import { Trans, Plural } from "@lingui/macro";

import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<
  User2023Stata["general"],
  "totalRates" | "totalRatesWithMood" | "userMentalRating"
>;

const Mood = ({ totalRates, totalRatesWithMood, userMentalRating }: Props) => {
  const percentageOfRates = useMemo(
    () => Math.ceil((totalRatesWithMood / totalRates) * 100),
    [totalRatesWithMood, totalRates],
  );

  const percentMessage = useMemo(() => {
    if (percentageOfRates > 50) {
      return <Trans>Ты молодчинка!</Trans>;
    }
    return <Trans>Неплохо!</Trans>;
  }, [percentageOfRates]);

  const mentalRatingEmoji = useMemo(() => {
    if (userMentalRating <= 20) {
      return "🏆";
    }

    if (userMentalRating <= 50) {
      return "🥇";
    }

    if (userMentalRating <= 100) {
      return "🥈";
    }

    return "🥉";
  }, []);

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <div>
        <p className=" text-3xl">
          <Trans>В этом году ты замерил настроение</Trans>
        </p>

        <p className="mt-6 text-5xl">
          <b>{totalRatesWithMood}</b>{" "}
          <Plural value={totalRatesWithMood} one="раз" few="раза" other="раз" />
        </p>
      </div>

      <div>
        <div className="grid grid-cols-2 grid-rows-2 items-center justify-center gap-x-6">
          <span className="text-3xl">
            <b>{percentageOfRates}%</b>
          </span>
          <span className="text-6xl">{mentalRatingEmoji}</span>
          <span>
            <Trans>дней получили от тебя оценку</Trans>
          </span>
          <span>
            <Trans>{userMentalRating} место по числу оценок</Trans>
          </span>
        </div>

        <p className="mt-6 text-4xl">{percentMessage}</p>
      </div>

      <div className="flex items-center">
        <p className="text-6xl">👩‍💻</p>
        <p className="text-lg">
          <Trans>
            Дневник настроения очень важен для хорошего ментального здоровья
          </Trans>
        </p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(Mood);
