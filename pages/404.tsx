import type { NextPage } from "next";
import Link from "next/link";

const Page404: NextPage = () => {
  return (
    <section className="flex items-center h-full p-16 dark:bg-gray-900 dark:text-gray-100">
      <div className="container flex flex-col items-center justify-center px-5 mx-auto my-8">
        <div className="max-w-md text-center">
          <h2 className="mb-8 font-extrabold text-9xl dark:text-gray-600">
            <span className="sr-only">Error</span>404
          </h2>
          <p className="text-2xl font-semibold md:text-3xl">
            Извини, такой страницы не существует.
          </p>
          <p className="mt-4 mb-8 dark:text-gray-400">
            Но не волнуйся, вернись на главную страницу.
          </p>
          <Link href="/">
            <a
              rel="noopener noreferrer"
              className="px-8 py-3 font-semibold rounded dark:bg-violet-400 dark:text-gray-900"
            >
              На главную страницу
            </a>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default Page404;
