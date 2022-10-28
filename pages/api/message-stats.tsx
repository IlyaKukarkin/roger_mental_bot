import { ImageResponse } from '@vercel/og';
import { NextRequest } from 'next/server';
import { PropsWithChildren, ReactNode } from 'react';

export const config = {
    runtime: 'experimental-edge',
};

type Props = {
    show?: string;
    likes?: string;
    dislikes?: string;
    link_clicks?: string;
    current_date: string;
    created_date?: string;
    text?: string;
    image?: string;
    link?: string;
}

export default async function handler(req: NextRequest) {
    const Wrapper = ({ children }: PropsWithChildren) => {
        return (
            <div
                style={{
                    backgroundColor: 'black',
                    backgroundSize: '150px 150px',
                    height: '100%',
                    width: '100%',
                    display: 'flex',
                    textAlign: 'center',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    flexWrap: 'nowrap',
                }}
            >
                {children}
            </div>
        )
    }

    const renderStats = ({ show, likes, dislikes, link_clicks, current_date }: Props) => {
        return (
            <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col">
                <div tw="flex justify-between items-center w-full">
                    <span tw="text-center text-2xl">Статистика</span>
                    <span tw="text-violet-400">на {new Date(current_date).toLocaleDateString("ru-RU")}</span>
                </div>
                <div tw="flex flex-col h-full w-full justify-center items-center">
                    <div tw="flex flex-col h-[25%] justify-start items-center m-2 lg:m-6">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{show}</p>
                        <p tw="text-sm sm:text-base">Количество показов</p>
                    </div>
                    <div tw="flex flex-col h-[25%] justify-start items-center m-2 lg:m-6">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{likes} / {dislikes}</p>
                        <p tw="text-sm sm:text-base">Лайки / Дизлайки</p>
                    </div>
                    <div tw="flex flex-col h-[25%] justify-start items-center m-2 lg:m-6">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{link_clicks}</p>
                        <p tw="text-sm sm:text-base">Количество переходов по ссылке</p>
                    </div>
                </div>
            </div>
        )
    }

    const renderElement = (label: string, content: string) => {
        return (
            <div tw="flex flex-col text-left">
                <div>{label}</div>
                <div tw="text-gray-400">{content}</div>
            </div>
        )
    }

    const renderImage = (image: string) => {
        return (
            <div tw="flex flex-col text-left">
                <div tw="mb-2">Картинка:</div>
                <img
                    width="256"
                    height="256"
                    src={image}
                    style={{
                        borderRadius: 28,
                    }}
                />
            </div>
        )
    }

    try {
        const { searchParams } = new URL(req.url);

        // ?title=<title>
        const current_date = searchParams.get('current_date');
        const show = searchParams.get('show');
        const likes = searchParams.get('likes');
        const dislikes = searchParams.get('dislikes');
        const link_clicks = searchParams.get('link_clicks');
        const text = searchParams.get('text');
        const image = searchParams.get('image');
        const link = searchParams.get('link');
        const created_date = searchParams.get('created_date');

        if (!show || !likes || !dislikes || !link_clicks || !text || !created_date || !current_date) {
            return new ImageResponse(
                (
                    <Wrapper>
                        <div tw="flex flex-col bg-gray-800 text-gray-100 w-full h-full justify-center items-center">
                            <h1 tw="text-3xl">Ошибка создания изображения</h1>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" tw="w-40 h-40 text-gray-600">
                                <path fill="currentColor" d="M256,16C123.452,16,16,123.452,16,256S123.452,496,256,496,496,388.548,496,256,388.548,16,256,16ZM403.078,403.078a207.253,207.253,0,1,1,44.589-66.125A207.332,207.332,0,0,1,403.078,403.078Z"></path>
                                <rect width="176" height="32" x="168" y="320" fill="currentColor"></rect>
                                <polygon fill="currentColor" points="210.63 228.042 186.588 206.671 207.958 182.63 184.042 161.37 162.671 185.412 138.63 164.042 117.37 187.958 141.412 209.329 120.042 233.37 143.958 254.63 165.329 230.588 189.37 251.958 210.63 228.042"></polygon>
                                <polygon fill="currentColor" points="383.958 182.63 360.042 161.37 338.671 185.412 314.63 164.042 293.37 187.958 317.412 209.329 296.042 233.37 319.958 254.63 341.329 230.588 365.37 251.958 386.63 228.042 362.588 206.671 383.958 182.63"></polygon>
                            </svg>
                        </div>
                    </Wrapper>
                ),
                {
                    width: 1200,
                    height: 630,
                },
            );
        }

        if (!image) {
            return new ImageResponse(
                (
                    <Wrapper>
                        <div tw="bg-gray-800 text-gray-100 h-full w-full py-8 flex justify-around">
                            <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col justify-start">
                                <div tw="flex justify-between items-center w-full">
                                    <span tw="text-center text-2xl">Сообщение</span>
                                    <span tw="text-violet-400">создано {new Date(created_date).toLocaleDateString("ru-RU")}</span>
                                </div>
                                <div tw="flex mt-8">
                                    {renderElement('Слова поддержки:', text)}
                                </div>
                                <div tw="flex mt-8">
                                    {link && renderElement('Ссылка:', link)}
                                </div>
                            </div>

                            {renderStats({ show, likes, dislikes, link_clicks, current_date })}
                        </div>
                    </Wrapper>
                ),
                {
                    width: 1200,
                    height: 630,
                },
            )
        }

        return new ImageResponse(
            (
                <Wrapper>
                    <div tw="bg-gray-800 text-gray-100 h-full w-full py-8 flex justify-around">
                        <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col justify-between">
                            <div tw="flex justify-between items-center w-full">
                                <span tw="text-center text-2xl">Сообщение</span>
                                <span tw="text-violet-400">создано {new Date(created_date).toLocaleDateString("ru-RU")}</span>
                            </div>
                            {renderElement('Слова поддержки:', text)}
                            {link && renderElement('Ссылка:', link)}
                            {renderImage(image)}
                        </div>

                        {renderStats({ show, likes, dislikes, link_clicks, current_date })}
                    </div>
                </Wrapper>
            ),
            {
                width: 1200,
                height: 630,
            },
        );
    } catch (e: any) {
        console.log(`${e.message}`);
        return new Response(`Failed to generate the image`, {
            status: 500,
        });
    }
}
