'use client'

import { useState } from 'react';

const CATEGORIES = [
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

export default function AddItemModal({ onClose, onAdd }: { onClose: () => void; onAdd: (item: any) => void }) {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    quantity: 1,
    mass: 0,
    priority: 1,
    width: 0,
    depth: 0,
    height: 0,
    expirationDate: '',
    usageLimit: 1
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newItem = {
      id: crypto.randomUUID(),
      ...formData,
      updatedAt: new Date().toISOString()
    };

    try {
      const response = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItem)
      });

      if (response.ok) {
        onAdd(newItem);
        onClose();
      }
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full shadow-xl border border-white/10">
        <h2 className="text-2xl font-bold text-white mb-6">Add New Item</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-white/70 text-sm">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              required
            />
          </div>

          <div>
            <label className="text-white/70 text-sm">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              required
            >
              <option value="">Select Category</option>
              {CATEGORIES.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm">Quantity</label>
              <input
                type="number"
                min="1"
                value={formData.quantity}
                onChange={(e) => setFormData(prev => ({ ...prev, quantity: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Mass (kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.mass}
                onChange={(e) => setFormData(prev => ({ ...prev, mass: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-white/70 text-sm">Width</label>
              <input
                type="number"
                value={formData.width}
                onChange={(e) => setFormData(prev => ({ ...prev, width: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Depth</label>
              <input
                type="number"
                value={formData.depth}
                onChange={(e) => setFormData(prev => ({ ...prev, depth: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Height</label>
              <input
                type="number"
                value={formData.height}
                onChange={(e) => setFormData(prev => ({ ...prev, height: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm">Priority (1-5)</label>
              <input
                type="number"
                min="1"
                max="5"
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Usage Limit</label>
              <input
                type="number"
                min="1"
                value={formData.usageLimit}
                onChange={(e) => setFormData(prev => ({ ...prev, usageLimit: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-white/70 text-sm">Expiration Date</label>
            <input
              type="date"
              value={formData.expirationDate}
              onChange={(e) => setFormData(prev => ({ ...prev, expirationDate: e.target.value }))}
              className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              required
            />
          </div>

          <div className="pt-4 flex gap-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
            >
              Add Item
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
