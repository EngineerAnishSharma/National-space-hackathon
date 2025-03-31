'use client'

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Papa from 'papaparse';

export default function ZonePage({ params }: { params: { id: string } }) {
  const [containers, setContainers] = useState([]);

  useEffect(() => {
    fetch('/data/containers.csv')
      .then(response => response.text())
      .then(csv => {
        const data = Papa.parse(csv, { header: true }).data;
        const zoneContainers = data.filter(c => c.zoneId === params.id);
        setContainers(zoneContainers);
      });
  }, [params.id]);

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Containers in Zone {params.id}</h1>
      <div className="grid grid-cols-3 gap-4">
        {containers.map(container => (
          <Link 
            key={container.id}
            href={`/container/${container.id}`}
            className="p-4 border rounded hover:bg-gray-100"
          >
            <h2>{container.name}</h2>
            <p>Type: {container.type}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
