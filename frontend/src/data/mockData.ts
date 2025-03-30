import { Zone, Container, Item } from '../types/storage';

async function fetchCSV(filename: string) {
  try {
    const response = await fetch(`/data/${filename}`);
    if (!response.ok) {
      console.error(`HTTP error! status: ${response.status}`);
      throw new Error(`Failed to fetch ${filename}`);
    }
    const text = await response.text()
      .then(text => text.replace(/\/\/ filepath:.*$/gm, '')); 
    return parseCSV(text);
  } catch (error) {
    console.error('Error fetching CSV:', error);
    return [];
  }
}

function parseCSV(csv: string) {
  try {
    const lines = csv.split('\n')
      .filter(line => line.trim() && !line.startsWith('//'));
    const [headerLine, ...dataLines] = lines;
    const headers = headerLine.split(',').map(h => h.trim());
    
    return dataLines.map(line => {
      const values = line.split(',').map(v => v.trim());
      return headers.reduce((obj: any, header, i) => {
        obj[header] = values[i];
        return obj;
      }, {});
    });
  } catch (error) {
    console.error('Error parsing CSV:', error);
    return [];
  }
}

export async function loadMockData() {
  try {
    const [items, containers] = await Promise.all([
      fetchCSV('items.csv'),
      fetchCSV('containers.csv')
    ]);

    const containersByZone = containers.reduce((acc: { [key: string]: any[] }, container: any) => {
      if (!acc[container.Zone]) {
        acc[container.Zone] = [];
      }
      acc[container.Zone].push({
        id: container['Container ID'],
        width: parseInt(container.Width),
        depth: parseInt(container.Depth),
        height: parseInt(container.Height),
        items: [],
        zone: container.Zone
      });
      return acc;
    }, {});

    const itemsByZone = items.reduce((acc: { [key: string]: any[] }, item: any) => {
      if (!acc[item['Preferred Zone']]) {
        acc[item['Preferred Zone']] = [];
      }
      acc[item['Preferred Zone']].push({
        id: item['Item ID'],
        name: item.Name,
        width: parseInt(item.Width),
        depth: parseInt(item.Depth),
        height: parseInt(item.Height),
        mass: parseInt(item.Mass),
        priority: parseInt(item.Priority),
        expiryDate: item['Expiry Date'] === 'N/A' ? null : item['Expiry Date'],
        usageLimit: parseInt(item['Usage Limit']),
        usageCount: 0,
        preferredZone: item['Preferred Zone']
      });
      return acc;
    }, {});

    // Create zones with their containers and items
    const zones = Object.keys(containersByZone).map(zoneName => ({
      id: zoneName.toLowerCase().replace(/\s+/g, '_'),
      name: zoneName,
      containers: containersByZone[zoneName].map(container => ({
        ...container,
        items: itemsByZone[zoneName] || []
      }))
    }));

    console.log('Loaded zones:', zones); // Debug log
    return zones;
  } catch (error) {
    console.error('Error loading mock data:', error);
    return [];
  }
}
