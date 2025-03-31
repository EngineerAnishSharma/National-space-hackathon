import { promises as fs } from 'fs';
import path from 'path';
import Papa from 'papaparse';

export async function loadContainersData() {
  const containersFile = await fs.readFile(
    path.join(process.cwd(), 'public/data/containers.csv'),
    'utf-8'
  );
  return Papa.parse(containersFile, { header: true }).data;
}

export async function loadItemsData() {
  const itemsFile = await fs.readFile(
    path.join(process.cwd(), 'public/data/items.csv'),
    'utf-8'
  );
  return Papa.parse(itemsFile, { header: true }).data;
}
