import type { NextPage } from "next";

import { BOT_LINK } from "../utils/constants";

const Page403: NextPage = () => {
  return (
    <section className="flex h-full min-h-screen items-center p-16 dark:bg-gray-900 dark:text-gray-100">
      <div className="container mx-auto my-8 flex flex-col items-center justify-center px-5">
        <div className="max-w-md text-center">
          <h2 className="mb-8 text-9xl font-extrabold dark:text-gray-600">
            <span className="sr-only">Error</span>403
          </h2>
          <p className="text-2xl font-semibold md:text-3xl">
            Форма недоступна.
          </p>
          <p className="mt-4 mb-8 dark:text-gray-400">
            Перезапроси ссылку на форму у бота, братик.
          </p>
          <a
            rel="noopener noreferrer"
            href={BOT_LINK}
            className="rounded bg-gray-300 px-8 py-3 font-semibold dark:bg-violet-400 dark:text-gray-900"
          >
            Перейти в Бота
          </a>
        </div>
      </div>
    </section>
  );
};

export default Page403;
