import { ImageResponse } from '@vercel/og';
import { NextRequest } from 'next/server';
import { PropsWithChildren } from 'react';
import Calendar from '../../components/Calendar';

export const config = {
    runtime: 'experimental-edge',
};

type Props = {
    username: string;
    type: TYPE;
    data: Data[];
    compare_to_others: Compare;
}

export type Data = {
    date: string;
    mood: MOOD
}

export type Compare = {
    percent: number;
    type: 'BASE' | 'ROW'
}

export enum TYPE {
    WEEK = 'WEEK',
    WEEK2 = 'WEEK2',
    MONTH = 'MONTH'
}

export enum MOOD {
    GREEN = 'GREEN',
    YELLOW = 'YELLOW',
    ORANGE = 'ORANGE',
    RED = 'RED',
    SKIP = 'SKIP',
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

    try {
        const { searchParams } = new URL(req.url);

        // ?title=<title>
        const username = searchParams.get('username');
        const type: TYPE = (searchParams.get('type') as TYPE);
        const data: Data = JSON.parse(searchParams.get('data') || '');
        const compare_to_others = searchParams.get('compare_to_others');

        if (!username || !type || !data || !compare_to_others) {
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

        return new ImageResponse(
            (
                <Wrapper>
                    <Calendar type={type} data={data} />
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
