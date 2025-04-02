'use client'

import { useEffect, useState } from 'react';
import Papa from 'papaparse';

interface ItemsListProps {
  mode: 'items' | 'containers';
  onSelect?: (item: any) => void;
}

export default function ItemsList({ mode, onSelect }: ItemsListProps) {
  const [items, setItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const file = mode === 'items' ? '/data/items.csv' : '/data/containers.csv';
      const response = await fetch(file);

      if (!response.ok) {
        throw new Error(`Failed to load ${mode} data`);
      }

      const csv = await response.text();
      const data = Papa.parse(csv, { header: true }).data;
      setItems(data.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()));
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [mode]);

  const handleAddItem = (newItem: any) => {
    setItems((prevItems) => [newItem, ...prevItems]);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-white/70">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-[600px] overflow-y-auto custom-scrollbar">
      {items.map((item) => (
        <div 
          key={item.id}
          onClick={() => onSelect?.(item)}
          className={`bg-white/10 p-4 rounded-lg hover:bg-white/20 transition-colors ${
            onSelect ? 'cursor-pointer' : ''
          }`}
        >
          <p className="text-white">{item.name}</p>
          <p className="text-white/70 text-sm">{item.category}</p>
        </div>
      ))}
    </div>
  );
}
