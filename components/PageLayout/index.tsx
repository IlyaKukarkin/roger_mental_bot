import React, { PropsWithChildren } from "react";

const PageLayout = ({ children }: PropsWithChildren) => {
  return (
    <section className="p-6 h-full min-h-screen flex justify-center items-center dark:bg-gray-800 dark:text-gray-50">
      {children}
    </section>
  );
};

export default PageLayout;
