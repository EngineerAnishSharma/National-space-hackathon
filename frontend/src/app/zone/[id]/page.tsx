'use client'

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import StarBackground from '@/components/StarBackground';

interface Container {
  id: string;
  name: string;
  type: string;
  zoneId: string;
  width: number;
  depth: number;
  height: number;
  capacity: number;
  start_width: number;
  start_depth: number;
  start_height: number;
  end_width: number;
  end_depth: number;
  end_height: number;
  currentWeight: number;
  maxWeight: number;
}

export default function ZonePage() {
  const params = useParams();
  const [containers, setContainers] = useState<Container[]>([]);

  useEffect(() => {
    if (!params?.id) return;

    fetch('/data/containers.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data as Container[];
        const zoneContainers = data.filter(c => c.zoneId === params.id);
        setContainers(zoneContainers);
      });
  }, [params?.id]);

  if (!params?.id) return null;

  return (
    <div className="relative min-h-screen bg-black">
      <StarBackground />
      
      {/* Main content with scroll */}
      <div className="relative z-10 h-screen overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="sticky top-0 z-20 backdrop-blur-md bg-black/30 p-4 rounded-lg shadow-xl mb-8">
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-bold text-white">
                Zone: {(Array.isArray(params.id) ? params.id[0] : params.id).replace('-', ' ').toUpperCase()}
              </h1>
              <Link 
                href="/"
                className="px-4 py-2 backdrop-blur-sm bg-white/20 hover:bg-white/30 rounded-lg text-white transition-all"
              >
                ← Back to Map
              </Link>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-8">
            {containers.map(container => (
              <Link 
                key={container.id}
                href={`/container/${container.id}`}
                className="backdrop-blur-md bg-white/10 rounded-lg overflow-hidden hover:bg-white/20 transition-all duration-300 border border-white/20"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-white">{container.name}</h2>
                    <span className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full">
                      {container.type}
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Dimensions</p>
                        <p className="font-medium text-white">
                          {container.width}w × {container.depth}d × {container.height}h
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">Capacity</p>
                        <p className="font-medium text-white">{container.capacity} units</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-gray-400 mb-1">Location Coordinates</p>
                      <div className="text-sm bg-gray-50/10 p-2 rounded">
                        <p className="text-white">Start: ({container.start_width}, {container.start_depth}, {container.start_height})</p>
                        <p className="text-white">End: ({container.end_width}, {container.end_depth}, {container.end_height})</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center pt-2">
                      <div>
                        <p className="text-gray-400">Weight</p>
                        <p className="font-medium text-white">
                          {container.currentWeight}/{container.maxWeight} kg
                        </p>
                      </div>
                      <div className="text-blue-400 hover:text-blue-600">
                        View Details →
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
