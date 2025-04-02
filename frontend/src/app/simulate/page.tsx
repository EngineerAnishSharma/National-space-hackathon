"use client";
import React, { useState } from "react";
import { Clock } from "lucide-react";
import { toast } from "react-hot-toast";
import { SearchBar } from "./_components/SearchBar";
import { DatePicker } from "./_components/DatePicker";
import { SimulateButton } from "./_components/SimulateButton";
import { SelectedItems } from "./_components/SelectedItems";
import { SimulationResults } from "./_components/SimulationResults";

interface Item {
  itemId: string;
  name: string;
}

interface SimulationResponse {
  success: boolean;
  newDate: string;
  changes: {
    itemsUsed: { itemId: string; name: string; remainingUses: number }[];
    itemsExpired: { itemId: string; name: string }[];
    itemsDepletedToday: { itemId: string; name: string }[];
  };
}

const dummyItems: Item[] = [
  { itemId: "item_5612", name: "Widget A" },
  { itemId: "item_7890", name: "Gadget B" },
  { itemId: "item_1234", name: "Tool C" },
  { itemId: "item_5678", name: "Device D" },
  { itemId: "item_9012", name: "Gear E" },
];

const dummySimulationResponse: SimulationResponse = {
  success: true,
  newDate: "2025-04-10T00:00:00Z",
  changes: {
    itemsUsed: [
      { itemId: "item_5612", name: "Widget A", remainingUses: 5 },
      { itemId: "item_7890", name: "Gadget B", remainingUses: 2 },
    ],
    itemsExpired: [{ itemId: "item_1234", name: "Tool C" }],
    itemsDepletedToday: [{ itemId: "item_5678", name: "Device D" }],
  },
};

export default function page() {
  const [selectedItems, setSelectedItems] = useState<Item[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [simulationResult, setSimulationResult] =
    useState<SimulationResponse | null>(null);
  const [filter, setFilter] = useState<
    "itemsUsed" | "itemsExpired" | "itemsDepletedToday"
  >("itemsUsed");
  const [isOpen, setOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleRemoveItem = (itemId: string) => {
    setSelectedItems((prev) => prev.filter((item) => item.itemId !== itemId));
  };

  const handleSimulate = () => {
    if (!selectedDate || selectedItems.length === 0) {
      toast.error("Please select a date and at least one item.");
      return;
    }

    setIsLoading(true);

    setTimeout(() => {
      setSimulationResult(dummySimulationResponse);
      setIsLoading(false);
      toast.success("Simulation completed successfully!");
    }, 800);
  };

  return (
    <div className="w-full h-full min-h-screen bg-gray-900 text-gray-100 rounded-lg shadow-xl overflow-hidden">
      <div className="flex items-center justify-between px-6 py-3 bg-gradient-to-r from-gray-900 to-gray-800 border-b border-indigo-900/30">
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-md bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-700/20">
            <Clock size={18} className="text-white" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Simulate Item Usage
          </h2>
        </div>
      </div>

      <div className="p-6 bg-gray-900 border-b border-gray-800">
        <div className="flex flex-col md:flex-row items-stretch gap-4">
          <SearchBar
            selectedItems={selectedItems}
            setSelectedItems={setSelectedItems}
            dummyItems={dummyItems}
            isOpen={isOpen}
            setOpen={setOpen}
          />
          <DatePicker
            selectedDate={selectedDate}
            setSelectedDate={setSelectedDate}
          />
          <SimulateButton
            isLoading={isLoading}
            handleSimulate={handleSimulate}
          />
        </div>
        <SelectedItems
          selectedItems={selectedItems}
          handleRemoveItem={handleRemoveItem}
        />
      </div>

      <SimulationResults
        simulationResult={simulationResult}
        filter={filter}
        setFilter={setFilter}
      />
    </div>
  );
}
