import React, { useEffect, useMemo, useReducer, useRef } from "react";
import Image from "next/image";
import { useRouter } from "next/router";

import Alert from "../Alert";
import { initialState, reducer } from "./reducer";
import { ActionType, ImagesError, SubmitResult } from "./types";
import { imageValidator, linkValidator } from "./validators";
import { AlertTypes } from "../Alert/types";
import { FormDataType } from "../../lib/api/messages";
import { ADMIN_USER } from "../../utils/constants";
import { amplitude } from "../../utils/useAmplitudeInit";
import { User } from "../../lib/api/types";

const ERROR_INPUT_STYLES = "border-rose-500 dark:border-rose-500";

type Props = {
  user: User;
};

const MessageForm = ({ user }: Props) => {
  const [state, dispatch] = useReducer(reducer, initialState, (state) => {
    if (user.name === ADMIN_USER) {
      return { ...state, anonymous: true };
    }
    return state;
  });
  const router = useRouter();

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

  useEffect(() => {
    let id: NodeJS.Timeout;
    if (submitResult === SubmitResult.SUCCESS) {
      id = setTimeout(() => {
        window.location.href = "https://telegram.me/RogerMentalBot";
        window.close();
      }, 3000);
    }

    return () => {
      if (id) {
        clearTimeout(id);
      }
    };
  }, [submitResult]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    dispatch({ type: ActionType.FORM_SUBMIT });

    if (!message || linkError || imagesError !== ImagesError.VALID) {
      dispatch({ type: ActionType.SHOW_ALERT });
      return;
    }

    dispatch({ type: ActionType.SUBMIT_START });

    const form: FormDataType = {
      form_id: user.form_id.toString(),
      text: message,
      is_anonymous: anonymous,
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

        if (res.status === 403) {
          amplitude.track("Form submit error", {
            user,
            error: { message: "Image upload error", code: 403 },
          });
          router.push(`/${res.status}`);
          return;
        }

        if (res.ok) {
          const imagesIdArray = await res.json();

          const formRes = await fetch(`/api/message`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ ...form, image_ids: imagesIdArray }),
          });

          if (formRes.status === 403) {
            amplitude.track("Form submit error", {
              user,
              error: { message: "Message create error", code: 403 },
            });
            router.push(`/${res.status}`);
            return;
          }

          if (formRes.ok) {
            dispatch({
              type: ActionType.SUBMIT_END,
              payload: SubmitResult.SUCCESS,
            });
            amplitude.track("Form submit success", {
              user,
            });
            return;
          }

          dispatch({
            type: ActionType.SUBMIT_END,
            payload: SubmitResult.ERROR,
          });
          amplitude.track("Form submit error", {
            user,
            error: { message: "Generic error" },
          });
        }

        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      } catch (e) {
        console.log(e);
        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      }
    } else {
      try {
        const formRes = await fetch(`/api/message`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ ...form }),
        });

        if (formRes.status === 403) {
          router.push(`/${formRes.status}`);
          return;
        }

        if (formRes.ok) {
          dispatch({
            type: ActionType.SUBMIT_END,
            payload: SubmitResult.SUCCESS,
          });
          return;
        }

        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      } catch (e) {
        dispatch({ type: ActionType.SUBMIT_END, payload: SubmitResult.ERROR });
      }
    }
  };

  const renderImages = useMemo(() => {
    if (!images) {
      return <></>;
    }

    return (
      <div className="relative mt-2 grid grid-cols-3 gap-2 md:grid-cols-4">
        {Object.values(images)
          .slice(0, 10)
          .map((img: File, index) => {
            return (
              <div key={img.name} className="relative aspect-video">
                <div className="relative z-10 flex w-full justify-end">
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
                    className="text-violet-400 hover:cursor-pointer hover:text-violet-500 dark:text-violet-400 hover:dark:text-violet-500"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="h-6 w-6"
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
                  className="h-20 w-20 rounded-md bg-cover bg-center object-cover dark:bg-gray-500 dark:bg-gray-700"
                />
              </div>
            );
          })}
      </div>
    );
  }, [images, submitting]);

  const renderAlert = useMemo(() => {
    let messageText = "Мы всё сохранили, спасибо!";
    let errorType = "";

    if (submitResult === SubmitResult.ERROR) {
      messageText = "Какие-то проблемы при сохранении, попробуй позже";
      errorType = "Generic";
    }
    if (linkError) {
      messageText = "Ссылка не ссылка";
      errorType = "Link";
    }
    if (imagesError === ImagesError.MORE_THAN_3) {
      messageText = "Только 3 картинки прикрепи";
      errorType = "Image";
    }
    if (imagesError === ImagesError.LARGE_FILE) {
      messageText = "Одна или несколько картинок очень большие";
      errorType = "Image";
    }
    if (!message) {
      messageText = "Куда, напиши слова поддержки";
      errorType = "Text";
    }

    let alertType = AlertTypes.SUCCESS;
    if (
      !message ||
      linkError ||
      imagesError !== ImagesError.VALID ||
      submitResult === SubmitResult.ERROR
    ) {
      alertType = AlertTypes.ERROR;
      alert_visible &&
        amplitude.track("Form submit error", {
          user,
          error: messageText,
          error_type: errorType,
        });
    }

    if (submitResult !== SubmitResult.SUCCESS) {
      return (
        <Alert
          message={messageText}
          is_displayed={alert_visible}
          type={alertType}
        />
      );
    }

    return null;
  }, [alert_visible]);

  const renderSuccess = useMemo(() => {
    if (submitResult === SubmitResult.SUCCESS) {
      return (
        <div className="absolute top-0 left-0 right-0 bottom-0 z-10 h-full w-full rounded-md backdrop-blur-sm">
          <div className="relative top-1/3 left-[10%] right-[10%] bottom-1/4 flex w-[80%] flex-col gap-6 rounded-md bg-gray-100 p-6 shadow-md dark:bg-gray-900 dark:text-gray-100 md:left-1/4 md:right-1/4 md:w-1/2">
            <h2 className="text-center text-2xl font-semibold leading-tight tracking-wide">
              Спасибо!
            </h2>
            <p className="flex-1 text-center dark:text-gray-400">
              Мы всё успешно сохранили
            </p>
            <button
              type="button"
              className="rounded bg-violet-400 px-8 py-3 font-semibold dark:bg-violet-400 dark:text-gray-900"
              onClick={() => {
                window.location.href = "https://telegram.me/RogerMentalBot";
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
    <section className="flex h-full max-h-screen min-h-screen items-center justify-center p-6 dark:bg-gray-800 dark:text-gray-100">
      {renderAlert}
      <form
        noValidate={true}
        onSubmit={handleSubmit}
        className="ng-untouched ng-pristine ng-valid container relative mx-auto w-full max-w-xl space-y-6 rounded-md bg-gray-100 p-2 shadow dark:bg-gray-900 md:p-8"
      >
        {renderSuccess}
        <h2 className="w-full text-center text-2xl font-bold leading-tight md:text-3xl">
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
                    stroke="currentColor"
                    version="1.1"
                    id="mdi-guy-fawkes-mask"
                    width="16px"
                    height="16px"
                    viewBox="0 0 16 16"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      style={{
                        stroke: "none",
                        fillRule: "nonzero",
                        fill: "currentColor",
                        fillOpacity: 1,
                      }}
                      d="M 14 8.667969 C 14 11.980469 11.3125 14.667969 8 14.667969 C 4.6875 14.667969 2 11.980469 2 8.667969 L 2.019531 2.953125 C 3.785156 1.921875 5.839844 1.332031 8.035156 1.332031 C 10.199219 1.332031 12.238281 1.914062 14 2.921875 L 14 8.667969 M 8.667969 13.734375 C 11.222656 13.199219 12.675781 11.757812 13.132812 8.667969 L 13.132812 3.535156 C 11.289062 2.84375 9.679688 2.226562 8.019531 2.222656 C 6.136719 2.21875 4.175781 2.902344 2.867188 3.535156 L 2.867188 8.667969 C 3.101562 10.980469 4.355469 13.175781 7.332031 13.734375 L 7.332031 12.464844 L 8.667969 12.464844 L 8.660156 13.167969 M 7.332031 10.667969 L 5.332031 10.667969 L 4 8.667969 L 6 9.332031 L 6.667969 9.332031 L 7.332031 8.667969 L 8.667969 8.667969 L 9.332031 9.332031 L 10 9.332031 L 12 8.667969 L 10.667969 10.667969 L 8.667969 10.667969 L 8 10 L 7.332031 10.667969 M 4 6.019531 C 4.425781 5.601562 5 5.367188 5.667969 5.367188 C 6.300781 5.367188 6.894531 5.601562 7.332031 6.019531 C 6.894531 6.433594 6.300781 6.667969 5.667969 6.667969 C 5 6.667969 4.425781 6.433594 4 6.019531 M 8.667969 6.019531 C 9.09375 5.601562 9.667969 5.367188 10.332031 5.367188 C 10.964844 5.367188 11.558594 5.601562 12 6.019531 C 11.558594 6.433594 10.964844 6.667969 10.332031 6.667969 C 9.667969 6.667969 9.09375 6.433594 8.667969 6.019531 Z M 8.667969 6.019531 "
                    />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="h-4 w-4"
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
                value={
                  state.anonymous || user.name === ADMIN_USER
                    ? "Аноним"
                    : user.name
                }
                className="w-full rounded-md py-2 pl-10 text-sm focus:border-violet-400 focus:outline-none dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900"
              />
            </div>
          </fieldset>
          <input
            type="checkbox"
            name="anonymous"
            id="anonymous"
            aria-label="Заполнить анонимно?"
            disabled={user.name === ADMIN_USER}
            defaultChecked={anonymous}
            onChange={() => dispatch({ type: ActionType.CHANGE_ANONYMOUS })}
            className="mr-1 rounded-sm accent-violet-400 focus:border-violet-400 focus:ring-2 focus:ring-violet-400"
          />
          <label htmlFor="anonymous" className="text-sm dark:text-gray-400">
            Заполнить анонимно?
          </label>
        </div>
        <div>
          <label
            htmlFor="message"
            className="mb-1 ml-1 block text-sm font-medium"
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
            className={`min-h-12 autoexpand block h-32 max-h-96 w-full rounded p-2 focus:border-violet-400 focus:outline-none focus:ring-violet-400 dark:bg-gray-800 focus:dark:bg-gray-900 md:h-24 ${
              formSubmitted && !message ? ERROR_INPUT_STYLES : ""
            }`}
          ></textarea>
        </div>
        <div>
          <fieldset className="w-full space-y-1 dark:text-gray-100">
            <label htmlFor="url" className="block text-sm font-medium">
              Приложи ссылку на песню/плейлист/мем/тикток/любимый фильм
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="h-4 w-4"
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
                    payload: e.target.value.trim(),
                  })
                }
                placeholder="https://youtu.be/o-YBDTqX_ZU"
                className={`w-full rounded-md py-2 pl-10 text-sm focus:border-violet-400 focus:outline-none focus:ring-violet-400 dark:bg-gray-800 dark:text-gray-100 focus:dark:bg-gray-900 ${
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
                className={`border-dark-500 w-full rounded-md border border-dashed bg-white px-2 py-2 focus:border-violet-400 focus:outline-none focus:ring-violet-400 dark:border-2 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 focus:dark:bg-gray-900 md:px-8 ${
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
            className="h-10 w-full rounded bg-violet-400 px-4 py-2 font-bold text-gray-900 shadow hover:bg-violet-500
            focus:outline-none focus:ring focus:ring-violet-400 focus:ring-opacity-50 disabled:bg-gray-200 disabled:dark:bg-gray-800"
          >
            {submitting ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="h-4 w-4 animate-pulse rounded-full bg-violet-400 dark:bg-violet-400"></div>
                <div className="h-4 w-4 animate-pulse rounded-full bg-violet-400 dark:bg-violet-400"></div>
                <div className="h-4 w-4 animate-pulse rounded-full bg-violet-400 dark:bg-violet-400"></div>
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
