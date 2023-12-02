import type { NextPage } from "next";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/router";

import { amplitude } from "../../utils/useAmplitudeInit";
import { User2023Stata } from "../../lib/api/users";
import Loading from "../../components/Loading";
import { MOOD, getRateBgColor } from "../../components/Calendar/utils";

const Results2023: NextPage = () => {
  const router = useRouter();
  const [fetching, setFetching] = useState(false);
  const [statistic, setStatistic] = useState<User2023Stata | null>(null);
  const { t: trackingId } = router.query;
  const userId = router.query.userid;

  useEffect(() => {
    amplitude.setUserId(trackingId);
    router.replace({ query: { userid: userId } }, undefined, { shallow: true });

    fetch(`/api/statistic?user_id=${userId}`)
      .then((res) => {
        if (res.ok) {
          return res.json();
        }

        throw new Error("Error");
      })
      .then((userStatistic) => setStatistic(userStatistic))
      .catch((error) => {
        // Add amplitude error
        console.log(error);
      })
      .finally(() => setFetching(false));
  }, []);

  const percentageOfRates = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    return Math.ceil(
      (statistic.general.totalRatesWithMood / statistic.general.totalRates) *
        100
    );
  }, [statistic]);

  const percentMessage = useMemo(() => {
    if (percentageOfRates > 60) {
      return "Ты молодчинка!\nДневник настроения очень важен для хорошего ментального здоровья";
    }
    if (percentageOfRates > 60) {
      return "Ты хорошо старался!\nПродолжай держать уровень и в следующем году!";
    }
    return "Ты долбоеб мудак и пидорас\nМы для кого бота писали? Ты? Сынок ебаный?";
  }, [percentageOfRates]);

  // ToDo: put all count functions in separate file
  const bestMonth = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    let bestMonth = 0;
    let currGoodRatesCount =
      statistic.months[bestMonth][3] + statistic.months[bestMonth][4];

    for (let i = 1; i < 12; i++) {
      if (
        currGoodRatesCount <
        statistic.months[i][3] + statistic.months[i][4]
      ) {
        bestMonth = i;
        currGoodRatesCount = statistic.months[i][3] + statistic.months[i][4];
      }
    }

    return bestMonth;
  }, [statistic]);

  const worthMonth = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    let worthMonth = 0;
    let currBadRatesCount =
      statistic.months[worthMonth][1] + statistic.months[worthMonth][2];

    for (let i = 1; i < 12; i++) {
      if (currBadRatesCount < statistic.months[i][1] + statistic.months[i][2]) {
        worthMonth = i;
        currBadRatesCount = statistic.months[i][1] + statistic.months[i][2];
      }
    }

    return worthMonth;
  }, [statistic]);

  const allBadrates = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    let badRates = 0;

    for (let i = 0; i < 12; i++) {
      badRates += statistic.months[i][1];
      badRates += statistic.months[i][2];
    }

    return badRates;
  }, [statistic]);

  const countMessageLikes = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    return Object.values(statistic.messages).reduce(
      (acc, currValue) => acc + currValue.likes,
      0
    );
  }, [statistic]);

  const countMessageShows = useMemo(() => {
    if (!statistic) {
      return 0;
    }

    return Object.values(statistic.messages).reduce(
      (acc, currValue) => acc + currValue.rates,
      0
    );
  }, [statistic]);

  const mapMonthToText = (id: number) => {
    switch (id) {
      case 0:
        return "Январь";
      case 1:
        return "Февраль";
      case 2:
        return "Март";
      case 3:
        return "Апрель";
      case 4:
        return "Май";
      case 5:
        return "Июнь";
      case 6:
        return "Июль";
      case 7:
        return "Август";
      case 8:
        return "Сентябрь";
      case 9:
        return "Октябрь";
      case 10:
        return "Ноябрь";
      case 11:
        return "Декабрь";
      default:
        return "Ошибка получения месяца";
    }
  };

  const getMoodForMonth = (data: { [mood: number]: number }): MOOD => {
    const rates = Object.values(data);

    const max = rates.reduce((acc, currValue) => {
      if (acc < currValue) {
        return currValue;
      }
      return acc;
    });

    return rates.indexOf(max);
  };

  if (fetching || !statistic) {
    return (
      <section className="flex items-center h-full min-h-screen p-16 dark:bg-gray-900 dark:text-gray-100">
        <Loading />
      </section>
    );
  }

  return (
    <section className="flex items-center h-full min-h-screen p-16 dark:bg-gray-900 dark:text-gray-100">
      <div className="flex flex-col justify-center w-full text-center">
        <p>
          Твоя стата за год от t.me/rogermentalbot за ДАТА РЕГИСТРАЦИИ -
          СЕГОДНЯШНЯЯ ДАТА (должна быть меньше 1 января 2024)
        </p>

        <br />
        <br />

        <p>
          Ты замерил <b>{statistic.general.totalRates}</b> раз настроение
        </p>
        <p>
          <b>{percentageOfRates}%</b> дней получили от тебя оценку
        </p>
        <p>{percentMessage}</p>

        <br />
        <br />

        <p>Самый позитивный месяц</p>
        <p>
          <b>{mapMonthToText(bestMonth)}</b>
        </p>
        <p>
          Ты поставил{" "}
          {statistic.months[bestMonth][3] + statistic.months[bestMonth][4]}{" "}
          оценки -- из них {statistic.months[bestMonth][4]} зелёных и{" "}
          {statistic.months[bestMonth][3]} желтых
        </p>
        <br />
        <p>Самый грустный месяц</p>
        <p>
          <b>{mapMonthToText(worthMonth)}</b>
        </p>
        <p>
          Ты поставил{" "}
          {statistic.months[worthMonth][1] + statistic.months[worthMonth][2]}{" "}
          оценки -- из них {statistic.months[worthMonth][1]} красных и{" "}
          {statistic.months[worthMonth][2]} оранжевых
        </p>

        <br />
        <br />

        <p>Как тебе запомнился каждый месяц</p>
        <div className="grid grid-cols-4 grid-rows-3">
          {Object.entries(statistic.months).map(([month, data]) => {
            return (
              <div key={month} className="flex flex-col items-center">
                <div
                  className={`opacity-80 w-10 h-10 rounded-full ${
                    getRateBgColor[getMoodForMonth(data)]
                  }`}
                />
                <p>
                  <b>{mapMonthToText(Number(month))}</b>
                </p>
              </div>
            );
          })}
        </div>

        <br />
        <br />

        <p>Поддержка</p>
        <br />

        <p>За год тебя поддержало {allBadrates} человек</p>
        <br />

        <p>Ты создал {Object.keys(statistic.messages).length} сообщения</p>
        <p>И получил {countMessageLikes} лайка за год</p>
        <p>За год ты поддержал {countMessageShows} человека.</p>

        <br />
        <p>Ты в топ-&quot;пока без понятия&quot; по всему боту по поддержке! </p>
      </div>
    </section>
  );
};

export default Results2023;
