export type MessageForm = {
  anonymous: boolean;
  message: string;
  link?: string;
  images?: FileList | null;
  linkError: boolean;
  imagesError: ImagesError;
  formSubmitted: boolean;
  submitting: boolean;
  submitResult: SubmitResult;
  alert_visible: boolean;
  timeoutId: NodeJS.Timeout | null;
};

export enum ImagesError {
  VALID = "VALID",
  MORE_THAN_3 = "MORE_THAN_3",
  LARGE_FILE = "LARGE_FILE",
}

export enum SubmitResult {
  UNKNOWN = "UNKNOWN",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

export enum ActionType {
  CHANGE_MESSAGE = "CHANGE_MESSAGE",
  CHANGE_ANONYMOUS = "CHANGE_ANONYMOUS",
  CHANGE_LINK = "CHANGE_LINK",
  CHANGE_IMAGES = "CHANGE_IMAGES",
  VALIDATE_LINK = "VALIDATE_LINK",
  VALIDATE_IMAGE = "VALIDATE_IMAGE",
  FORM_SUBMIT = "FORM_SUBMIT",
  SUBMIT_START = "SUBMIT_START",
  SUBMIT_END = "SUBMIT_END",
  SHOW_ALERT = "SHOW_ALERT",
  HIDE_ALERT = "HIDE_ALERT",
  SAVE_TIMER_ID = "SAVE_TIMER_ID",
}

export type Action =
  | {
      type: ActionType.CHANGE_MESSAGE | ActionType.CHANGE_LINK;
      payload: string;
    }
  | {
      type:
        | ActionType.CHANGE_ANONYMOUS
        | ActionType.FORM_SUBMIT
        | ActionType.SHOW_ALERT
        | ActionType.HIDE_ALERT
        | ActionType.SUBMIT_START;
    }
  | {
      type: ActionType.CHANGE_IMAGES;
      payload: FileList | undefined | null;
    }
  | {
      type: ActionType.SAVE_TIMER_ID;
      payload: NodeJS.Timeout;
    }
  | { type: ActionType.VALIDATE_LINK; payload: boolean }
  | { type: ActionType.VALIDATE_IMAGE; payload: ImagesError }
  | { type: ActionType.SUBMIT_END; payload: SubmitResult };
