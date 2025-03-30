'use client'
import { useState, useRef, useEffect } from 'react';
import { Zone, Container } from '../types/storage';
import ZoneView from '../components/ZoneView';
import ContainerView from '../components/ContainerView';
import { loadMockData } from '../data/mockData';

function getZonePosition(index: number, totalZones: number) {
  // Calculate grid dimensions based on total zones
  const gridSize = Math.ceil(Math.sqrt(totalZones));
  const row = Math.floor(index / gridSize);
  const col = index % gridSize;
  
  // Calculate sizes with gaps
  const cellSize = 250; // px
  const gap = 20; // px
  
  return {
    left: col * (cellSize + gap),
    top: row * (cellSize + gap),
    width: cellSize,
    height: cellSize
  };
}

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
              {zones.map((zone, index) => {
                const pos = getZonePosition(index, zones.length);
                return (
                  <div
                    key={zone.id}
                    className="absolute transition-all duration-300 rounded-lg border-2 border-blue-400/30"
                    style={{
                      left: pos.left,
                      top: pos.top,
                      width: pos.width,
                      height: pos.height,
                    }}
                    onClick={() => setSelectedZone(zone)}
                    onMouseEnter={() => setHoveredZone(zone.id)}
                    onMouseLeave={() => setHoveredZone(null)}
                  >
                    <div 
                      className={`h-full w-full p-6 rounded-lg ${
                        hoveredZone === zone.id ? 'bg-blue-500/50' : 'bg-gray-700/50'
                      }`}
                    >
                      <h3 className="text-xl font-bold text-white mb-2">{zone.name}</h3>
                      <div className="text-white/80 text-sm">
                        <p>{zone.containers.length} containers</p>
                        <p>{zone.containers.reduce((acc, cont) => acc + cont.items.length, 0)} items</p>
                      </div>
                    </div>
                  </div>
                );
              })}
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
