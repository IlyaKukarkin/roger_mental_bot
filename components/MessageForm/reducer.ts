import { Action, ActionType, MessageForm } from "./types";

export const initialState: MessageForm = {
  anonymous: false,
  message: "",
  link: "",
  images: [],
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
    default:
      throw new Error();
  }
};
