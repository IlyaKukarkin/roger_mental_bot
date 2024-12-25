import React, { memo, useMemo } from "react";
import { Trans } from "@lingui/macro";

import { UserYearlyStata } from "../../../lib/api/users";
import RogerLink from "./rogerLink";

type Props = Pick<UserYearlyStata, "months">;

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
        return (
          <Trans>
            Наша умная система сообщила, что ты недостаточно часто замерял
            настроение, чтобы открыть смайлик. Продолжай замерять настроение!
          </Trans>
        );
      case 1:
        return (
          <Trans>
            Ну, этот год хотя бы заканчивается — следующий точно будет лучше!
          </Trans>
        );
      case 2:
        return (
          <Trans>Год на легкую улыбочку! А следующий будет еще лучше? </Trans>
        );
      case 3:
        return <Trans>Хороший год выдался, не правда ли? </Trans>;
      case 4:
        return <Trans>Отличный год! Будет что рассказать внукам</Trans>;
      default:
        return (
          <Trans>
            Наша умная система сообщила, что ты недостаточно часто замерял
            настроение, чтобы открыть смайлик. Продолжай замерять настроение!
          </Trans>
        );
    }
  }, [getYearMood]);

  return (
    <div className="flex h-full flex-col items-center justify-evenly font-bold">
      <p className="text-3xl">
        <Trans>Смайлик, описывающий твой 2024 год</Trans>
      </p>

      <p className="-my-24 text-[250px]">{getYearEmoji}</p>

      <p className="text-xl">{getYearText}</p>

      <RogerLink />
    </div>
  );
};

export default memo(MoodYear);
