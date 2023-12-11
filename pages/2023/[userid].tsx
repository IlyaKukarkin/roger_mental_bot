import type { NextPage, GetStaticPropsContext } from "next";

import { useEffect } from "react";
import { useRouter } from "next/router";

import { amplitude } from "../../utils/useAmplitudeInit";
import { User2023Stata } from "../../lib/api/users";
import Loading from "../../components/Loading";
import Results2023 from "../../components/Results/Results2023";

type Props = {
  statistic: User2023Stata;
};

const Results2023Page: NextPage<Props> = ({ statistic }) => {
  const router = useRouter();
  const { t: trackingId } = router.query;
  const userId = router.query.userid;

  useEffect(() => {
    amplitude.setUserId(trackingId);
    router.replace({ query: { userid: userId } }, undefined, { shallow: true });
  }, []);

  if (!statistic) {
    return (
      <section className="flex h-full min-h-screen items-center p-16 dark:bg-gray-900 dark:text-gray-100">
        {/* ToDo: add "warp" animation instead of loading spinner */}
        <Loading />
      </section>
    );
  }

  return <Results2023 statistic={statistic} />;
};

export async function getStaticProps(
  context: GetStaticPropsContext<{ userid: string }, string>,
) {
  const { params } = context;
  const userId = params && params.userid;

  // ToDo: replace for prod value
  const res = await fetch(
    `https://rogerbot.tech/api/statistic?user_id=${userId}`,
  );
  const statistic = await res.json();

  return {
    props: {
      statistic,
    },
    revalidate: 86400, // 1 Day in seconds
  };
}

export async function getStaticPaths() {
  return { paths: [], fallback: "blocking" };
}

export default Results2023Page;
