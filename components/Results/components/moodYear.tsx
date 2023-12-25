import React, { memo, useMemo } from "react";

import { User2023Stata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<User2023Stata, "months">;

const MoodYear = ({ months }: Props) => {
  const getYearMood = useMemo((): number => {
    let noRates = 0;
    const summ = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
    };

    Object.values(months).forEach((month) => {
      noRates += month[0];
      summ[1] += month[1];
      summ[2] += month[2];
      summ[3] += month[3];
      summ[4] += month[4];
    });

    const moodForYear = [...Object.values(summ).sort((a, b) => b - a)];

    return moodForYear.some((i) => i > 0)
      ? Object.values(summ).lastIndexOf(moodForYear[0]) + 1
      : 0;
  }, [months]);

  const getYearEmoji = useMemo(() => {
    switch (getYearMood) {
      case 0:
        return "🙃";
      case 1:
        return "😒";
      case 2:
        return "🙂";
      case 3:
        return "😌";
      case 4:
        return "😍";
      default:
        return "🙃";
    }
  }, [getYearMood]);

  const getYearText = useMemo(() => {
    switch (getYearMood) {
      case 0:
        return "Наша умная система сообщила, что ты недостаточно часто замерял настроение, чтобы открыть смайлик. Продолжай замерять настроение!";
      case 1:
        return "Ну, этот год хотя бы заканчивается — следующий точно будет лучше!";
      case 2:
        return "Год на легкую улыбочку! А следующий будет еще лучше? ";
      case 3:
        return "Хороший год выдался, не правда ли? ";
      case 4:
        return "Отличный год! Будет что рассказать внукам";
      default:
        return "Наша умная система сообщила, что ты недостаточно часто замерял настроение, чтобы открыть смайлик. Продолжай замерять настроение!";
    }
  }, [getYearMood]);

  return (
    <div className="flex h-full flex-col items-center font-bold">
      <p className="mt-24 text-3xl">Смайлик, описывающий твой 2023 год</p>

      <p className="text-[250px]">{getYearEmoji}</p>

      <p className="text-xl">{getYearText}</p>

      <RogerLink />
    </div>
  );
};

export default memo(MoodYear);
