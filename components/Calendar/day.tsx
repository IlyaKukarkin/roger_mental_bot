import React from "react"

import { getRateBgColor, MOOD } from "./utils";

type Props = {
    data: number;
    disabled: boolean;
    rate: MOOD;
}

const Day = ({ data, disabled, rate }: Props) => {
    if (disabled) {
        return (
            <div tw="flex ml-2 mt-3 w-10 h-10 justify-center items-center rounded-full bg-gray-400">
                <p tw="text-gray-900 font-bold text-xl">{data}</p>
            </div>
        )
    }

    if (rate === MOOD.SKIP) {
        return (
            <div tw={`flex ml-2 mt-3 opacity-80 w-10 h-10 justify-center items-center rounded-full ${getRateBgColor[rate]}`}>
                <p tw="text-gray-200 font-bold text-xl">{data}</p>
            </div>
        )
    }

    return (
        <div tw={`flex ml-2 mt-3 opacity-80 w-10 h-10 justify-center items-center rounded-full ${getRateBgColor[rate]}`}>
            <p tw="text-gray-900 font-bold text-xl">{data}</p>
        </div>
    )
}

export default Day