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

import styles from "./styles.module.css";

type Props = {
  statistic: User2023Stata;
};

const TIME_PER_PAGE = 5000;

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
  }, [index]);

  const pages: ((
    props: AnimatedProps<{ style: CSSProperties }>
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
    <div
      className={`text-center dark:bg-gray-900 dark:text-gray-100 ${styles.container}`}
      onClick={onClick}
    >
      {transitions((style, i) => {
        const Page = pages[i];
        return <Page style={style} />;
      })}
    </div>
  );
};

export default Results2023;
