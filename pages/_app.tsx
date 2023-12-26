import type { AppProps } from "next/app";

import { i18n } from "@lingui/core";
import { I18nProvider } from "@lingui/react";
import Head from "next/head";

import useAmplitudeInit from "../utils/useAmplitudeInit";
import Loading from "../components/Loading";
import { useLinguiInit } from "../utils/useLocales";

import "../styles/globals.css";

function MyApp({ Component, pageProps }: AppProps) {
  const loading = useAmplitudeInit();
  console.log(pageProps);
  useLinguiInit(pageProps.translation);

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
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-touch-icon.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon-16x16.png"
        />
        <link rel="manifest" href="/site.webmanifest" />
        <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#041347" />
        <meta name="msapplication-TileColor" content="#041347" />
        <meta name="theme-color" content="#ffffff" />
      </Head>
      {loading ? (
        <Loading />
      ) : (
        <I18nProvider i18n={i18n}>
          <Component {...pageProps} />
        </I18nProvider>
      )}
    </>
  );
}

export { reportWebVitals } from "@logtail/next";

export default MyApp;
