import React from "react";

import { Data } from "../../pages/api/user-stats";
import Day from "./day";
import Title from "./title";

type Props = {
    data: Data[];
}

const Calendar = ({ data }: Props) => {
    const splitToWeeks = (data: Data[]): Array<Data[]> => {
        const res = [];

        for (let i = 0; i < 4; i++) {
            res.push(data.splice(0, 7))
        }

        return res;
    }

    const renderRow = (week: Data[], index: number) => {
        return (
            <div key={index} tw="flex w-full">
                {week.map(day => (<Day key={day.date} data={day.date} disabled={day.disabled} rate={day.mood} />))}
            </div>
        )
    }

    const renderTitle = () => {
        const titles = ['Пн', "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

        return (
            <div tw="flex w-full">
                {titles.map((title, index) => (<Title key={index} text={title} />))}
            </div>
        )
    }

    return (
        <div tw="flex flex-col">
            {renderTitle()}
            {splitToWeeks(data).map((week: Data[], index) => renderRow(week, index))}
        </div>
    )
}

export default Calendar;