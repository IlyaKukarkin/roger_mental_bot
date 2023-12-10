import React, { PropsWithChildren } from "react";

const PageLayout = ({ children }: PropsWithChildren) => {
  return (
    <section className="flex h-full min-h-screen items-center justify-center p-6 dark:bg-gray-800 dark:text-gray-50">
      {children}
    </section>
  );
};

export default PageLayout;
