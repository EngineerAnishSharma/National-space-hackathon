'use client'

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Papa from 'papaparse';

export default function ContainerPage() {
  const params = useParams();
  const [items, setItems] = useState([]);

  useEffect(() => {
    if (!params?.id) return;
    
    fetch('/data/items.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data;
        const containerItems = data.filter(i => i.containerId === params.id);
        setItems(containerItems);
      });
  }, [params?.id]);

  if (!params?.id) return null;

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Items in Container {params.id}</h1>
      <div className="grid grid-cols-3 gap-4">
        {items.map(item => (
          <div key={item.id} className="p-4 border rounded">
            <h2>{item.name}</h2>
            <p>Category: {item.category}</p>
            <p>Quantity: {item.quantity}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
