import type { NextPage, GetStaticPropsContext } from "next";

import { useEffect, useState } from "react";
import { useRouter } from "next/router";

import { amplitude } from "../../utils/useAmplitudeInit";
import { User2023Stata } from "../../lib/api/users";
import Results2023 from "../../components/Results/Results2023";
import Loading from "../../components/Results/components/loadingWarp/loading";

type Props = {
  statistic: User2023Stata;
};

const Results2023Page: NextPage<Props> = ({ statistic }) => {
  const router = useRouter();
  const { t: trackingId } = router.query;
  const userId = router.query.userid;
  const [showLoadingAnimation, setShowLoadingAnimation] = useState(true);

  useEffect(() => {
    setTimeout(() => setShowLoadingAnimation(false), 3000);

    amplitude.setUserId(trackingId);
    router.replace({ query: { userid: userId } }, undefined, { shallow: true });
  }, []);

  if (showLoadingAnimation || !statistic) {
    return (
      <div className="relative flex h-screen items-center justify-center bg-gray-800 text-gray-100 md:pt-24">
        <div
          className={`relative h-full w-full bg-gray-900 text-gray-100 md:aspect-[9/16] md:h-[calc(100%-64px)] md:w-auto md:rounded-xl`}
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

  return <Results2023 statistic={statistic} />;
};

const mockData: Partial<User2023Stata> = {
  general: {
    totalRates: 12,
    totalRatesWithMood: 10,
    averageUserTotalRates: 5,
    userMentalRating: 3,
    userSupportRating: 2,
  },
  months: {
    0: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    1: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    2: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    3: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    4: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    5: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    6: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    7: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    8: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    9: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    10: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
    11: {
      0: 0,
      1: 1,
      2: 2,
      3: 3,
      4: 4,
    },
  },
  messages: {
    test: {
      likes: 5,
      dislikes: 2,
      rates: 7,
    },
  },
};

export async function getStaticProps(
  context: GetStaticPropsContext<{ userid: string }, string>,
) {
  const { params } = context;
  const userId = params && params.userid;

  // const res = await fetch(
  //   `https://rogerbot.tech/api/statistic?user_id=${userId}`,
  // );
  // const statistic = await res.json();

  return {
    props: {
      statistic: mockData,
    },
    revalidate: 86400, // 1 Day in seconds
  };
}

export async function getStaticPaths() {
  return { paths: [], fallback: "blocking" };
}

export default Results2023Page;
