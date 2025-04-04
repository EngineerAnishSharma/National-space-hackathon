'use client'

import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import ISS from "@/components/ISS";
import ZoomControl from "@/components/ZoomControl"; 
import { StarryBackground } from '@/components/StarryBackground';
import Link from 'next/link';
import { Plus, ZoomIn, ZoomOut } from 'lucide-react';

export default function HomePage() {
  const [translateX, setTranslateX] = useState<number>(0);
  const [translateY, setTranslateY] = useState<number>(0);
  const [scale, setScale] = useState<number>(0.7);
  const [tooltip, setTooltip] = useState({
    visible: false,
    x: 0,
    y: 0, 
    title: "",
    totalContainers: 0,
    totalItems: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  interface Item {
    id: string;
    containerId: string;
    [key: string]: any;
  }
  
  const [containers, setContainers] = useState<any[]>([]);
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([
      fetch('/data/containers.csv')
        .then(response => response.text())
        .then(csv => {
          const data = Papa.parse(csv, { header: true }).data;
          setContainers(data);
        }),
      fetch('/data/items.csv')
        .then(response => response.text())
        .then(csv => {
          const data = Papa.parse(csv, { header: true }).data as Item[];
          setItems(data);
        })
    ]).finally(() => setIsLoading(false));
  }, []);

  const resetView = () => {
    setTranslateX(0);
    setTranslateY(0);
    setScale(0.7);
  };

  const zoomIn = () => {
    setScale(prev => Math.min(prev * 1.2, 2));
  };

  const zoomOut = () => {
    setScale(prev => Math.max(prev * 0.8, 0.3));
  };

  const formatZoomPercentage = () => {
    return `${Math.round(scale * 100)}%`;
  };

  if (isLoading) {
    return (
      <div className="h-screen bg-[#01041f] flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="h-screen">
      <div className="relative h-screen bg-[#01041f]">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-[#01041f] to-[#082b33]" />
          <StarryBackground />
        </div>
        <div className="relative z-10">
          {!isLoading && (
            <>
              <ISS
                translateX={translateX}
                setTranslateX={setTranslateX}
                translateY={translateY}
                setTranslateY={setTranslateY}
                scale={scale}
                setScale={setScale}
                tooltip={tooltip}
                setTooltip={setTooltip}
                containers={containers}
                items={items}
              />
<ZoomControl scale={scale} setScale={setScale} resetView={resetView} />

{/* <div
  className="fixed bottom-20 right-4 z-50 flex items-center gap-1 bg-black/20 backdrop-blur-md 
    border border-white/10 rounded-full shadow-lg px-2"
>
  <button
    onClick={zoomIn}
    className="p-2 hover:bg-white/10 text-white/90 rounded-full
      transition-all duration-200 hover:scale-105"
  >
    <ZoomIn className="w-5 h-5" />
  </button>
</div> */}
              <Link 
                href="/management"
                className="fixed bottom-30 right-2 z-50 px-6 py-3 bg-black/20 backdrop-blur-md 
                  border border-white/10 text-white/90 rounded-full shadow-lg flex items-center gap-2
                  transition-all duration-200 hover:scale-105 hover:bg-white/10"
              >
                <Plus className="w-5 h-5" />
                Manage Items & Containers
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
