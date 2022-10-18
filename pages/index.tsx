import type { NextPage } from "next";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";

import { MessageForm, PageLayout } from "../components";
import { User } from "../lib/api/messages";

const Home: NextPage = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

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
          setUser(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        router.push(`/500?error=${err.toString()}`);
      });
  }, []);

  if (loading || !user) {
    return (
      <PageLayout>
        <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-gray-300 dark:border-violet-400"></div>
      </PageLayout>
    );
  }

  return <MessageForm user_id={user.user_id} name={user.name} />;
};

export default Home;
