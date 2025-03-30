'use client'

export default function WasteManagement() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4 text-blue-900">Waste Management</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-3 text-blue-900">Expired Items</h2>
            <div className="space-y-2 text-blue-900">
              <p>No expired items found</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-3 text-blue-900">Ready for Disposal</h2>
            <div className="space-y-2 text-blue-900">
              <p>No items ready for disposal</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
