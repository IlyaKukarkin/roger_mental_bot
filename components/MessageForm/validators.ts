import { ImagesError } from "./types";

export const imageValidator = (files: File[]): ImagesError => {
  if (files.length === 0) {
    return ImagesError.VALID;
  }

  if (files.length > 3) {
    return ImagesError.MORE_THAN_3;
  }

  let bigImages = false;
  files.forEach((file) => {
    if (file.size > 5000000) {
      bigImages = true;
    }
  });

  if (bigImages) {
    return ImagesError.LARGE_FILE;
  }

  return ImagesError.VALID;
};

export const linkValidator = (link: string): boolean => {
  const URL_REGEX =
    /^((http|https):\/\/)?[a-zа-я0-9]+([\-\.]{1}[a-zа-я0-9]+)*\.[a-zа-я]{2,5}(:[0-9]{1,5})?(\/.*)?$/i;

  return !URL_REGEX.test(link);
};
