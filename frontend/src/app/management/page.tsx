'use client'

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import Papa from 'papaparse';
import ItemsList from '@/components/management/ItemsList';
import PlacementView from '@/components/management/PlacementView';
import AddItemModal from '@/components/management/AddItemModal';
import AddContainerModal from '@/components/management/AddContainerModal';
import StarBackground from '@/components/StarBackground';

export default function ManagementPage() {
  const [activeTab, setActiveTab] = useState<'items' | 'containers' | 'placement'>('items');
  const [showAddItem, setShowAddItem] = useState(false);
  const [showAddContainer, setShowAddContainer] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [listView, setListView] = useState<'items' | 'containers'>('items');
  interface Item {
    [key: string]: string;
  }
  const [items, setItems] = useState<Item[]>([]);
  const [containers, setContainers] = useState<Item[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [itemsRes, containersRes] = await Promise.all([
          fetch('/data/items.csv'),
          fetch('/data/containers.csv')
        ]);

        if (!itemsRes.ok || !containersRes.ok) {
          console.error('Failed to load data files');
          return;
        }

        const itemsText = await itemsRes.text();
        const containersText = await containersRes.text();

        const itemsData = Papa.parse(itemsText, { header: true }).data as Item[];
        const containersData = Papa.parse(containersText, { header: true }).data as Item[];

        setItems(itemsData);
        setContainers(containersData);
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, []);

  return (
    <div className="relative min-h-screen bg-black">
      <StarBackground />
      
      <div className="relative z-10 min-h-screen">
        <header className="sticky top-0 backdrop-blur-md bg-black/30 border-b border-white/10">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-white">Storage Management</h1>
              <Link 
                href="/"
                className="px-4 py-2 text-white/70 hover:text-white transition-colors"
              >
                ← Back to Map
              </Link>
            </div>
            
            <div className="flex justify-between items-center mt-4">
              <div className="flex gap-4">
                {(['items', 'containers', 'placement'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-2 rounded-lg transition-all ${
                      activeTab === tab
                        ? 'bg-blue-600 text-white'
                        : 'bg-white/10 text-white/70 hover:bg-white/20'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowAddItem(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white"
                >
                  <Plus className="w-4 h-4" /> Add Item
                </button>
                <button
                  onClick={() => setShowAddContainer(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
                >
                  <Plus className="w-4 h-4" /> Add Container
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-2 gap-8">
            <div className="backdrop-blur-md bg-white/5 rounded-xl p-6">
              {activeTab !== 'placement' && (
                <div className="flex justify-between items-center mb-6">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setListView('items')}
                      className={`px-4 py-2 rounded-lg ${
                        listView === 'items' ? 'bg-blue-600' : 'bg-white/10'
                      }`}
                    >
                      Items
                    </button>
                    <button
                      onClick={() => setListView('containers')}
                      className={`px-4 py-2 rounded-lg ${
                        listView === 'containers' ? 'bg-blue-600' : 'bg-white/10'
                      }`}
                    >
                      Containers
                    </button>
                  </div>
                </div>
              )}
              <ItemsList 
                mode={listView}
                onSelect={activeTab === 'placement' ? setSelectedItem : undefined}
              />
            </div>

            <div className="backdrop-blur-md bg-white/5 rounded-xl p-6">
              <PlacementView 
                mode={activeTab}
                selectedItem={selectedItem}
                onPlacementComplete={() => setSelectedItem(null)}
              />
            </div>
          </div>
        </main>
      </div>

      {showAddItem && <AddItemModal onClose={() => setShowAddItem(false)} onAdd={(item) => setItems([...items, item])} />}
      {showAddContainer && <AddContainerModal onClose={() => setShowAddContainer(false)} />}
    </div>
  );
}