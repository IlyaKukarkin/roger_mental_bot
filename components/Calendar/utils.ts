export enum MOOD {
    GREEN = 4,
    YELLOW = 3,
    ORANGE = 2,
    RED = 1,
    SKIP = 0,
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