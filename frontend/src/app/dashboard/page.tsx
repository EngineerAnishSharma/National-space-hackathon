export default function Dashboard() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Mission Control Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-3">Active Missions</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Chandrayaan-3</span>
                <span className="text-green-500">Active</span>
              </div>
              <div className="flex justify-between">
                <span>Aditya-L1</span>
                <span className="text-blue-500">In Transit</span>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-3">Recent Updates</h2>
            <div className="space-y-2 text-sm">
              <p>Latest telemetry data received</p>
              <p>Mission parameters nominal</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
