import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarDays } from "lucide-react";
import { Calendar } from "../ui/calendar";

export function CalendarControl({
  date,
  setDate,
}: {
  date: Date | undefined;
  setDate: React.Dispatch<React.SetStateAction<Date | undefined>>;
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <div className="absolute w-auto flex items-center justify-center rounded-xl top-8 right-4 bg-gray-900 p-2 shadow-lg z-10 text-white border border-gray-700 cursor-pointer">
          <CalendarDays size={18} />
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0 rounded-xl overflow-hidden border-gray-700">
        <Calendar mode="single" selected={date} onSelect={setDate} />
      </PopoverContent>
    </Popover>
  );
}
