import type { NextPage, GetStaticProps } from "next";
import type { User } from "../lib/api/types";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useLingui } from "@lingui/react";

import { MessageForm } from "../components";
import { amplitude } from "../utils/useAmplitudeInit";
import { loadCatalog } from "../utils/useLocales";
import Loading from "../components/Loading";

export const getStaticProps: GetStaticProps = async (ctx) => {
  const translation = await loadCatalog(ctx.locale!);

  return {
    props: {
      translation,
    },
  };
};

const Home: NextPage = () => {
  const router = useRouter();
  const { form_id } = router.query;
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  /**
   * This hook is needed to subscribe your
   * component for changes if you use t`` macro
   */
  useLingui();

  useEffect(() => {
    fetch(`/api/message${window.location.search}`)
      .then((res) => {
        if (res.status !== 200) {
          amplitude.track("Form open error", {
            error: { code: res.status },
            form_id,
          });
          router.push(`/${res.status}`);
          return;
        }
        return res.json();
      })
      .then((data: User | null) => {
        if (data) {
          setUser(data);
          amplitude.setUserId(data._id.toString());
          amplitude.track("Form open", { user: data, form_id });
          setLoading(false);
          return;
        }
        amplitude.track("Form open error", { user: data, form_id });
      })
      .catch((err) => {
        amplitude.track("Form open error", {
          error: { message: err.toString(), code: 500 },
          form_id,
        });
        router.push(`/500?error=${err.toString()}`);
      });
  }, [form_id, router]);

  if (loading || !user || !form_id || Array.isArray(form_id)) {
    return <Loading />;
  }

  return <MessageForm user={user} />;
};

export default Home;
