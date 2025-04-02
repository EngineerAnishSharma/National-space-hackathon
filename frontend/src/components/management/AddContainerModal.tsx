'use client'

import { useState } from 'react';

const CONTAINER_TYPES = [
  'Storage Rack',
  'Equipment Rack',
  'Science Rack',
  'Cargo Bag',
  'Stowage Box',
  'Supply Container',
  'Experiment Container'
];

interface AddContainerModalProps {
  onClose: () => void;
}

export default function AddContainerModal({ onClose }: AddContainerModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    capacity: 10,
    width: 0,
    depth: 0,
    height: 0,
    maxWeight: 100
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/containers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onClose();
      }
    } catch (error) {
      console.error('Error adding container:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full shadow-xl border border-white/10">
        <h2 className="text-2xl font-bold text-white mb-6">Add New Container</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-white/70 text-sm">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm">Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
              className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
            >
              <option value="">Select Type</option>
              {CONTAINER_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm">Capacity</label>
              <input
                type="number"
                value={formData.capacity}
                onChange={(e) => setFormData(prev => ({ ...prev, capacity: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Max Weight</label>
              <input
                type="number"
                value={formData.maxWeight}
                onChange={(e) => setFormData(prev => ({ ...prev, maxWeight: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
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
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Depth</label>
              <input
                type="number"
                value={formData.depth}
                onChange={(e) => setFormData(prev => ({ ...prev, depth: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="text-white/70 text-sm">Height</label>
              <input
                type="number"
                value={formData.height}
                onChange={(e) => setFormData(prev => ({ ...prev, height: Number(e.target.value) }))}
                className="w-full bg-white/5 rounded-lg px-3 py-2 text-white"
              />
            </div>
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
              Add Container
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
