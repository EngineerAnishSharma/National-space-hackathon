import { Zone, Container } from '../types/storage';

interface ZoneViewProps {
  zone: Zone;
  onBack: () => void;
  onSelectContainer: (container: Container) => void;
}

export default function ZoneView({ zone, onBack, onSelectContainer }: ZoneViewProps) {
  return (
    <div className="bg-purple-300 rounded-lg shadow p-6">
      <button 
        onClick={onBack}
        className="mb-4 text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        ← Back to Overview
      </button>
      
      <h2 className="text-2xl font-bold mb-6">{zone.name}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {zone.containers.map((container) => (
          <div
            key={container.id}
            onClick={() => onSelectContainer(container)}
            className="p-4 border rounded-lg cursor-pointer hover:bg-red-50"
          >
            <h3 className="font-semibold mb-2">Container {container.id}</h3>
            <div className="text-sm text-blue-600">
              <p>Dimensions: {container.width}x{container.depth}x{container.height} cm</p>
              <p>Items: {container.items.length}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
