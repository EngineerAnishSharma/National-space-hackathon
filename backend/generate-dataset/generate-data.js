const { faker } = require('@faker-js/faker');
const fs = require('fs');

// Set current date to March 29, 2025, for consistency
const currentDate = new Date('2025-03-29');

// Define zones based on ISS modules
const zones = [
  'Crew Quarters', 'US Laboratory', 'European Laboratory', 'Japanese Laboratory',
  'Russian Laboratory', 'Storage Area 1', 'Storage Area 2', 'Storage Area 3',
  'Docking Area 1', 'Docking Area 2', 'Docking Area 3', 'Docking Area 4',
  'Airlock', 'Service Module', 'Cupola'
];

// Define space-relevant item names
const itemNames = [
  'Dehydrated Meal Pack', 'Oxygen Cylinder', 'First Aid Kit', 'Water Container',
  'Microgravity Experiment Setup', 'Solar Panel Part', 'Communication Device',
  'Tool Kit', 'Medical Supply Kit', 'Scientific Instrument', 'Battery Pack',
  'Food Ration', 'Hygiene Kit', 'Experiment Sample', 'Spare Part'
];

// Function to generate random future date within 365 days
function getRandomFutureDate() {
  const daysToAdd = faker.number.int({ min: 1, max: 365 });
  const futureDate = new Date(currentDate);
  futureDate.setDate(currentDate.getDate() + daysToAdd);
  return futureDate.toISOString().split('T')[0];
}

// Generate containers (500 entries)
const containers = [];
for (let i = 0; i < 500; i++) {
  const zone = faker.helpers.arrayElement(zones);
  const containerId = `${zone.replace(/\s/g, '')}_${String(i + 1).padStart(3, '0')}`;
  const width = faker.number.int({ min: 50, max: 250 });
  const depth = faker.number.int({ min: 50, max: 250 });
  const height = faker.number.int({ min: 50, max: 250 });
  containers.push({ Zone: zone, 'Container ID': containerId, Width: width, Depth: depth, Height: height });
}

// Generate items (2000 entries)
const items = [];
for (let i = 0; i < 2000; i++) {
  const itemId = `item${String(i + 1).padStart(4, '0')}`;
  const name = faker.helpers.arrayElement(itemNames);
  const width = faker.number.int({ min: 5, max: 100 });
  const depth = faker.number.int({ min: 5, max: 100 });
  const height = faker.number.int({ min: 5, max: 100 });
  const mass = faker.number.int({ min: 1, max: 100 });
  const priority = faker.number.int({ min: 0, max: 100 });
  const expiryDate = faker.datatype.boolean() ? getRandomFutureDate() : 'N/A';
  const usageLimit = faker.number.int({ min: 1, max: 100 });
  const preferredZone = faker.helpers.arrayElement(zones);
  items.push({
    'Item ID': itemId, Name: name, Width: width, Depth: depth, Height: height,
    Mass: mass, Priority: priority, 'Expiry Date': expiryDate, 'Usage Limit': usageLimit,
    'Preferred Zone': preferredZone
  });
}

// Write containers to CSV
const containersCsv = 'Zone,Container ID,Width,Depth,Height\n' +
  containers.map(row => `${row.Zone},${row['Container ID']},${row.Width},${row.Depth},${row.Height}`).join('\n');
fs.writeFileSync('containers.csv', containersCsv);

// Write items to CSV
const itemsCsv = 'Item ID,Name,Width,Depth,Height,Mass,Priority,Expiry Date,Usage Limit,Preferred Zone\n' +
  items.map(row => `${row['Item ID']},${row.Name},${row.Width},${row.Depth},${row.Height},${row.Mass},${row.Priority},${row['Expiry Date']},${row['Usage Limit']},${row['Preferred Zone']}`).join('\n');
fs.writeFileSync('items.csv', itemsCsv);

console.log('Datasets generated: containers.csv and items.csv');
