import type { NextPage } from "next";

import React, { useState, useEffect } from "react";

import { MessageForm, PageLayout } from "../components";

const Home: NextPage = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/message${window.location.search}`)
      .then((res) => {
        console.log("PAGE:", res);
        res.status === 200 ? setLoading(false) : console.log("error");
      })
      .catch((err) => {
        console.log("ERROR:", err);
      });
  }, []);

  if (loading) {
    return (
      <PageLayout>
        <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin dark:border-violet-400"></div>
      </PageLayout>
    );
  }

  return <MessageForm />;
};

export default Home;
