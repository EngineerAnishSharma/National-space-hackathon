import { Container } from '../types/storage';

interface ContainerViewProps {
  container: Container;
  onBack: () => void;
}

export default function ContainerView({ container, onBack }: ContainerViewProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <button 
        onClick={onBack}
        className="mb-4 text-blue-600 hover:text-blue-800 flex items-center gap-2 font-semibold"
      >
        ← Back to Zone
      </button>
      
      <h2 className="text-2xl font-bold mb-6 text-blue-900">{container.zone} - Container {container.id}</h2>
      
      <div className="grid gap-6">
        <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
          <h3 className="font-bold text-blue-900 text-lg mb-3">Container Details</h3>
          <div className="text-sm text-blue-800 font-medium">
            <p className="mb-2">Dimensions: <span className="text-blue-700">{container.width}x{container.depth}x{container.height} cm</span></p>
            <p>Location: <span className="text-blue-700">{container.zone}</span></p>
          </div>
        </div>
        
        <div>
          <h3 className="font-bold text-blue-900 text-lg mb-4">Stored Items</h3>
          <div className="grid gap-4">
            {container.items.map((item) => (
              <div key={item.id} className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50 hover:bg-blue-100 transition-colors">
                <h4 className="font-bold text-blue-900 text-base mb-3">{item.name}</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <p>
                    <span className="text-blue-800 font-medium">Priority: </span>
                    <span className={`font-semibold ${
                      item.priority >= 90 ? 'text-red-700' :
                      item.priority >= 70 ? 'text-orange-700' :
                      'text-green-700'
                    }`}>{item.priority}</span>
                  </p>
                  <p>
                    <span className="text-blue-800 font-medium">Mass: </span>
                    <span className="text-blue-900 font-semibold">{item.mass}kg</span>
                  </p>
                  <p>
                    <span className="text-blue-800 font-medium">Uses: </span>
                    <span className="text-blue-900 font-semibold">{item.usageCount}/{item.usageLimit}</span>
                  </p>
                  {item.expiryDate && (
                    <p>
                      <span className="text-blue-800 font-medium">Expires: </span>
                      <span className="text-red-700 font-semibold">{item.expiryDate}</span>
                    </p>
                  )}
                </div>
              </div>
            ))}
            {container.items.length === 0 && (
              <p className="text-blue-800 font-medium">No items in this container</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
