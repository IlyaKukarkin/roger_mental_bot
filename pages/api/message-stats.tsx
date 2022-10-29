import { ImageResponse } from '@vercel/og';
import { NextRequest } from 'next/server';
import { PropsWithChildren } from 'react';

export const config = {
    runtime: 'experimental-edge',
};

type Props = {
    approved?: boolean;
    show?: string;
    likes?: string;
    dislikes?: string;
    link_clicks: string;
    current_date: string;
    created_date?: string;
    text?: string;
    image?: string;
    link?: string;
    link_image?: string;
    link_title?: string;
}

enum TYPE {
    TEXT = 'TEXT',
    IMAGE_OR_LINK = 'IMAGE_OR_LINK',
    ALL = 'ALL'
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

    const renderStats = ({ approved, show, likes, dislikes, link_clicks, current_date }: Props) => {
        return (
            <div tw="bg-gray-900 text-gray-100 w-[40%] h-full rounded-xl p-8 flex flex-col">
                <div tw="flex justify-between items-center w-full">
                    <span tw="text-center text-2xl">Статистика</span>
                    <span tw="text-violet-400">на {new Date(current_date).toLocaleDateString("ru-RU")}</span>
                </div>
                <div tw="flex flex-col h-[90%] w-full justify-center items-center">
                    <div tw="flex flex-col h-20 justify-start items-center m-4">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{approved ? 'Да' : 'Нет'}</p>
                        <p tw="text-sm pt-8 text-gray-400 sm:text-base">Аппрувнуто модераторами</p>
                    </div>
                    <div tw="flex flex-col h-20 justify-start items-center m-4">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{show}</p>
                        <p tw="text-sm pt-8 text-gray-400 sm:text-base">Количество показов</p>
                    </div>
                    <div tw="flex flex-col h-20 justify-start items-center m-4">
                        <p tw="text-4xl font-bold leading-none lg:text-6xl">{likes} / {dislikes}</p>
                        <p tw="text-sm pt-8 text-gray-400 sm:text-base">Лайки / Дизлайки</p>
                    </div>
                    {link_clicks && (
                        <div tw="flex flex-col h-20 justify-start items-center m-4">
                            <p tw="text-4xl font-bold leading-none lg:text-6xl">{link_clicks}</p>
                            <p tw="text-sm pt-8 text-gray-400 sm:text-base">Количество переходов по ссылке</p>
                        </div>
                    )}
                </div>
            </div>
        )
    }

    const renderText = (label: string, content: string, type: TYPE) => {
        const textLength = {
            [TYPE.ALL]: 120,
            [TYPE.IMAGE_OR_LINK]: 250,
            [TYPE.TEXT]: 500
        }[type]

        const trimText = content.length < textLength ? content : `${content.slice(0, textLength)}...`

        return (
            <div tw="flex flex-col text-left">
                <div>{label}</div>
                <div tw="text-gray-400 w-full">{trimText}</div>
            </div>
        )
    }

    const renderLink = (link: string, link_image: string, link_title: string) => {
        const trimTitle = link_title.length < 35 ? link_title : `${link_title.slice(0, 35)}...`
        const trimLink = link.length < 35 ? link : `${link.slice(0, 35)}...`

        return (
            <div tw="flex flex-col text-left">
                <div tw="mb-2">Ссылка:</div>
                <div tw="flex h-18 items-center">
                    <img
                        src={link_image}
                        tw="h-18 w-18"
                        style={{
                            position: 'relative',
                            borderRadius: 12,
                            objectFit: 'cover'
                        }}
                    />
                    <div tw="flex flex-col h-18 justify-start ml-4">
                        <p tw="h-6">{trimTitle}</p>
                        <p tw="h-6 text-gray-400">{trimLink}</p>
                    </div>
                </div>
            </div>
        )
    }

    const renderImage = (image: string) => {
        return (
            <div tw="flex flex-col shrink text-left">
                <div tw="mb-2">Картинка:</div>
                <div tw="flex relative">
                    <img src={image} tw='absolute h-[256px] w-[256px] top-0 left-0 right-0 bottom-0' style={{ filter: 'blur(4px)', borderRadius: 28 }} />
                    <img
                        src={image}
                        tw="h-[256px] w-[256px]"
                        style={{
                            padding: '4px',
                            position: 'relative',
                            borderRadius: 28,
                            objectFit: 'contain'
                        }}
                    />
                </div>
            </div>
        )
    }

    try {
        const { searchParams } = new URL(req.url);

        // ?title=<title>
        const current_date = searchParams.get('current_date');
        const show = searchParams.get('show');
        const approved = searchParams.get('approved') === 'true';
        const likes = searchParams.get('likes');
        const dislikes = searchParams.get('dislikes');
        const link_clicks = searchParams.get('link_clicks') || '';
        const text = searchParams.get('text');
        const image = searchParams.get('image');
        const link_image = searchParams.get('link_image');
        const link = searchParams.get('link');
        const link_title = searchParams.get('link_title');
        const created_date = searchParams.get('created_date');

        if (!show || !likes || !dislikes || !text || !created_date || !current_date) {
            return new ImageResponse(
                (
                    <Wrapper>
                        <div tw="flex flex-col bg-gray-800 text-gray-100 w-full h-full justify-center items-center">
                            <h1 tw="text-3xl">Ошибка создания изображения</h1>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
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
                                    {renderText('Слова поддержки:', text, link && link_image && link_title ? TYPE.IMAGE_OR_LINK : TYPE.TEXT)}
                                </div>
                                <div tw="flex mt-8">
                                    {(link && link_image && link_title) && renderLink(link, link_image, link_title)}
                                </div>
                            </div>

                            {renderStats({ approved, show, likes, dislikes, link_clicks, current_date })}
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
                            {renderText('Слова поддержки:', text, link && link_image && link_title ? TYPE.ALL : TYPE.IMAGE_OR_LINK)}
                            {(link && link_image && link_title) && renderLink(link, link_image, link_title)}
                            {renderImage(image)}
                        </div>

                        {renderStats({ approved, show, likes, dislikes, link_clicks, current_date })}
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
