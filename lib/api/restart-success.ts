import { sendMessageToAdmins } from "./users";

export const sendRestartSuccessNotification = async (): Promise<null> => {
  await sendMessageToAdmins("Успешно рестартанул ботов")
  return null
};