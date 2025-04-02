"use client";
import React, { useCallback, useRef } from "react";
import { Package } from "lucide-react";
import { Command as CommandPrimitive } from "cmdk";
import {
  CommandGroup,
  CommandItem,
  CommandList,
  CommandInput,
} from "@/components/ui/command";

interface Item {
  itemId: string;
  name: string;
}

interface SearchBarProps {
  selectedItems: Item[];
  setSelectedItems: React.Dispatch<React.SetStateAction<Item[]>>;
  dummyItems: Item[];
  isOpen: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export function SearchBar({
  selectedItems,
  setSelectedItems,
  dummyItems,
  isOpen,
  setOpen,
}: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const commandRef = useRef<HTMLDivElement>(null);

  const handleSelectOption = useCallback(
    (item: Item) => {
      if (!selectedItems.find((i) => i.itemId === item.itemId)) {
        setSelectedItems((prev) => [...prev, item]);
      }
      setOpen(false);
      if (inputRef.current) {
        inputRef.current.blur();
        inputRef.current.value = "";
      }
    },
    [selectedItems, setOpen, setSelectedItems]
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      const input = inputRef.current;
      if (!input) return;

      if (event.key === "Enter" && input.value) {
        const optionToSelect = dummyItems.find(
          (item) => item.name.toLowerCase() === input.value.toLowerCase()
        );
        if (optionToSelect) {
          handleSelectOption(optionToSelect);
          input.blur();
        }
      }

      if (event.key === "Escape") {
        input.blur();
        setOpen(false);
      }
    },
    [handleSelectOption, dummyItems, setOpen]
  );

  const handleBlur = useCallback(() => {
    setTimeout(() => {
      setOpen(false);
    }, 100);
  }, [setOpen]);

  const handleFocus = useCallback(() => {
    setOpen(true);
  }, [setOpen]);

  return (
    <div className="relative w-full md:w-3/5">
      <div ref={commandRef} className="relative">
        <CommandPrimitive
          onKeyDown={handleKeyDown}
          className="w-full border-2 border-gray-700 rounded-md bg-gray-800 shadow-lg shadow-black/10"
        >
          <CommandInput
            ref={inputRef}
            onBlur={handleBlur}
            onFocus={handleFocus}
            placeholder="Search Items..."
            className="text-base bg-transparent text-gray-100 pl-10 py-6 focus:outline-none"
          />
          {isOpen && (
            <div className="absolute top-full left-0 right-0 z-50 mt-1 rounded-md bg-gray-800 border-2 border-gray-700 shadow-xl">
              <CommandList className="max-h-60 overflow-y-auto">
                <CommandGroup heading="Available Items">
                  {dummyItems
                    .filter(
                      (item) =>
                        !selectedItems.find((i) => i.itemId === item.itemId)
                    )
                    .map((item) => (
                      <CommandItem
                        key={item.itemId}
                        value={item.name}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                        }}
                        onSelect={() => handleSelectOption(item)}
                        className="flex w-full items-center gap-2 hover:bg-indigo-600/20 cursor-pointer px-3 py-2 rounded-md my-1 mx-1 transition-colors duration-200 text-gray-100"
                      >
                        <Package size={16} className="text-indigo-400" />
                        <div>
                          <div>{item.name}</div>
                          <div className="text-xs text-gray-400">
                            {item.itemId}
                          </div>
                        </div>
                      </CommandItem>
                    ))}
                </CommandGroup>
              </CommandList>
            </div>
          )}
        </CommandPrimitive>
      </div>
    </div>
  );
}
