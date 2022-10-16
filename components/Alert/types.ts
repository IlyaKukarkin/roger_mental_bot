export type Props = {
  message: string;
  is_displayed: boolean;
  type?: AlertTypes;
};

export enum AlertTypes {
  SUCCESS = "SUCCESS",
  ERROR = "ERRROR",
}
