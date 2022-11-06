import React from "react"

type Props = {
    text: string;
}

const Title = ({ text }: Props) => {
    return (
        <div tw={'flex ml-2 mt-3 opacity-80 w-10 h-10 justify-center items-center rounded-full'}>
            <p tw="text-gray-100 font-bold text-xl">{text}</p>
        </div>
    )
}

export default Title