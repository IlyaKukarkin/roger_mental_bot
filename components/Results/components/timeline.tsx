import React, { memo } from "react";

import { NUMBER_OF_PAGES } from "../Results2023";

const Timeline = ({ currIndex }: { currIndex: number }) => {
  const tempArray = Array(NUMBER_OF_PAGES).fill(0);

  const getItemColor = (index: number) => {
    if (index <= currIndex) {
      return "bg-violet-400";
    }

    return "bg-gray-600";
  };

  return (
    <div className="mt-4 p-4 space-y-2 flex justify-center">
      <div className="flex max-w-xs space-x-3">
        {tempArray.map((_, index) => {
          return (
            <span
              key={index}
              className={`w-12 h-2 rounded-sm ${getItemColor(index)}`}
            ></span>
          );
        })}
      </div>
    </div>
  );
};

export default memo(Timeline);
