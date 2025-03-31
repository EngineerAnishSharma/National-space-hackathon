'use client'

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import StarBackground from '@/components/StarBackground';

interface Item {
  id: string;
  name: string;
  priority: number;
  category: string;
  quantity: number;
  position_start_width: number;
  position_start_depth: number;
  position_start_height: number;
  position_end_width: number;
  position_end_depth: number;
  position_end_height: number;
  mass: number;
  usageCount: number;
  usageLimit: number;
  expirationDate: string;
  containerId: string;
  zoneId: string;
}

export default function ContainerPage() {
  const params = useParams();
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    if (!params?.id) return;
    
    fetch('/data/items.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data as Item[];
        const containerItems = data.filter(i => i.containerId === params.id);
        setItems(containerItems);
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
                Container Details
              </h1>
              <div className="space-x-4">
                <Link 
                  href={`/zone/${items[0]?.zoneId || ''}`}
                  className="px-4 py-2 backdrop-blur-sm bg-white/20 hover:bg-white/30 rounded-lg text-white transition-all"
                >
                  ← Back to Zone
                </Link>
                <Link 
                  href="/"
                  className="px-4 py-2 backdrop-blur-sm bg-white/20 hover:bg-white/30 rounded-lg text-white transition-all"
                >
                  ← Back to Map
                </Link>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-8">
            {items.map(item => (
              <div key={item.id} className="backdrop-blur-md bg-white/10 rounded-lg overflow-hidden border border-white/20">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-white/90">{item.name}</h2>
                    <span className={`px-3 py-1 text-sm rounded-full ${
                      getPriorityColor(item.priority)
                    }`}>
                      Priority {item.priority}
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-white/70">Category</p>
                        <p className="font-medium text-white/90">{item.category}</p>
                      </div>
                      <div>
                        <p className="text-white/70">Quantity</p>
                        <p className="font-medium text-white/90">{item.quantity} units</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-white/70">Position</p>
                      <div className="text-sm bg-white/5 p-2 rounded">
                        <p>Start: ({item.position_start_width}, {item.position_start_depth}, {item.position_start_height})</p>
                        <p>End: ({item.position_end_width}, {item.position_end_depth}, {item.position_end_height})</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-white/70">Mass</p>
                        <p className="font-medium text-white/90">{item.mass} kg</p>
                      </div>
                      <div>
                        <p className="text-white/70">Usage</p>
                        <p className="font-medium text-white/90">{item.usageCount}/{item.usageLimit}</p>
                      </div>
                    </div>

                    <div className="pt-2">
                      <p className="text-white/70">Expiration Date</p>
                      <p className={`font-medium ${
                        isNearExpiry(item.expirationDate) ? 'text-red-400' : 'text-white/90'
                      }`}>
                        {new Date(item.expirationDate).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function getPriorityColor(priority: 1 | 2 | 3 | 4 | 5 | number) {
  const colors = {
    1: 'bg-red-400 text-red-900',
    2: 'bg-orange-400 text-orange-900',
    3: 'bg-yellow-400 text-yellow-900',
    4: 'bg-blue-400 text-blue-900',
    5: 'bg-green-400 text-green-900'
  };
  return colors[priority as keyof typeof colors] || 'bg-gray-400 text-gray-900';
}

interface ExpiryCheck {
  (date: string): boolean;
}

const isNearExpiry: ExpiryCheck = (date) => {
  const expiryDate = new Date(date);
  const today = new Date();
  const daysUntilExpiry = (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
  return daysUntilExpiry < 30;
}
