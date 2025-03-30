import React from "react";
import { CalendarControl } from "./CalendarControl";
import { TrashControl } from "./TrashControl";
import DockControl from "./DockControl";

const Controls = ({
  date,
  setDate,
}: {
  date: Date | undefined;
  setDate: React.Dispatch<React.SetStateAction<Date | undefined>>;
}) => {
  return (
    <>
      <DockControl />
      <TrashControl />
      <CalendarControl date={date} setDate={setDate} />
    </>
  );
};

export default Controls;
