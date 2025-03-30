'use client'
import { useState, useRef, useEffect } from 'react';
import { Zone, Container } from '../types/storage';
import ZoneView from '../components/ZoneView';
import ContainerView from '../components/ContainerView';
import { loadMockData } from '../data/mockData';
import SpaceStationSVG from '../components/SpaceStationSVG';

const ZONE_PATHS = {
  'Airlock': 'path-id-for-airlock',
  'Crew Quarters': 'path-id-for-crew-quarters',
  'Cupola': 'path-id-for-cupola',
  'Docking Area 1': 'path-id-for-docking-area-1',
  'Docking Area 2': 'path-id-for-docking-area-2',
  'Docking Area 3': 'path-id-for-docking-area-3',
  'Docking Area 4': 'path-id-for-docking-area-4',
  'European Laboratory': 'path-id-for-european-laboratory',
  'Japanese Laboratory': 'path-id-for-japanese-laboratory',
  'Russian Laboratory': 'path-id-for-russian-laboratory',
  'Service Module': 'path-id-for-service-module',
  'Storage Area 1': 'path-id-for-storage-area-1',
  'Storage Area 2': 'path-id-for-storage-area-2',
  'Storage Area 3': 'path-id-for-storage-area-3',
  'US Laboratory': 'path-id-for-us-laboratory'
};

function StarryBackground() {
  useEffect(() => {
    const starCount = 45;
    const shootingStarInterval = 8000;

    function createStar() {
      const star = document.createElement("div");
      star.className = "star";
      star.style.top = `${Math.random() * 100}%`;
      star.style.left = `${Math.random() * 100}%`;
      document.getElementById("stars")?.appendChild(star);
    }

    function createShootingStar() {
      const shootingStar = document.createElement("div");
      shootingStar.className = "shooting-star";
      shootingStar.style.top = `${Math.random() * 100}%`;
      shootingStar.style.left = `${Math.random() * 100}%`;
      const starsContainer = document.getElementById("stars");
      if (starsContainer) {
        starsContainer.appendChild(shootingStar);
        setTimeout(() => shootingStar.remove(), 3000);
      }
    }

    function generateStars() {
      for (let i = 0; i < starCount; i++) {
        createStar();
      }
    }

    function randomizeShootingStars() {
      const interval = Math.random() * shootingStarInterval;
      setTimeout(() => {
        createShootingStar();
        randomizeShootingStars();
      }, interval);
    }

    generateStars();
    randomizeShootingStars();

    return () => {
      const stars = document.getElementById("stars");
      if (stars) stars.innerHTML = '';
    };
  }, []);

  return <div id="stars" className="absolute inset-0" />;
}

export default function Home() {
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  const [selectedContainer, setSelectedContainer] = useState<Container | null>(null);
  const [hoveredZone, setHoveredZone] = useState<string | null>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);
  const isDragging = useRef(false);
  const startPosition = useRef({ x: 0, y: 0 });

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await loadMockData();
        console.log('Loaded data:', data); // Debug log
        setZones(data);
      } catch (err) {
        console.error('Error:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    startPosition.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging.current) {
      setPosition({
        x: e.clientX - startPosition.current.x,
        y: e.clientY - startPosition.current.y
      });
    }
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const newScale = Math.min(Math.max(0.5, scale - e.deltaY * 0.001), 2);
    setScale(newScale);
  };

  if (loading) {
    return <div className="p-8 text-center">Loading space station data...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-600">{error}</div>;
  }

  return (
    <div className="p-8">
      <div className="max-w-full mx-auto overflow-hidden">
        <h1 className="text-3xl font-bold mb-6 text-white relative z-10">Space Station Storage Management</h1>
        
        {!selectedZone ? (
          <div 
            className="relative h-[800px] space-background rounded-lg cursor-move overflow-hidden"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
          >
            <StarryBackground />
            <div 
              className="absolute origin-center transition-transform duration-100 z-10"
              style={{
                transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
              }}
            >
              <SpaceStationSVG
                zones={zones}
                onSelectZone={setSelectedZone}
                hoveredZone={hoveredZone}
                onZoneHover={setHoveredZone}
              />
            </div>
          </div>
        ) : selectedContainer ? (
          <ContainerView 
            container={selectedContainer} 
            onBack={() => setSelectedContainer(null)}
          />
        ) : (
          <ZoneView 
            zone={selectedZone} 
            onBack={() => setSelectedZone(null)}
            onSelectContainer={setSelectedContainer}
          />
        )}
      </div>
    </div>
  );
}
