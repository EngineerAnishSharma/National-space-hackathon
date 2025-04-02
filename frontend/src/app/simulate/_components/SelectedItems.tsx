"use client";
import React from "react";
import { Package } from "lucide-react";

interface Item {
  itemId: string;
  name: string;
}

interface SelectedItemsProps {
  selectedItems: Item[];
  handleRemoveItem: (itemId: string) => void;
}

export function SelectedItems({
  selectedItems,
  handleRemoveItem,
}: SelectedItemsProps) {
  return (
    selectedItems.length > 0 && (
      <div className="mt-4 flex flex-wrap gap-2 w-full">
        {selectedItems.map((item) => (
          <div
            key={item.itemId}
            className="bg-gray-800 text-gray-100 px-4 py-2 rounded-md flex items-center border-2 border-gray-700 shadow-sm shadow-purple-900/10 transition-all duration-200 hover:border-indigo-700"
          >
            <Package size={14} className="text-indigo-400 mr-2" />
            <span>{item.name}</span>
            <span className="text-xs text-gray-400 mx-2">·</span>
            <span className="text-xs text-gray-400">{item.itemId}</span>
            <button
              onClick={() => handleRemoveItem(item.itemId)}
              className="ml-3 text-gray-400 hover:text-red-400 focus:outline-none rounded-full hover:bg-red-500/10 p-1 transition-colors"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    )
  );
}
