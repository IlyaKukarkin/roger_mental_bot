import React, { memo } from "react";

import { User2023Stata } from "../../../lib/api/users";

type Props = Pick<User2023Stata, "userCreatedAt">;

const Welcome = ({ userCreatedAt }: Props) => {
  const startDate = (createdAt: Date) => {
    const baseDate = new Date("2023-01-01T00:00:00.000+00:00");
    return createdAt > baseDate ? createdAt : baseDate;
  };

  return (
    <p>
      Твоя стата за год от t.me/rogermentalbot за{" "}
      {startDate(new Date(userCreatedAt)).toLocaleDateString()} -{" "}
      {new Date().toLocaleDateString()}
    </p>
  );
};

export default memo(Welcome);
