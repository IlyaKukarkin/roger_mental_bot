import React, { useMemo, memo } from "react";
import { User2023Stata } from "../../../lib/api/users";

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
    if (percentageOfRates > 60) {
      return "Ты молодчинка!\nДневник настроения очень важен для хорошего ментального здоровья";
    }
    if (percentageOfRates > 60) {
      return "Ты хорошо старался!\nПродолжай держать уровень и в следующем году!";
    }
    return "Ты долбоеб мудак и пидорас\nМы для кого бота писали? Ты? Сынок ебаный?";
  }, [percentageOfRates]);

  return (
    <>
      <p>
        Ты замерил <b>{totalRates}</b> раз настроение
      </p>
      <br />
      <p>
        <b>{percentageOfRates}%</b> дней получили от тебя оценку
      </p>
      <br />
      <p>{percentMessage}</p>
      <br />
      <p>Ты в топ-{userMentalRating} по всему боту замеру настроения!</p>
    </>
  );
};

export default memo(Mood);
