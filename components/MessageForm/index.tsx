import React, { useEffect, useMemo, useReducer, useRef } from "react";
import Image from "next/future/image";

import Alert from "../Alert";
import { initialState, reducer } from "./reducer";
import { ActionType, ImagesError, SubmitResult } from "./types";
import { imageValidator, linkValidator } from "./validators";
import { AlertTypes } from "../Alert/types";
import { FormDataType, User } from "../../lib/api/messages";

const ERROR_INPUT_STYLES = "border-rose-500 dark:border-rose-500";

const MessageForm = ({ name, user_id }: User) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const fileInput = useRef<null | HTMLInputElement>(null);
  const {
    message,
    anonymous,
    images,
    link,
    formSubmitted,
    submitting,
    imagesError,
    linkError,
    alert_visible,
    submitResult,
    timeoutId,
  } = state;

  useEffect(() => {
    if (images) {
      dispatch({
        type: ActionType.VALIDATE_IMAGE,
        payload: imageValidator(images),
      });

      if (fileInput.current) {
        const dataTransfer = new DataTransfer();

        images.forEach((image) => {
          dataTransfer.items.add(image);
        });

        fileInput.current.files = dataTransfer.files;
      }
    }
  }, [images]);

  useEffect(() => {
    dispatch({
      type: ActionType.VALIDATE_LINK,
      payload: link ? linkValidator(link) : false,
    });
  }, [link]);

  useEffect(() => {
    if (alert_visible) {
      const id = setTimeout(() => {
        dispatch({ type: ActionType.HIDE_ALERT });
      }, 3000);

      dispatch({ type: ActionType.SAVE_TIMER_ID, payload: id });
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [alert_visible]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    dispatch({ type: ActionType.FORM_SUBMIT });

    if (!message || linkError || imagesError !== ImagesError.VALID) {
      dispatch({ type: ActionType.SHOW_ALERT });
      return;
    }

    dispatch({ type: ActionType.SUBMIT_START });

    const form: FormDataType = {
      id_user: user_id,
      text: message,
      is_anonymous: anonymous,
      is_approved: false,
      media_link: link || "",
      image_ids: [],
    };
    const formData = new FormData();

    if (
      fileInput.current &&
      fileInput.current?.files &&
      fileInput.current?.files.length !== 0
    ) {
      Object.values(fileInput.current.files).forEach((image, index) => {
        formData.append(`image-${index}`, image);
      });

      try {
        const res = await fetch(`/api/message`, {
          method: "PUT",
          body: formData,
        });

        if (res.ok) {
          const imagesIdArray = await res.json();

          await fetch(`/api/message`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ ...form, image_ids: imagesIdArray }),
          });

          dispatch({
            type: ActionType.SUBMIT_END,
            payload: SubmitResult.SUCCESS,
          });
          return;
        }

        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      } catch (e) {
        console.log(e);
        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      }
    } else {
      await fetch(`/api/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...form }),
      });

      dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.SUCCESS });
      return;
    }
  };

  const renderImages = useMemo(() => {
    if (!images) {
      return <></>;
    }

    return (
      <div className="grid grid-cols-3 md:grid-cols-4 relative gap-2 mt-2">
        {Object.values(images)
          .slice(0, 10)
          .map((img: File, index) => {
            return (
              <div key={img.name} className="relative aspect-video">
                <div className="relative w-full z-10 flex justify-end">
                  <button
                    type="button"
                    disabled={submitting}
                    onClick={() => {
                      const tempArr = [...images];
                      tempArr.splice(index, 1);

                      dispatch({
                        type: ActionType.CHANGE_IMAGES,
                        payload: tempArr,
                      });
                    }}
                    className="text-violet-400 dark:text-violet-400 hover:cursor-pointer hover:text-violet-500 hover:dark:text-violet-500"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-6 h-6"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
                <Image
                  src={URL.createObjectURL(img)}
                  alt=""
                  fill
                  sizes="122px"
                  className="w-20 h-20 bg-center object-cover bg-cover rounded-md dark:bg-gray-500 dark:bg-gray-700"
                />
              </div>
            );
          })}
      </div>
    );
  }, [images, submitting]);

  const renderAlert = useMemo(() => {
    let messageText = "Мы всё сохранили, спасибо!";

    if (submitResult === SubmitResult.ERROR) {
      messageText = "Какие-то проблемы при сохранении, попробуй позже";
    }
    if (linkError) {
      messageText = "Ссылка не ссылка";
    }
    if (imagesError === ImagesError.MORE_THAN_3) {
      messageText = "Только 3 картинки прикрепи";
    }
    if (imagesError === ImagesError.LARGE_FILE) {
      messageText = "Одна или несколько картинок очень большие";
    }
    if (!message) {
      messageText = "Куда, напиши слова поддержки";
    }

    let alertType = AlertTypes.SUCCESS;
    if (
      !message ||
      linkError ||
      imagesError !== ImagesError.VALID ||
      submitResult === SubmitResult.ERROR
    ) {
      alertType = AlertTypes.ERROR;
    }

    return (
      <Alert
        message={messageText}
        is_displayed={alert_visible}
        type={alertType}
      />
    );
  }, [alert_visible]);

  const renderSuccess = useMemo(() => {
    if (submitResult === SubmitResult.SUCCESS) {
      return (
        <div className="absolute top-0 left-0 right-0 bottom-0 rounded-md backdrop-blur-sm z-10 w-full h-full">
          <div className="relative top-1/3 left-[10%] md:left-1/4 p-6 rounded-md right-[10%] md:right-1/4 bottom-1/4 w-[80%] md:w-1/2 flex flex-col gap-6 shadow-md bg-gray-100 dark:bg-gray-900 dark:text-gray-100">
            <h2 className="text-2xl font-semibold text-center leading-tight tracking-wide">
              Спасибо!
            </h2>
            <p className="flex-1 text-center dark:text-gray-400">
              Мы всё успешно сохранили
            </p>
            <button
              type="button"
              className="px-8 py-3 font-semibold rounded bg-violet-400 dark:bg-violet-400 dark:text-gray-900"
              onClick={() => {
                // window.location.href = "tg:resolve";
                window.location.href = "https://telegram.me/roger_mental_bot";
                window.close();
              }}
            >
              Закрыть
            </button>
          </div>
        </div>
      );
    }

    return null;
  }, [submitResult]);

  return (
    <section className="p-6 h-full min-h-screen max-h-screen flex justify-center items-center dark:text-gray-100 dark:bg-gray-800">
      {renderAlert}
      <form
        noValidate={true}
        onSubmit={handleSubmit}
        className="container relative w-full max-w-xl p-2 md:p-8 mx-auto space-y-6 rounded-md shadow bg-gray-100 dark:bg-gray-900 ng-untouched ng-pristine ng-valid"
      >
        {renderSuccess}
        <h2 className="w-full text-center text-2xl md:text-3xl font-bold leading-tight">
          Поделись хорошим настроением
        </h2>

        <div>
          <fieldset className="w-full space-y-1 dark:text-gray-100">
            <label htmlFor="name" className="block text-sm font-medium">
              Имя
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-2">
                {anonymous ? (
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
                      d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                    />
                  </svg>
                ) : (
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
                )}
              </span>
              <input
                type="text"
                name="name"
                id="name"
                disabled={true}
                value={state.anonymous ? "Аноним" : name}
                className="w-full py-2 pl-10 text-sm rounded-md focus:outline-none dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900 focus:border-violet-400"
              />
            </div>
          </fieldset>
          <input
            type="checkbox"
            name="anonymous"
            id="anonymous"
            aria-label="Заполнить анонимно?"
            onChange={() => dispatch({ type: ActionType.CHANGE_ANONYMOUS })}
            className="mr-1 rounded-sm focus:ring-violet-400 focus:border-violet-400 focus:ring-2 accent-violet-400"
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
            value={message}
            disabled={submitting}
            onChange={(e) =>
              dispatch({
                type: ActionType.CHANGE_MESSAGE,
                payload: e.target.value,
              })
            }
            maxLength={5000}
            placeholder="Привет! Когда у меня плохое настроение, я открываю плейлист по ссылке и представляю, что я маленький корабль в океане..."
            className={`block w-full max-h-96 min-h-12 h-32 md:h-24 p-2 rounded autoexpand focus:outline-none focus:ring-violet-400 focus:dark:bg-gray-900 focus:border-violet-400 dark:bg-gray-800 ${
              formSubmitted && !message ? ERROR_INPUT_STYLES : ""
            }`}
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
                disabled={submitting}
                maxLength={1000}
                value={link}
                onChange={(e) =>
                  dispatch({
                    type: ActionType.CHANGE_LINK,
                    payload: e.target.value,
                  })
                }
                placeholder="https://youtu.be/o-YBDTqX_ZU"
                className={`w-full py-2 pl-10 text-sm rounded-md focus:outline-none focus:ring-violet-400 dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900 focus:border-violet-400 ${
                  formSubmitted && linkError ? ERROR_INPUT_STYLES : ""
                }`}
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
                ref={fileInput}
                type="file"
                name="images"
                accept="image/png, image/jpeg, image/jpg, image/gif"
                multiple
                disabled={submitting}
                id="images"
                onChange={() =>
                  dispatch({
                    type: ActionType.CHANGE_IMAGES,
                    payload: Object.values(fileInput.current?.files || {}),
                  })
                }
                className={`w-full px-2 md:px-8 py-2 bg-white border-dark-500 border border-dashed rounded-md dark:border-gray-700 focus:ring-violet-400 focus:outline-none dark:border-2 dark:text-gray-400 dark:bg-gray-800 focus:dark:bg-gray-900 focus:border-violet-400 ${
                  formSubmitted && imagesError !== ImagesError.VALID
                    ? ERROR_INPUT_STYLES
                    : ""
                }`}
              />
            </div>
          </fieldset>

          {renderImages}
        </div>
        <div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full px-4 py-2 h-10 font-bold rounded shadow focus:outline-none focus:ring focus:ring-opacity-50
            bg-violet-400 focus:ring-violet-400 hover:bg-violet-500 text-gray-900 disabled:dark:bg-gray-800 disabled:bg-gray-200"
          >
            {submitting ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 rounded-full animate-pulse bg-violet-400 dark:bg-violet-400"></div>
                <div className="w-4 h-4 rounded-full animate-pulse bg-violet-400 dark:bg-violet-400"></div>
                <div className="w-4 h-4 rounded-full animate-pulse bg-violet-400 dark:bg-violet-400"></div>
              </div>
            ) : (
              "Отправить"
            )}
          </button>
        </div>
      </form>
    </section>
  );
};

export default MessageForm;
