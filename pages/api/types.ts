export type CronLogData = {
  name: CronName;
  error?: LogError;
};

export type LogError = {
  name: CronLogError;
  code?: number;
  trace?: string;
};

export enum CronName {
  MOOD = "Mood",
  DISLIKE = "Dislike",
  RATE = "Rate",
  STATA = "Stata",
}

export enum CronLogEvent {
  START = "Start cron: ",
  SUCCESS = "Success cron: ",
  ERROR = "Error cron: ",
}

export enum CronLogError {
  GENERIC = "Generic",
  UNAUTHORIZED = "Unauthorized",
}
