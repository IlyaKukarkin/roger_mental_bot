export type MessageForm = {
  anonymous: boolean;
  message: string;
  link?: string;
  images?: Array<unknown>;
};

export enum ActionType {
  CHANGE_MESSAGE = "CHANGE_MESSAGE",
  CHANGE_ANONYMOUS = "CHANGE_ANONYMOUS",
  CHANGE_LINK = "CHANGE_LINK",
  CHANGE_IMAGES = "CHANGE_IMAGES",
}

export type Action =
  | {
      type: ActionType.CHANGE_MESSAGE | ActionType.CHANGE_LINK;
      payload: string;
    }
  | { type: ActionType.CHANGE_ANONYMOUS }
  | { type: ActionType.CHANGE_IMAGES; payload: Array<unknown> };
