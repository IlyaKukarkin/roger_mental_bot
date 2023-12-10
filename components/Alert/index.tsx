import React from "react";

import { AlertTypes, Props } from "./types";

const Alert = ({ is_displayed, message, type = AlertTypes.SUCCESS }: Props) => {
  const BORDER_COLOR =
    type === AlertTypes.SUCCESS ? "border-emerald-400" : "border-rose-500";

  return (
    <div
      className={`absolute top-10 animate-alert ${
        is_displayed ? "block" : "hidden"
      }`}
    >
      <div className="flex max-w-2xl gap-6 divide-x divide-gray-700 overflow-hidden rounded-lg bg-gray-100 shadow-md dark:bg-gray-900 dark:text-gray-100">
        <div className={`flex flex-1 flex-col border-l-8 p-4 ${BORDER_COLOR}`}>
          <span className="text-2xl">
            {type === AlertTypes.SUCCESS ? "Успех" : "Ой"}
          </span>
          <span className="text-xs dark:text-gray-400">{message}</span>
        </div>
      </div>
    </div>
  );
};

export default Alert;
