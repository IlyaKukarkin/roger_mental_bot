import React from "react";

interface Props {
  name: string;
}

const MessageForm = ({ name }: Props) => {
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    console.log(event);
  };

  return (
    <section className="p-6 h-full min-h-screen flex justify-center items-center dark:text-gray-100 dark:bg-gray-800">
      <form
        noValidate={true}
        onSubmit={handleSubmit}
        className="container w-full max-w-xl p-2 md:p-8 mx-auto space-y-6 rounded-md shadow dark:bg-gray-900 ng-untouched ng-pristine ng-valid"
      >
        <h2 className="w-full text-2xl md:text-3xl font-bold leading-tight">
          Поделись хорошим настроением
        </h2>

        <div>
          <fieldset className="w-full space-y-1 dark:text-gray-100">
            <label htmlFor="name" className="block text-sm font-medium">
              Имя
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
                  />
                </svg>
              </span>
              <input
                type="text"
                name="name"
                id="name"
                disabled={true}
                value={name}
                className="w-full py-2 pl-10 text-sm rounded-md focus:outline-none dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900 focus:dark:border-violet-400"
              />
            </div>
          </fieldset>
          <input
            type="checkbox"
            name="anonymous"
            id="anonymous"
            aria-label="Заполнить анонимно?"
            className="mr-1 rounded-sm focus:ring-violet-400 focus:dark:border-violet-400 focus:ring-2 accent-violet-400"
          />
          <label htmlFor="anonymous" className="text-sm dark:text-gray-400">
            Заполнить анонимно?
          </label>
        </div>
        <div>
          <label
            htmlFor="message"
            className="block text-sm font-medium mb-1 ml-1"
          >
            Напиши слова поддержки
          </label>
          <textarea
            id="message"
            placeholder="Привет! Когда у меня плохое настроение, я открываю плейлист по ссылке и представляю, что я маленький корабль в океане..."
            className="block w-full h-32 md:h-24 p-2 rounded autoexpand focus:outline-none focus:ring focus:ring-opacity-25 focus:ring-violet-400 dark:bg-gray-800"
          ></textarea>
        </div>
        <div>
          <fieldset className="w-full space-y-1 dark:text-gray-100">
            <label htmlFor="url" className="block text-sm font-medium">
              Приложи ссылку на плейлист/любимый фильм/мемес
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418"
                  />
                </svg>
              </span>
              <input
                type="text"
                name="url"
                id="url"
                placeholder="https://youtu.be/o-YBDTqX_ZU"
                className="w-full py-2 pl-10 text-sm rounded-md focus:outline-none dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900 focus:dark:border-violet-400"
              />
            </div>
          </fieldset>
        </div>
        <div>
          <fieldset className="w-full space-y-1 dark:text-gray-100">
            <label htmlFor="images" className="block text-sm font-medium">
              Приложи любую картиночку(и)
            </label>
            <div className="flex">
              <input
                type="file"
                name="images"
                id="images"
                className="w-full px-2 md:px-8 py-2 md:py-4 border-2 border-dashed rounded-md dark:border-gray-700 dark:text-gray-400 dark:bg-gray-800"
              />
            </div>
          </fieldset>
        </div>
        <div>
          <button
            type="submit"
            className="w-full px-4 py-2 font-bold rounded shadow focus:outline-none focus:ring hover:ring focus:ring-opacity-50 dark:bg-violet-400 focus:ring-violet-400 hover:ring-violet-400 dark:text-gray-900"
          >
            Отправить
          </button>
        </div>
      </form>
    </section>
  );
};

export default MessageForm;
