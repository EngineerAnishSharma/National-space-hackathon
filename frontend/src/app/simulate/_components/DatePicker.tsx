"use client";
import React from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  selectedDate: Date | null;
  setSelectedDate: React.Dispatch<React.SetStateAction<Date | null>>;
}

export function DatePicker({ selectedDate, setSelectedDate }: DatePickerProps) {
  return (
    <div className="w-full md:w-1/5">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal bg-gray-800 text-gray-100 border-2 border-gray-700 rounded-md px-4 focus:outline-none shadow-lg shadow-black/10 py-5",
              !selectedDate && "text-gray-400"
            )}
          >
            <CalendarIcon size={18} className="mr-2" />
            {selectedDate
              ? format(selectedDate, "MMM dd, yyyy")
              : "Select Date"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0 bg-gray-800 border-2 border-gray-700 rounded-md shadow-xl z-50">
          <Calendar
            mode="single"
            selected={selectedDate || undefined}
            onSelect={(date) => setSelectedDate(date || null)}
            disabled={(date) =>
              date <= new Date(new Date().setDate(new Date().getDate()))
            }
            initialFocus
            className="bg-gray-800 text-gray-100 border-none rounded-md p-2"
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
