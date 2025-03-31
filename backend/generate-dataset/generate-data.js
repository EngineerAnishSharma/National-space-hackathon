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
        capacity: faker.number.int({ min: 10, max: 50 }),
        width: faker.number.int({ min: 50, max: 200 }),
        depth: faker.number.int({ min: 50, max: 200 }),
        height: faker.number.int({ min: 50, max: 200 }),
        maxWeight: faker.number.int({ min: 100, max: 1000 }),
        currentWeight: 0,
        coordinates: {
          start: {
            width: faker.number.float({ min: 0, max: 50, precision: 0.1 }),
            depth: faker.number.float({ min: 0, max: 50, precision: 0.1 }),
            height: faker.number.float({ min: 0, max: 50, precision: 0.1 })
          },
          end: {
            width: faker.number.float({ min: 51, max: 100, precision: 0.1 }),
            depth: faker.number.float({ min: 51, max: 100, precision: 0.1 }),
            height: faker.number.float({ min: 51, max: 100, precision: 0.1 })
          }
        }
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
      capacity: faker.number.int({ min: 10, max: 50 }),
      width: faker.number.int({ min: 50, max: 200 }),
      depth: faker.number.int({ min: 50, max: 200 }),
      height: faker.number.int({ min: 50, max: 200 }),
      maxWeight: faker.number.int({ min: 100, max: 1000 }),
      currentWeight: 0,
      coordinates: {
        start: {
          width: faker.number.float({ min: 0, max: 50, precision: 0.1 }),
          depth: faker.number.float({ min: 0, max: 50, precision: 0.1 }),
          height: faker.number.float({ min: 0, max: 50, precision: 0.1 })
        },
        end: {
          width: faker.number.float({ min: 51, max: 100, precision: 0.1 }),
          depth: faker.number.float({ min: 51, max: 100, precision: 0.1 }),
          height: faker.number.float({ min: 51, max: 100, precision: 0.1 })
        }
      }
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
        expirationDate: faker.date.future().toISOString().split('T')[0],
        width: faker.number.int({ min: 10, max: 50 }),
        depth: faker.number.int({ min: 10, max: 50 }),
        height: faker.number.int({ min: 10, max: 50 }),
        priority: faker.number.int({ min: 1, max: 5 }),
        usageLimit: faker.number.int({ min: 1, max: 100 }),
        usageCount: 0,
        preferredZone: faker.helpers.arrayElement(ZONES).id,
        position: {
          startCoordinates: {
            width: faker.number.float({ min: 0, max: 20, precision: 0.1 }),
            depth: faker.number.float({ min: 0, max: 20, precision: 0.1 }),
            height: faker.number.float({ min: 0, max: 20, precision: 0.1 })
          },
          endCoordinates: {
            width: faker.number.float({ min: 21, max: 40, precision: 0.1 }),
            depth: faker.number.float({ min: 21, max: 40, precision: 0.1 }),
            height: faker.number.float({ min: 21, max: 40, precision: 0.1 })
          }
        }
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
  // Flatten nested objects
  const flattenedData = data.map(item => {
    const flattened = {};
    
    Object.entries(item).forEach(([key, value]) => {
      if (key === 'coordinates') {
        flattened['start_width'] = value.start.width;
        flattened['start_depth'] = value.start.depth;
        flattened['start_height'] = value.start.height;
        flattened['end_width'] = value.end.width;
        flattened['end_depth'] = value.end.depth;
        flattened['end_height'] = value.end.height;
      } else if (key === 'position') {
        flattened['position_start_width'] = value.startCoordinates.width;
        flattened['position_start_depth'] = value.startCoordinates.depth;
        flattened['position_start_height'] = value.startCoordinates.height;
        flattened['position_end_width'] = value.endCoordinates.width;
        flattened['position_end_depth'] = value.endCoordinates.depth;
        flattened['position_end_height'] = value.endCoordinates.height;
      } else {
        flattened[key] = value;
      }
    });
    
    return flattened;
  });

  // Get all unique headers
  const headers = Array.from(new Set(
    flattenedData.flatMap(obj => Object.keys(obj))
  ));
  
  // Create CSV rows
  const rows = flattenedData.map(obj =>
    headers.map(header => {
      const value = obj[header] ?? '';
      // Escape commas and quotes
      return typeof value === 'string' && (value.includes(',') || value.includes('"')) 
        ? `"${value.replace(/"/g, '""')}"` 
        : value;
    }).join(',')
  );

  return [headers.join(','), ...rows].join('\n');
}

// Save the files
fs.writeFileSync('../../frontend/public/data/containers.csv', toCSV(containers));
fs.writeFileSync('../../frontend/public/data/items.csv', toCSV(items));

console.log(`Generated ${containers.length} containers and ${items.length} items`);
