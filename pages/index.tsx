import type { NextPage } from "next";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";

import { MessageForm, PageLayout } from "../components";

const Home: NextPage = () => {
  const router = useRouter();
  const { form_id } = router.query;
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/message${window.location.search}`)
      .then((res) => {
        if (res.status !== 200) {
          router.push(`/${res.status}`);
          return;
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
          setUserName(data?.name);
          setLoading(false);
        }
      })
      .catch((err) => {
        router.push(`/500?error=${err.toString()}`);
      });
  }, []);

  if (loading || !userName || !form_id || Array.isArray(form_id)) {
    return (
      <PageLayout>
        <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-gray-300 dark:border-violet-400"></div>
      </PageLayout>
    );
  }

  return <MessageForm name={userName} form_id={form_id} />;
};

export default Home;
