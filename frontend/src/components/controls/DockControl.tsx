import React, { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Anchor, ChevronRight, MoveRight, Info, Check } from "lucide-react";

interface DockItem {
  id: number;
  name: string;
  containerId: string;
  area: string;
  needsRearrangement: boolean;
  rearrangementInfo?: {
    itemName: string;
    destinationContainer: string;
    destinationArea: string;
  };
}

const DockControl = () => {
  // Mock data for dock items
  const [dockItems, setDockItems] = useState<DockItem[]>([
    {
      id: 1,
      name: "Fresh Milk",
      containerId: "FRIDGE-03",
      area: "Bottom Shelf",
      needsRearrangement: true,
      rearrangementInfo: {
        itemName: "Cheese",
        destinationContainer: "FRIDGE-01",
        destinationArea: "Dairy Drawer",
      },
    },
    {
      id: 2,
      name: "Bananas",
      containerId: "COUNTER-01",
      area: "Fruit Bowl",
      needsRearrangement: false,
    },
  ]);

  const handleDock = (id: number) => {
    // Remove item from the list after docking
    setDockItems(dockItems.filter((item) => item.id !== id));
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <div className="absolute w-auto flex items-center justify-center rounded-xl top-8 right-32 bg-gray-900 p-2 shadow-lg z-10 text-white border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors">
          <Anchor size={18} />
          <div className="absolute top-0 right-0 translate-x-1/2 -translate-y-1/2 w-5 h-5 p-1 bg-blue-500 text-white rounded-full flex items-center justify-center">
            {dockItems.length > 0 && (
              <p className="text-xs font-bold text-white">{dockItems.length}</p>
            )}
          </div>
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-0 rounded-xl overflow-hidden bg-gray-900 border-gray-700 text-gray-100">
        <div className="p-2 bg-gray-800 text-gray-200 font-medium border-b border-gray-700 text-sm">
          Items to Dock
        </div>
        <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800">
          {dockItems.map((item) => (
            <DockItemCard key={item.id} item={item} onDock={handleDock} />
          ))}
        </div>
        <div className="p-2 border-t border-gray-700 flex justify-between">
          <button
            className="text-xs text-blue-400 font-medium hover:text-blue-300"
            onClick={() => setDockItems([])}
          >
            Dock All
          </button>
          <button className="text-xs text-gray-400 font-medium hover:text-gray-300">
            Cancel
          </button>
        </div>
      </PopoverContent>
    </Popover>
  );
};

function DockItemCard({
  item,
  onDock,
}: {
  item: DockItem;
  onDock: (id: number) => void;
}) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="border-b border-gray-700 hover:bg-gray-800">
      <div className="py-2 px-3 flex items-center gap-2">
        <div className="flex-grow">
          <h3 className="font-medium text-gray-200 text-sm">{item.name}</h3>
          <div className="flex text-xs text-gray-400 gap-2">
            <div>{item.containerId}</div>
            <div>•</div>
            <div>{item.area}</div>
          </div>
        </div>
        {item.needsRearrangement && (
          <div className="text-blue-400">
            <Info size={14} />
          </div>
        )}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-gray-500 hover:text-gray-300"
        >
          <ChevronRight
            size={14}
            className={`transition-transform ${showDetails ? "rotate-90" : ""}`}
          />
        </button>
        <button
          onClick={() => onDock(item.id)}
          className="text-gray-500 hover:text-blue-400 bg-gray-800 rounded-full p-1"
          title="Confirm Dock"
        >
          <Check size={14} />
        </button>
      </div>

      {showDetails && item.needsRearrangement && item.rearrangementInfo && (
        <div className="px-3 pb-2 text-xs text-gray-400">
          <div className="border-l border-gray-700 pl-3 ml-2 space-y-2">
            <p className="text-gray-300">Rearrangement needed:</p>
            <div className="flex items-center gap-1">
              <span>{item.rearrangementInfo.itemName}</span>
              <MoveRight size={12} className="text-blue-400 mx-1" />
              <span>
                {item.rearrangementInfo.destinationContainer} (
                {item.rearrangementInfo.destinationArea})
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DockControl;
