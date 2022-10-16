import {
  Action,
  ActionType,
  ImagesError,
  MessageForm,
  SubmitResult,
} from "./types";

export const initialState: MessageForm = {
  anonymous: false,
  message: "",
  link: "",
  images: null,
  linkError: false,
  imagesError: ImagesError.VALID,
  formSubmitted: false,
  submitting: false,
  submitResult: SubmitResult.UNKNOWN,
};

export const reducer = (state: MessageForm, action: Action): MessageForm => {
  switch (action.type) {
    case ActionType.CHANGE_MESSAGE:
      return { ...state, message: action.payload };
    case ActionType.CHANGE_LINK:
      return { ...state, link: action.payload };
    case ActionType.CHANGE_ANONYMOUS:
      return { ...state, anonymous: !state.anonymous };
    case ActionType.CHANGE_IMAGES:
      return { ...state, images: action.payload };
    case ActionType.VALIDATE_LINK:
      return { ...state, linkError: action.payload };
    case ActionType.VALIDATE_IMAGE:
      return { ...state, imagesError: action.payload };
    case ActionType.FORM_SUBMIT:
      return { ...state, formSubmitted: true };
    case ActionType.SUBMIT_START:
      return { ...state, submitting: true, submitResult: SubmitResult.UNKNOWN };
    case ActionType.SUBMIT_END:
      return { ...state, submitting: false, submitResult: action.payload };
    default:
      throw new Error();
  }
};
