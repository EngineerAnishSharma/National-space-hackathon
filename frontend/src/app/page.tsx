'use client'

import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import ISS from "@/components/ISS";
import ZoomControl from "@/components/ZoomControl";
import { StarryBackground } from '@/components/StarryBackground';

export default function HomePage() {
  const [translateX, setTranslateX] = useState<number>(0);
  const [translateY, setTranslateY] = useState<number>(0);
  const [scale, setScale] = useState<number>(0.7);
  const [tooltip, setTooltip] = useState({
    visible: false,
    x: 0,
    y: 0, 
    title: "",
    totalModules: 0,
    totalEquipment: 0
  });
  const [containers, setContainers] = useState([]);
  const [items, setItems] = useState([]);

  useEffect(() => {
    // Load containers
    fetch('/data/containers.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data;
        setContainers(data);
      });

    // Load items
    fetch('/data/items.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data;
        setItems(data);
      });
  }, []);

  const resetView = () => {
    setTranslateX(0);
    setTranslateY(0);
    setScale(0.7);
  };

  return (
    <div className="h-screen">
      <div className="relative h-screen bg-[#01041f]">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-[#01041f] to-[#082b33]" />
          <StarryBackground />
        </div>
        <div className="relative z-10">
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
        </div>
      </div>
    </div>
  );
}
