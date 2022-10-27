import type { NextPage } from "next";

import { BOT_LINK } from "../utils/constants";

const Page403: NextPage = () => {
  return (
    <section className="flex items-center h-full min-h-screen p-16 dark:bg-gray-900 dark:text-gray-100">
      <div className="container flex flex-col items-center justify-center px-5 mx-auto my-8">
        <div className="max-w-md text-center">
          <h2 className="mb-8 font-extrabold text-9xl dark:text-gray-600">
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
            className="px-8 py-3 font-semibold rounded bg-gray-300 dark:bg-violet-400 dark:text-gray-900"
          >
            Перейти в Бота
          </a>
        </div>
      </div>
    </section>
  );
};

export default Page403;
