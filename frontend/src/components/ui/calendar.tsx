"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { DayPicker } from "react-day-picker";

import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: React.ComponentProps<typeof DayPicker>) {
  return (
    <div className="dark">
      {" "}
      {/* Force dark mode */}
      <DayPicker
        showOutsideDays={showOutsideDays}
        className={cn("p-3 bg-black text-white", className)} // Ensure dark background
        classNames={{
          months: "flex flex-col sm:flex-row gap-2",
          month: "flex flex-col gap-4",
          caption: "flex justify-center pt-1 relative items-center w-full",
          caption_label: "text-sm font-medium text-white",
          nav: "flex items-center gap-1",
          nav_button: cn(
            buttonVariants({ variant: "outline" }),
            "size-7 bg-transparent p-0 opacity-50 hover:opacity-100 border-white text-white"
          ),
          nav_button_previous: "absolute left-1",
          nav_button_next: "absolute right-1",
          table: "w-full border-collapse space-x-1",
          head_row: "flex",
          head_cell: "text-gray-400 rounded-md w-8 font-normal text-[0.8rem]", // Light gray text for better visibility
          row: "flex w-full mt-2",
          cell: cn(
            "relative p-0 text-center text-sm text-white focus-within:relative focus-within:z-20",
            "[&:has([aria-selected])]:bg-gray-700 [&:has([aria-selected].day-range-end)]:rounded-r-md",
            props.mode === "range"
              ? "[&:has(>.day-range-end)]:rounded-r-md [&:has(>.day-range-start)]:rounded-l-md first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md"
              : "[&:has([aria-selected])]:rounded-md"
          ),
          day: cn(
            buttonVariants({ variant: "ghost" }),
            "size-8 p-0 font-normal text-white aria-selected:opacity-100"
          ),
          day_range_start:
            "day-range-start aria-selected:bg-blue-500 aria-selected:text-white",
          day_range_end:
            "day-range-end aria-selected:bg-blue-500 aria-selected:text-white",
          day_selected:
            "bg-blue-500 text-white hover:bg-blue-400 focus:bg-blue-500",
          day_today: "bg-gray-800 text-white",
          day_outside: "day-outside text-gray-500 aria-selected:text-gray-500",
          day_disabled: "text-gray-600 opacity-50",
          day_range_middle:
            "aria-selected:bg-gray-700 aria-selected:text-white",
          day_hidden: "invisible",
          ...classNames,
        }}
        components={{
          IconLeft: ({ className, ...props }) => (
            <ChevronLeft
              className={cn("size-4 text-white", className)}
              {...props}
            />
          ),
          IconRight: ({ className, ...props }) => (
            <ChevronRight
              className={cn("size-4 text-white", className)}
              {...props}
            />
          ),
        }}
        {...props}
      />
    </div>
  );
}

export { Calendar };
