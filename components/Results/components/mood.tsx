import React, { useMemo, memo } from "react";

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
      return "Ты молодчинка!";
    }
    return "Неплохо!";
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
    <div className="flex h-full flex-col items-center font-bold">
      <p className="pt-32 text-3xl">В этом году ты замерил настроение</p>

      <p className="pt-10 text-5xl">
        <b>{totalRates}</b> раз
      </p>

      <div className="mt-10 grid grid-cols-2 grid-rows-2 items-center justify-center gap-x-6">
        <span className="text-3xl">
          <b>{percentageOfRates}%</b>
        </span>
        <span className="text-6xl">{mentalRatingEmoji}</span>
        <span> дней получили от тебя оценку</span>
        <span>{userMentalRating} место по числу оценок</span>
      </div>

      <p className="pt-24 text-4xl">{percentMessage}</p>

      <div className="mt-6 flex items-center">
        <p className="text-6xl">👩‍💻</p>
        <p className="text-lg">
          Дневник настроения очень важен для хорошего ментального здоровья
        </p>
      </div>

      <RogerLink />
    </div>
  );
};

export default memo(Mood);
