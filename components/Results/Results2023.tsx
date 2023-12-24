import React, { CSSProperties, useEffect, useState } from "react";
import {
  useTransition,
  animated,
  AnimatedProps,
  useSpringRef,
} from "@react-spring/web";

import { User2023Stata } from "../../lib/api/users";
import Welcome from "./components/welcome";
import Mood from "./components/mood";
import Calendar from "./components/calendar";
import Support from "./components/support";
import End from "./components/end";
import Timeline from "./components/timeline";

import styles from "./styles.module.css";

type Props = {
  statistic: User2023Stata;
};

export const NUMBER_OF_PAGES = 5;
export const TIME_PER_PAGE = 5000;

const Results2023 = ({ statistic }: Props) => {
  const { general, messages, months, userCreatedAt } = statistic;

  const [index, set] = useState(0);
  const transRef = useSpringRef();
  const transitions = useTransition(index, {
    ref: transRef,
    keys: null,
    from: { opacity: 0, transform: "translate3d(100%,0,0)" },
    enter: { opacity: 1, transform: "translate3d(0%,0,0)" },
    leave: { opacity: 0, transform: "translate3d(-50%,0,0)" },
  });

  const onPrevClick = () => {
    if (index !== 0) {
      set((prev) => prev - 1);
    }
  };

  const onNextClick = () => {
    if (index !== NUMBER_OF_PAGES - 1) {
      set((prev) => prev + 1);
    }
  };

  useEffect(() => {
    transRef.start();
  }, [index, transRef]);

  const pages: ((
    props: AnimatedProps<{ style: CSSProperties }>,
  ) => React.ReactElement)[] = [
    ({ style }) => (
      <animated.div className={styles.page} style={{ ...style }}>
        <Welcome userCreatedAt={userCreatedAt} />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div className={styles.page} style={{ ...style }}>
        <Mood
          totalRates={general.totalRates}
          totalRatesWithMood={general.totalRatesWithMood}
          userMentalRating={general.userMentalRating}
        />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div className={styles.page} style={{ ...style }}>
        <Calendar months={months} />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div className={styles.page} style={{ ...style }}>
        <Support
          months={months}
          messages={messages}
          userSupportRating={general.userSupportRating}
        />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div className={styles.page} style={{ ...style }}>
        <End />
      </animated.div>
    ),
  ];

  return (
    <div className="relative flex h-screen items-center justify-center bg-gray-800 text-gray-100 md:pt-24">
      <div className="absolute top-0 z-40 w-full">
        <Timeline currIndex={index} />
      </div>
      <div
        className={`relative h-full w-full bg-gray-900 text-gray-100 md:aspect-[9/16] md:h-[calc(100%-64px)] md:w-auto md:rounded-xl`}
      >
        <div
          className={`flex h-full w-full flex-col items-center justify-center text-center ${styles.container}`}
        >
          {/* Mobile controls */}
          <div
            className="absolute top-0 left-0 right-1/2 bottom-0 z-30 md:hidden"
            onClick={onPrevClick}
          />
          <div
            className="absolute top-0 left-1/2 right-0 bottom-0 z-30 md:hidden"
            onClick={onNextClick}
          />

          {/* Desctop controls */}
          <div className="absolute left-[-64px] hidden md:block">
            <button
              aria-label="Slide back"
              type="button"
              onClick={onPrevClick}
              className="focus:ri z-30 rounded-full bg-opacity-50 p-2 focus:outline-none dark:bg-gray-900 focus:dark:bg-gray-400"
            >
              <svg
                width="8"
                height="14"
                fill="none"
                viewBox="0 0 8 14"
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
              >
                <path
                  d="M7 1L1 7L7 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></path>
              </svg>
            </button>
          </div>
          <div className="absolute right-[-64px] hidden md:block">
            <button
              aria-label="Slide forward"
              id="next"
              onClick={onNextClick}
              className="focus:ri z-30 rounded-full bg-opacity-50 p-2 focus:outline-none dark:bg-gray-900 focus:dark:bg-gray-400"
            >
              <svg
                width="8"
                height="14"
                viewBox="0 0 8 14"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
              >
                <path
                  d="M1 1L7 7L1 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></path>
              </svg>
            </button>
          </div>

          {transitions((style, i) => {
            const Page = pages[i];
            return <Page style={style} />;
          })}
        </div>
      </div>
    </div>
  );
};

export default Results2023;
