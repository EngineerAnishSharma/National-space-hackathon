const fs = require('fs');
const { faker } = require('@faker-js/faker');

// Define the standard zone IDs matching ISS.tsx
const ZONES = [
  { id: 'storage-1', name: 'Progress 1 Storage' },
  { id: 'storage-2', name: 'Progress 2 Storage' },
  { id: 'service-module', name: 'Zvezda Service Module' },
  { id: 'fgb', name: 'Zarya FGB' },
  { id: 'node-1', name: 'Unity Node 1' },
  { id: 'airlock', name: 'Quest Airlock' },
  { id: 'us-lab', name: 'Destiny Lab' },
  { id: 'node-2', name: 'Harmony Node 2' },
  { id: 'jap-lab', name: 'Kibo Japanese Lab' }
];

// Container types appropriate for space station
const CONTAINER_TYPES = [
  'Storage Rack',
  'Equipment Rack',
  'Science Rack',
  'Cargo Bag',
  'Stowage Box',
  'Supply Container',
  'Experiment Container'
];

// Item categories relevant to ISS operations
const ITEM_CATEGORIES = [
  'Food Supply',
  'Medical Supply',
  'Science Equipment',
  'Maintenance Tools',
  'Emergency Equipment',
  'Crew Supply',
  'Experimental Materials',
  'Spare Parts',
  'Life Support'
];

function generateContainers(count) {
  const containers = [];
  
  // Ensure each zone has at least 2 containers
  ZONES.forEach(zone => {
    for (let i = 0; i < 2; i++) {
      containers.push({
        id: faker.string.uuid(),
        name: `${zone.name} Container ${i + 1}`,
        type: faker.helpers.arrayElement(CONTAINER_TYPES),
        zoneId: zone.id,
        capacity: faker.number.int({ min: 10, max: 50 })
      });
    }
  });

  // Add remaining random containers
  const remainingCount = count - (ZONES.length * 2);
  for (let i = 0; i < remainingCount; i++) {
    const zone = faker.helpers.arrayElement(ZONES);
    containers.push({
      id: faker.string.uuid(),
      name: `${zone.name} Container ${faker.number.int({ min: 3, max: 99 })}`,
      type: faker.helpers.arrayElement(CONTAINER_TYPES),
      zoneId: zone.id,
      capacity: faker.number.int({ min: 10, max: 50 })
    });
  }

  return containers;
}

function generateItems(containers, itemsPerContainer) {
  const items = [];

  containers.forEach(container => {
    const itemCount = faker.number.int({ min: 1, max: itemsPerContainer });
    
    for (let i = 0; i < itemCount; i++) {
      items.push({
        id: faker.string.uuid(),
        name: faker.commerce.productName(),
        category: faker.helpers.arrayElement(ITEM_CATEGORIES),
        containerId: container.id,
        quantity: faker.number.int({ min: 1, max: 10 }),
        mass: faker.number.float({ min: 0.1, max: 25, precision: 0.1 }),
        expirationDate: faker.date.future().toISOString().split('T')[0]
      });
    }
  });

  return items;
}

// Generate the data
const containers = generateContainers(50); // 50 total containers
const items = generateItems(containers, 10); // Up to 10 items per container

// Convert to CSV
function toCSV(data) {
  const header = Object.keys(data[0]).join(',');
  const rows = data.map(obj => Object.values(obj).join(','));
  return [header, ...rows].join('\n');
}

// Save the files
fs.writeFileSync('../../frontend/public/data/containers.csv', toCSV(containers));
fs.writeFileSync('../../frontend/public/data/items.csv', toCSV(items));

console.log(`Generated ${containers.length} containers and ${items.length} items`);
