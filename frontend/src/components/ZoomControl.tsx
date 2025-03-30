import { ListRestart, Minus, Plus } from "lucide-react";
import React from "react";

interface ZoomControlProps {
  scale: number;
  setScale: React.Dispatch<React.SetStateAction<number>>;
  resetView: () => void;
}

const ZoomControl: React.FC<ZoomControlProps> = ({
  scale,
  setScale,
  resetView,
}) => {
  return (
    <>
      {/* Reset Button */}
      <div
        className="absolute w-auto flex items-center justify-center rounded-xl bottom-14 right-4 bg-gray-900 p-2 shadow-lg z-10 text-white border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors"
        onClick={resetView}
      >
        <ListRestart size={18} />
      </div>

      {/* Zoom Controls */}
      <div className="absolute w-auto flex items-center justify-center rounded-xl bottom-4 right-4 bg-gray-900 p-1 shadow-lg z-10 text-white border border-gray-700">
        <div
          className="flex items-center justify-center p-1 cursor-pointer hover:text-gray-300 transition-colors"
          onClick={() => setScale((prev) => Math.max(prev - 0.1, 0.7))}
          aria-label="Zoom out"
        >
          <Minus size={16} />
        </div>
        <div className="w-[1px] h-[16px] bg-gray-700 mx-1"></div>
        <div className="flex items-center justify-center px-2 pointer-events-none text-xs font-medium text-gray-300">
          {Math.round(scale * 100) - 70}%
        </div>
        <div className="w-[1px] h-[16px] bg-gray-700 mx-1"></div>
        <div
          className="flex items-center justify-center p-1 cursor-pointer hover:text-gray-300 transition-colors"
          onClick={() => setScale((prev) => Math.min(prev + 0.1, 2))}
          aria-label="Zoom in"
        >
          <Plus size={16} />
        </div>
      </div>
    </>
  );
};

export default ZoomControl;
