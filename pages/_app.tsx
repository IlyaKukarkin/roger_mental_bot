import type { AppProps } from "next/app";

import Head from "next/head";

import "../styles/globals.css";

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Roger mental bot</title>
        <meta name="title" content="Roger mental bot" />
        <meta
          name="description"
          content="Bot for your mental health and memes"
        />
        <meta name="keywords" content="bot, telegram, mental, memes" />
        <meta name="robots" content="index, follow" />
        <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="language" content="Russian" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#041347" />
        <meta name="msapplication-TileColor" content="#041347" />
        <meta name="theme-color" content="#ffffff" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}

export { reportWebVitals } from "next-axiom";

export default MyApp;
