'use client';

// No longer needs useEffect, useState, Papa

// Use the same interfaces as ManagementPage
interface Item {
    itemId: string;
    name: string;
    width: number | null;
    depth: number | null;
    height: number | null;
    mass: number | null;
    priority: number | null;
    expiryDate: string | null;
    usageLimit: string | number | null;
    preferredZone: string | null;
    _key?: string; // Use the unique key
}

interface Container {
    containerId: string;
    zone: string | null;
    width: number | null;
    depth: number | null;
    height: number | null;
     _key?: string; // Use the unique key
}


interface ItemsListProps {
  mode: 'items' | 'containers';
  items: Item[];
  containers: Container[];
  onSelect?: (item: any) => void; // Keep if selection is needed
}

export default function ItemsList({ mode, items, containers, onSelect }: ItemsListProps) {

  const dataToShow = mode === 'items' ? items : containers;
  const isEmpty = dataToShow.length === 0;

  const renderEmptyState = () => (
    <div className="flex items-center justify-center h-[200px] text-center text-white/50">
        {mode === 'items'
            ? "No items added yet.\nPlease add items manually or upload a CSV file."
            : "No containers added yet.\nPlease add containers manually or upload a CSV file."
        }
    </div>
  );

  const renderTable = () => (
     <div className="overflow-x-auto overflow-y-auto max-h-[450px] custom-scrollbar border border-white/10 rounded-lg"> {/* Adjust max-h-* as needed */}
        <table className="min-w-full divide-y divide-white/10">
            <thead className="bg-white/10 sticky top-0 backdrop-blur-sm"> 
                {mode === 'items' ? (
                    <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">ID</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Name</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Dimensions (H×W×D cm)</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Mass (kg)</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Priority</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Expiry</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Usage</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Zone Pref.</th>
                         {/* Add Action column if needed */}
                         {/* <th scope="col" className="relative px-4 py-3"><span className="sr-only">Actions</span></th> */}
                    </tr>
                ) : ( // Containers
                    <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Container ID</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Zone</th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-white/70 uppercase tracking-wider">Dimensions (H×W×D cm)</th>
                         {/* Add Action column if needed */}
                         {/* <th scope="col" className="relative px-4 py-3"><span className="sr-only">Actions</span></th> */}
                    </tr>
                )}
            </thead>
            <tbody className="bg-black/30 divide-y divide-white/10">
                {mode === 'items' ? items.map((item) => (
                    <tr key={item._key || item.itemId} className={`hover:bg-white/10 ${onSelect ? 'cursor-pointer' : ''}`} onClick={() => onSelect?.(item)}>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">{item.itemId}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white font-medium">{item.name}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">
                            {item.height ?? '?' }×{item.width ?? '?' }×{item.depth ?? '?'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">{item.mass ?? 'N/A'}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">{item.priority ?? 'N/A'}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">
                             {item.expiryDate ? new Date(item.expiryDate).toLocaleDateString() : 'N/A'}
                        </td>
                         <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">
                            {item.usageLimit ? `${item.usageLimit}${typeof item.usageLimit === 'number' ? ' uses' : ''}` : 'N/A'}
                        </td>
                         <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">{item.preferredZone ?? 'Any'}</td>
                         {/* Add actions cell if needed */}
                         {/* <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium"> Edit / Delete </td> */}
                    </tr>
                )) : containers.map((cont) => (
                     <tr key={cont._key || cont.containerId} className={`hover:bg-white/10 ${onSelect ? 'cursor-pointer' : ''}`} onClick={() => onSelect?.(cont)}>
                         <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">{cont.containerId}</td>
                         <td className="px-4 py-3 whitespace-nowrap text-sm text-white font-medium">{cont.zone ?? 'N/A'}</td>
                         <td className="px-4 py-3 whitespace-nowrap text-sm text-white/90">
                            {cont.height ?? '?' }×{cont.width ?? '?' }×{cont.depth ?? '?'}
                        </td>
                         {/* Add actions cell if needed */}
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
  );


  return (
    // Use flex-grow to make the table container fill available space
    <div className="flex flex-col flex-grow min-h-0"> {/* Allow shrinking and growing */}
        {isEmpty ? renderEmptyState() : renderTable()}
    </div>
  );
}