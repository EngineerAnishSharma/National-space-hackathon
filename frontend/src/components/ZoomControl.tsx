'use client';

import React from 'react';

interface ZoomControlProps {
  scale: number;
  setScale: React.Dispatch<React.SetStateAction<number>>;
  resetView?: () => void; // optional if you're not using it, or make it required if you need it
}

const ZoomControl: React.FC<ZoomControlProps> = ({ scale, setScale, resetView }) => {
  const zoomIn = () => setScale(prev => Math.min(prev * 1.2, 10));
  const zoomOut = () => setScale(prev => Math.max(prev / 1.2, 0.1));

  return (
    <div className="fixed bottom-4 right-4 flex items-center gap-2 bg-black/50 rounded-lg p-2">
      <button
        onClick={zoomOut}
        className="w-8 h-8 flex items-center justify-center bg-white/10 hover:bg-white/20 rounded-lg text-white"
      >
        -
      </button>
      <div className="text-white min-w-[60px] text-center">
        {Math.round(scale * 100)}%
      </div>
      <button
        onClick={zoomIn}
        className="w-8 h-8 flex items-center justify-center bg-white/10 hover:bg-white/20 rounded-lg text-white"
      >
        +
      </button>
    </div>
  );
};

export default ZoomControl;
