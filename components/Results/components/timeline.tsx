import React, { memo } from "react";
import useMeasure from "react-use-measure";
import { useSpring, animated } from "@react-spring/web";

import { NUMBER_OF_PAGES, TIME_PER_PAGE } from "../Results2023";

const Timeline = ({
  currIndex,
  pause,
}: {
  currIndex: number;
  pause: boolean;
}) => {
  const tempArray = Array(NUMBER_OF_PAGES).fill(0);
  const [ref, { width }] = useMeasure();
  const props = useSpring({
    from: { width: 0 },
    to: { width },
    reset: true,
    pause: pause,
    config: {
      duration: TIME_PER_PAGE,
    },
  });

  return (
    <div className="mt-4 flex justify-center space-y-2 p-4">
      <div className="flex max-w-xs space-x-3">
        {tempArray.map((_, index) => {
          return (
            <span
              ref={ref}
              key={index}
              className={`h-2 w-12 rounded-sm bg-gray-600`}
            >
              {index === currIndex && (
                <animated.div
                  className="h-2 rounded-sm bg-violet-400"
                  style={props}
                />
              )}
              {index < currIndex && (
                <div className="h-2 w-full rounded-sm bg-violet-400"></div>
              )}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default memo(Timeline);
