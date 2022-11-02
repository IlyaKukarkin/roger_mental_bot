import React from "react";

import { Data, TYPE } from "../../pages/api/user-stats";

type Props = {
    type: TYPE;
    data: Data;
}

const Calendar = ({ type, data }: Props) => {
    const renderRow    

    if (type === TYPE.WEEK) {
        return (
            <p style={{ backgroundColor: 'red', color: 'aqua' }}>Week</p>
        )
    }

    if (type === TYPE.WEEK2) {
        return (
            <p style={{ backgroundColor: 'red', color: 'aqua' }}>Week2</p>
        )
    }

    return (
        <div tw="flex">
            <p style={{ backgroundColor: 'red', color: 'aqua' }}>Month</p>
            <p style={{ backgroundColor: 'red', color: 'aqua' }}>Month</p>
            <p style={{ backgroundColor: 'red', color: 'aqua' }}>Month</p>
        </div>
    )
}

export default Calendar;