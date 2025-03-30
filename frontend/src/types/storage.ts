export interface Item {
  id: string;
  name: string;
  width: number;
  depth: number;
  height: number;
  mass: number;
  priority: number;
  expiryDate: string | null;
  usageLimit: number;
  usageCount: number;
  preferredZone: string;
}

export interface Container {
  id: string;
  width: number;
  depth: number;
  height: number;
  items: Item[];
  zone: string;
}

export interface Zone {
  id: string;
  name: string;
  containers: Container[];
}
