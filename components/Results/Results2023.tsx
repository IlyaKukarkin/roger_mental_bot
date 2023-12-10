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
  const onClick = () => set((state) => (state + 1) % 5);
  const transRef = useSpringRef();
  const transitions = useTransition(index, {
    ref: transRef,
    keys: null,
    from: { opacity: 0, transform: "translate3d(100%,0,0)" },
    enter: { opacity: 1, transform: "translate3d(0%,0,0)" },
    leave: { opacity: 0, transform: "translate3d(-50%,0,0)" },
  });

  useEffect(() => {
    transRef.start();
  }, [index, transRef]);

  const pages: ((
    props: AnimatedProps<{ style: CSSProperties }>,
  ) => React.ReactElement)[] = [
    ({ style }) => (
      <animated.div style={{ ...style }}>
        <Welcome userCreatedAt={userCreatedAt} />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div style={{ ...style }}>
        <Mood
          totalRates={general.totalRates}
          totalRatesWithMood={general.totalRatesWithMood}
          userMentalRating={general.userMentalRating}
        />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div style={{ ...style }}>
        <Calendar months={months} />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div style={{ ...style }}>
        <Support
          months={months}
          messages={messages}
          userSupportRating={general.userSupportRating}
        />
      </animated.div>
    ),
    ({ style }) => (
      <animated.div style={{ ...style }}>
        <End />
      </animated.div>
    ),
  ];

  return (
    <div className="relative flex h-screen items-center justify-center bg-gray-800 text-gray-100 md:pt-24 ">
      <div className="absolute top-0 z-40 w-full">
        <Timeline currIndex={index} />
      </div>
      <div
        className={`relative h-full w-full md:rounded-xl bg-gray-900 text-gray-100 md:aspect-[9/16] md:h-[calc(100%-64px)] md:w-auto`}
      >
        <div
          className={`flex h-full w-full cursor-pointer flex-col items-center justify-center text-center ${styles.container}`}
          onClick={onClick}
        >
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
