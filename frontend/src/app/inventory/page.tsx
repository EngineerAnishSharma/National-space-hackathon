'use client'
import { mockItems } from '../../data/mockData';

export default function Inventory() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4 text-blue-900">Inventory Management</h1>
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 text-blue-900">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left pb-2">Item Name</th>
                  <th className="text-left pb-2">Priority</th>
                  <th className="text-left pb-2">Zone</th>
                  <th className="text-left pb-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {mockItems.map(item => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{item.name}</td>
                    <td className="py-2">{item.priority}</td>
                    <td className="py-2">{item.preferredZone}</td>
                    <td className="py-2">
                      {item.expiryDate ? `Expires: ${item.expiryDate}` : 'No expiry'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
