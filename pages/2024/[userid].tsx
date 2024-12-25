import type { NextPage, GetStaticPropsContext } from "next";

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useLingui } from "@lingui/react";

import { amplitude } from "../../utils/useAmplitudeInit";
import { UserYearlyStata } from "../../lib/api/users";
import Results2024 from "../../components/Results/Results2024";
import Loading from "../../components/Results/components/loadingWarp/loading";
import { loadCatalog } from "../../utils/useLocales";

import styles from "./styles.module.css";

type Props = {
  statistic: UserYearlyStata;
};

const Results2024Page: NextPage<Props> = ({ statistic }) => {
  const router = useRouter();
  const { t: trackingId } = router.query;
  const userId = router.query.userid;
  const [showLoadingAnimation, setShowLoadingAnimation] = useState(true);

  /**
   * This hook is needed to subscribe your
   * component for changes if you use t`` macro
   */
  useLingui();

  useEffect(() => {
    // Mobile ViewPort height fix
    // First we get the viewport height and we multiple it by 1% to get a value for a vh unit
    let vh = window.innerHeight * 0.01;

    // Then we set the value in the --vh custom property to the root of the document
    document.documentElement.style.setProperty("--vh", `${vh}px`);

    setTimeout(() => setShowLoadingAnimation(false), 1500);

    if (trackingId) {
      amplitude.setUserId(trackingId);
      router.replace({ query: { userid: userId } }, undefined, {
        shallow: true,
      });
    }
  }, [router, trackingId, userId]);

  if (showLoadingAnimation || router.isFallback) {
    return (
      <div
        className={`relative flex h-screen items-center justify-center bg-gray-800 text-gray-100 md:pt-24 ${styles.root}`}
      >
        <div
          className={`relative h-full w-full bg-results text-gray-100 md:aspect-[9/16] md:h-[calc(100%-64px)] md:w-auto md:rounded-xl`}
        >
          <div
            className={`flex h-full w-full cursor-pointer flex-col items-center justify-center text-center`}
          >
            <Loading />
          </div>
        </div>
      </div>
    );
  }

  return <Results2024 statistic={statistic} />;
};

export async function getStaticProps(
  context: GetStaticPropsContext<{ userid: string }, string>,
) {
  const { params, locale } = context;
  const userId = params && params.userid;

  const apiURL =
    process.env.NODE_ENV === "development"
      ? "http://localhost:3000/api"
      : "https://rogerbot.tech/api";

  const [res, translation] = await Promise.all([
    fetch(`${apiURL}/statistic?user_id=${userId}`),
    loadCatalog(locale!),
  ]);
  const statistic = await res.json();

  console.log(statistic);

  return {
    props: {
      statistic: { ...statistic, userId },
      translation,
    },
    revalidate: 86400, // 1 Day in seconds
  };
}

export async function getStaticPaths() {
  return { paths: [], fallback: "blocking" };
}

export default Results2024Page;
