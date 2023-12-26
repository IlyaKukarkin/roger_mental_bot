import { ImageResponse } from "@vercel/og";
import { NextRequest } from "next/server";
import { PropsWithChildren } from "react";

import Calendar from "../../components/Calendar";
import {
  getRateBgColor,
  getRateColor,
  MOOD,
  getFullDayOfTheWeek,
  getShortDayOfTheWeek,
} from "../../components/Calendar/utils";

export const config = {
  runtime: "edge",
};

export type Data = {
  date: number;
  mood: MOOD;
  disabled: boolean;
};

type MoodLegend = {
  mood: MOOD;
  title: string;
};

export default async function handler(req: NextRequest) {
  const Wrapper = ({ children }: PropsWithChildren) => {
    const moodLegend: MoodLegend[] = [
      {
        title: "ужасный день",
        mood: MOOD.RED,
      },
      {
        title: "чуть плохой день",
        mood: MOOD.ORANGE,
      },
      {
        title: "хороший день",
        mood: MOOD.YELLOW,
      },
      {
        title: "отличный день",
        mood: MOOD.GREEN,
      },
      {
        title: "нет оценки",
        mood: MOOD.SKIP,
      },
    ];

    return (
      <div
        style={{
          backgroundColor: "black",
          backgroundSize: "150px 150px",
          height: "100%",
          width: "100%",
          display: "flex",
          textAlign: "center",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          flexWrap: "nowrap",
        }}
      >
        {children}

        <p tw="absolute -bottom-3 text-gray-400">
          {moodLegend.map((mood) => {
            return (
              <>
                <div
                  tw={`inline w-6 h-6 mx-2 rounded-xl ${
                    getRateBgColor[mood.mood]
                  }`}
                />
                <span>{`- ${mood.title}`}</span>
              </>
            );
          })}
        </p>
      </div>
    );
  };

  const renderGeneralStats = (data: Data[]) => {
    const filterData = data.filter((day) => !day.disabled);

    const total = filterData.length;
    const { red, orange, yellow, green, skip } = filterData.reduce(
      (acc, curr) => {
        if (curr.mood === MOOD.RED) {
          return {
            ...acc,
            red: acc.red + 1,
          };
        }

        if (curr.mood === MOOD.ORANGE) {
          return {
            ...acc,
            orange: acc.orange + 1,
          };
        }

        if (curr.mood === MOOD.YELLOW) {
          return {
            ...acc,
            yellow: acc.yellow + 1,
          };
        }

        if (curr.mood === MOOD.GREEN) {
          return {
            ...acc,
            green: acc.green + 1,
          };
        }

        return {
          ...acc,
          skip: acc.skip + 1,
        };
      },
      { red: 0, orange: 0, yellow: 0, green: 0, skip: 0 },
    );

    const calcRed = Math.round((Number(red) / Number(total)) * 100);
    const calcOrange = Math.round((Number(orange) / Number(total)) * 100);
    const calcYellow = Math.round((Number(yellow) / Number(total)) * 100);
    const calcGreen = Math.round((Number(green) / Number(total)) * 100);
    const calcSkip = Math.round((Number(skip) / Number(total)) * 100);

    return (
      <div tw="flex flex-col bg-gray-800 rounded-xl px-8 pt-0 pb-2 w-full bg-opacity-50">
        <p tw="text-xl ml-8">Распределение настроения:</p>
        <div tw="flex justify-around w-full">
          <p
            tw={`text-xl px-2 py-1 rounded-md text-gray-900 font-bold ${
              getRateBgColor[MOOD.RED]
            }`}
          >
            {Number.isNaN(calcRed) ? 0 : calcRed} %
          </p>
          <p
            tw={`text-xl px-2 py-1 rounded-md text-gray-900 font-bold ${
              getRateBgColor[MOOD.ORANGE]
            }`}
          >
            {Number.isNaN(calcOrange) ? 0 : calcOrange} %
          </p>
          <p
            tw={`text-xl px-2 py-1 rounded-md text-gray-900 font-bold ${
              getRateBgColor[MOOD.YELLOW]
            }`}
          >
            {Number.isNaN(calcYellow) ? 0 : calcYellow} %
          </p>
          <p
            tw={`text-xl px-2 py-1 rounded-md text-gray-900 font-bold ${
              getRateBgColor[MOOD.GREEN]
            }`}
          >
            {Number.isNaN(calcGreen) ? 0 : calcGreen} %
          </p>
          <p
            tw={`text-xl px-2 py-1 rounded-md text-gray-200 font-bold ${
              getRateBgColor[MOOD.SKIP]
            }`}
          >
            {Number.isNaN(calcSkip) ? 0 : calcSkip} %
          </p>
        </div>
      </div>
    );
  };

  const renderGoodDay = (data: Data[]) => {
    const countGoodDays = data.reduce(
      (agr, curr, index) => {
        if (!curr.disabled && curr.mood === MOOD.GREEN) {
          const tempArray = [...agr];
          const getIndex = index % 7;
          const currValue = agr[getIndex];

          tempArray.splice(getIndex, 1, currValue + 1);

          return [...tempArray];
        }

        return agr;
      },
      [0, 0, 0, 0, 0, 0, 0],
    );

    const max = Math.max(...countGoodDays);
    const countMaxElem = countGoodDays.filter((el) => el === max).length;

    if (max === 0) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.GREEN]}`}>
            Ни одного(
          </p>
          <p tw="text-gray-400 -mt-4">Самый зелёный день недели</p>
        </div>
      );
    }

    if (countMaxElem === 7) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.GREEN]}`}>
            Все!
          </p>
          <p tw="text-gray-400 -mt-4">Самый зелёный день недели</p>
        </div>
      );
    }

    if (countMaxElem != 1) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <div tw="flex">
            {countGoodDays.map((el, index, arr) => {
              if (el === max) {
                if (index === arr.indexOf(max)) {
                  return (
                    <p
                      key={index}
                      tw={`text-xl text-center font-bold ${
                        getRateColor[MOOD.GREEN]
                      }`}
                    >
                      {getShortDayOfTheWeek[index]}
                    </p>
                  );
                }

                return (
                  <p
                    key={index}
                    tw={`text-xl text-center font-bold mr-2 ${
                      getRateColor[MOOD.GREEN]
                    }`}
                  >
                    , {getShortDayOfTheWeek[index]}
                  </p>
                );
              }
            })}
          </div>
          <p tw="text-gray-400 -mt-4">Самые зелёные дни недели</p>
        </div>
      );
    }

    return (
      <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
        <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.GREEN]}`}>
          {getFullDayOfTheWeek[countGoodDays.indexOf(max)]}
        </p>
        <p tw="text-gray-400 -mt-4">Самый зелёный день недели</p>
      </div>
    );
  };

  const renderBadDay = (data: Data[]) => {
    const countBadDays = data.reduce(
      (agr, curr, index) => {
        if (!curr.disabled && curr.mood === MOOD.RED) {
          const tempArray = [...agr];
          const getIndex = index % 7;
          const currValue = agr[getIndex];

          tempArray.splice(getIndex, 1, currValue + 1);

          return [...tempArray];
        }

        return agr;
      },
      [0, 0, 0, 0, 0, 0, 0],
    );

    const max = Math.max(...countBadDays);
    const countMaxElem = countBadDays.filter((el) => el === max).length;

    if (max === 0) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.RED]}`}>
            Ни одного!
          </p>
          <p tw="text-gray-400 -mt-4">Самый красный день недели</p>
        </div>
      );
    }

    if (countMaxElem === 7) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.RED]}`}>
            Все(
          </p>
          <p tw="text-gray-400 -mt-4">Самый красный день недели</p>
        </div>
      );
    }

    if (countMaxElem != 1) {
      return (
        <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
          <div tw="flex">
            {countBadDays.map((el, index, arr) => {
              if (el === max) {
                if (index === arr.indexOf(max)) {
                  return (
                    <p
                      key={index}
                      tw={`text-xl text-center font-bold ${
                        getRateColor[MOOD.RED]
                      }`}
                    >
                      {getShortDayOfTheWeek[index]}
                    </p>
                  );
                }

                return (
                  <p
                    key={index}
                    tw={`text-xl text-center font-bold mr-2 ${
                      getRateColor[MOOD.RED]
                    }`}
                  >
                    , {getShortDayOfTheWeek[index]}
                  </p>
                );
              }
            })}
          </div>
          <p tw="text-gray-400 -mt-4">Самые красные дни недели</p>
        </div>
      );
    }

    return (
      <div tw="flex flex-col mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center">
        <p tw={`text-xl text-center font-bold ${getRateColor[MOOD.RED]}`}>
          {getFullDayOfTheWeek[countBadDays.indexOf(max)]}
        </p>
        <p tw="text-gray-400 -mt-4">Самый красный день недели</p>
      </div>
    );
  };

  const renderCompareStatistic = (percent: number) => {
    return (
      <div tw="flex flex-col h-35 mt-4 bg-gray-800 rounded-xl px-8 px-0 w-full bg-opacity-50 items-center justify-center">
        <p tw="text-gray-400">Ты замерял настроение чаще, чем</p>
        <p tw="text-4xl text-center font-bold -mt-4">{percent} %</p>
        <p tw="text-gray-400 -mt-4">пользователей</p>
      </div>
    );
  };

  try {
    const { searchParams } = new URL(req.url);

    // ?title=<title>
    const username = searchParams.get("username");
    const title = searchParams.get("title");
    const data: Data[] = JSON.parse(decodeURI(searchParams.get("data") || ""));
    const compare_to_others = Number(searchParams.get("compare_to_others"));

    if (
      !username ||
      !title ||
      !data ||
      (!compare_to_others && compare_to_others !== 0)
    ) {
      return new ImageResponse(
        (
          <Wrapper>
            <div tw="flex flex-col bg-gray-800 text-gray-100 w-full h-full justify-center items-center">
              <h1 tw="text-3xl">Ошибка создания изображения</h1>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                <path
                  fill="currentColor"
                  d="M256,16C123.452,16,16,123.452,16,256S123.452,496,256,496,496,388.548,496,256,388.548,16,256,16ZM403.078,403.078a207.253,207.253,0,1,1,44.589-66.125A207.332,207.332,0,0,1,403.078,403.078Z"
                ></path>
                <rect
                  width="176"
                  height="32"
                  x="168"
                  y="320"
                  fill="currentColor"
                ></rect>
                <polygon
                  fill="currentColor"
                  points="210.63 228.042 186.588 206.671 207.958 182.63 184.042 161.37 162.671 185.412 138.63 164.042 117.37 187.958 141.412 209.329 120.042 233.37 143.958 254.63 165.329 230.588 189.37 251.958 210.63 228.042"
                ></polygon>
                <polygon
                  fill="currentColor"
                  points="383.958 182.63 360.042 161.37 338.671 185.412 314.63 164.042 293.37 187.958 317.412 209.329 296.042 233.37 319.958 254.63 341.329 230.588 365.37 251.958 386.63 228.042 362.588 206.671 383.958 182.63"
                ></polygon>
              </svg>
            </div>
          </Wrapper>
        ),
        {
          width: 1200,
          height: 630,
        },
      );
    }

    return new ImageResponse(
      (
        <Wrapper>
          <div tw="bg-gray-800 text-gray-100 h-full w-full py-8 flex justify-around">
            <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col justify-start">
              <div tw="flex justify-between w-full">
                <span tw="text-violet-400">Пользователь: {username}</span>
                <span tw="text-violet-400">
                  Создано: {new Date().toLocaleDateString("ru-RU")}
                </span>
              </div>
              <div tw="flex flex-col mt-2 items-center w-full">
                <p tw="text-2xl mx-auto p-0 m-0">Календарь настроений</p>
                <p tw="text-2xl mx-auto p-0 m-0">{title}</p>
              </div>
              <div tw="flex justify-center items-center w-full h-[70%]">
                <Calendar data={data} />
              </div>
            </div>
            <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col justify-start">
              {renderGeneralStats(data)}
              {renderGoodDay(data)}
              {renderBadDay(data)}
              {renderCompareStatistic(compare_to_others)}
            </div>
          </div>
        </Wrapper>
      ),
      {
        width: 1200,
        height: 630,
      },
    );
  } catch (e: any) {
    console.log(`${e.message}`);
    return new Response(`Failed to generate the image`, {
      status: 500,
    });
  }
}
