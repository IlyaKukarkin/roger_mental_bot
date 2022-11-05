export enum MOOD {
    GREEN = 'GREEN',
    YELLOW = 'YELLOW',
    ORANGE = 'ORANGE',
    RED = 'RED',
    SKIP = 'SKIP',
}

export const getRateBgColor = {
    [MOOD.GREEN]: 'bg-emerald-400',
    [MOOD.YELLOW]: 'bg-yellow-200',
    [MOOD.ORANGE]: 'bg-orange-400',
    [MOOD.RED]: 'bg-red-400',
    [MOOD.SKIP]: 'bg-gray-700',
}

export const getRateColor = {
    [MOOD.GREEN]: 'text-emerald-400',
    [MOOD.YELLOW]: 'text-yellow-200',
    [MOOD.ORANGE]: 'text-orange-400',
    [MOOD.RED]: 'text-red-400',
    [MOOD.SKIP]: 'text-stone-100',
}

export const getFullDayOfTheWeek = [
    "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
]

export const getShortDayOfTheWeek = [
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
]