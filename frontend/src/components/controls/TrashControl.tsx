import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Trash, ChevronRight } from "lucide-react";
import { useState } from "react";

export function TrashControl() {
  const trashItems = [
    {
      id: 1,
      name: "Leftover Pasta",
      expiryDate: "2025-04-02",
      containerId: "FRIDGE-01",
      area: "Main Shelf",
    },
    {
      id: 2,
      name: "Yogurt",
      expiryDate: "2025-04-05",
      containerId: "FRIDGE-02",
      area: "Door Compartment",
    },
  ];

  return (
    <Popover>
      <PopoverTrigger asChild>
        <div className="absolute w-auto flex items-center justify-center rounded-xl top-8 right-18 bg-gray-900 p-2 shadow-lg z-10 text-white border border-gray-700 cursor-pointer">
          <Trash size={18} />
          <div className="absolute top-0 right-0 translate-x-1/2 -translate-y-1/2 w-5 h-5 p-1 bg-red-500 text-white rounded-full flex items-center justify-center">
            {trashItems.length > 0 && (
              <p className="text-xs font-bold text-white">
                {trashItems.length}
              </p>
            )}
          </div>
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-0 rounded-xl overflow-hidden bg-gray-900 border-gray-700 text-gray-100">
        <div className="p-2 bg-gray-800 text-gray-200 font-medium border-b border-gray-700 text-sm">
          Items to Discard
        </div>
        <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800">
          {trashItems.map((item) => (
            <TrashItemCard key={item.id} item={item} />
          ))}
        </div>
        <div className="p-2 border-t border-gray-700 flex justify-between">
          <button className="text-xs text-red-400 font-medium hover:text-red-300">
            Discard All
          </button>
          <button className="text-xs text-gray-400 font-medium hover:text-gray-300">
            Cancel
          </button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

function TrashItemCard({
  item,
}: {
  item: {
    id: number;
    name: string;
    expiryDate: string;
    containerId: string;
    area: string;
  };
}) {
  const [showSteps, setShowSteps] = useState(false);

  const formatDate = (dateString: any) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="border-b border-gray-700 hover:bg-gray-800">
      <div className="py-2 px-3 flex items-center gap-2">
        <div className="flex-grow">
          <h3 className="font-medium text-gray-200 text-sm">{item.name}</h3>
          <div className="flex text-xs text-gray-400 gap-2">
            <div>{formatDate(item.expiryDate)}</div>
            <div>•</div>
            <div>{item.area}</div>
          </div>
        </div>
        <button
          onClick={() => setShowSteps(!showSteps)}
          className="text-gray-500 hover:text-gray-300 mr-1"
        >
          <ChevronRight
            size={14}
            className={`transition-transform ${showSteps ? "rotate-90" : ""}`}
          />
        </button>
        <button className="text-gray-500 hover:text-red-400">
          <Trash size={14} />
        </button>
      </div>

      {showSteps && (
        <div className="px-3 pb-2 text-xs text-gray-400">
          <div className="border-l border-gray-700 pl-3 ml-2 space-y-2">
            <p>1. Remove from {item.containerId}</p>
            <p>2. Clean container if needed</p>
            <p>3. Check for recycling options</p>
          </div>
        </div>
      )}
    </div>
  );
}
