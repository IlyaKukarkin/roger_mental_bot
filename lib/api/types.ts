import { ObjectId } from "mongodb";

export type User = {
  form_id: ObjectId;
  telegram_username: string;
  is_volunteer: boolean;
  current_user_time: number;
  result: boolean;
  _id: ObjectId;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  time_to_send_messages: number;
  current_time: number;
  user_time: number;
  name: string;
  timezone: string;
  is_banned_from_volunteering: boolean;
  telegram_id: string;
};

export type TgMessage = {
  message_id: number;
};

export type TgResponse =
  | {
      ok: true;
      result: TgMessage;
    }
  | {
      ok: false;
      error_code: number;
      description: string;
    };

export enum APILogStage {
  ASK_MOOD = "Ask mood",
  RATE = "Rate",
}

export enum APILogErrorName {
  GENERIC = "Generic",
  TELEGRAM_API = "Telegram API",
}

export type APILogError = {
  name: APILogErrorName;
  code?: number;
  trace?: string;
};

export type APILogContext = {
  stage: APILogStage;
};

export type APILogUser = Partial<User>;

export type APILog = {
  context: APILogContext;
  user?: APILogUser;
  error?: APILogError;
};
