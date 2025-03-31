import React, { useRef, useState } from 'react';
import { Canvas, ThreeElements } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Vector3 } from 'three';

interface Item {
  id: string;
  name: string;
  category: string;
  priority: number;
  position_start_width: number;
  position_start_depth: number;
  position_start_height: number;
  width: number;
  depth: number;
  height: number;
  // ...other properties
}

const itemCategoryColors = {
  'Food Supply': '#FF9B9B',
  'Medical Supply': '#FF6B6B',
  'Science Equipment': '#4ECDC4',
  'Maintenance Tools': '#45B7D1',
  'Emergency Equipment': '#FF4646',
  'Crew Supply': '#96CEB4',
  'Experimental Materials': '#FFBE0B',
  'Spare Parts': '#9B5DE5',
  'Life Support': '#00F5D4'
};

function ItemMesh({ item, onHover, isHovered }: any) {
  const meshRef = useRef<ThreeElements['mesh']>(null);
  const baseColor = itemCategoryColors[item.category as keyof typeof itemCategoryColors] || '#2196f3';
  
  const position = new Vector3(
    item.position_start_width,
    item.position_start_height,
    item.position_start_depth
  );

  return (
    <group>
      <mesh
        ref={meshRef}
        position={position}
        onPointerOver={() => onHover(true, item)}
        onPointerOut={() => onHover(false, item)}
      >
        <boxGeometry args={[item.width, item.height, item.depth]} />
        <meshPhysicalMaterial 
          color={baseColor}
          transparent={false}
          metalness={0.7}
          roughness={0.2}
          clearcoat={1.0}
          clearcoatRoughness={0.1}
          emissive={isHovered ? baseColor : '#000000'}
          emissiveIntensity={isHovered ? 0.8 : 0}
        />
      </mesh>
      {isHovered && (
        <mesh position={position}>
          <boxGeometry args={[
            item.width + 0.4,
            item.height + 0.4,
            item.depth + 0.4
          ]} />
          <meshStandardMaterial
            color={baseColor}
            transparent
            opacity={0.3}
            emissive={baseColor}
            emissiveIntensity={2}
          />
        </mesh>
      )}
    </group>
  );
}

export default function ItemViewer3D({ items }: { items: Item[] }) {
  const [hoveredItem, setHoveredItem] = useState<Item | null>(null);
  const [viewAngle, setViewAngle] = useState<'top' | 'front' | 'side'>('front');

  const cameraPositions = {
    top: [0, 50, 0],
    front: [0, 0, 50],
    side: [50, 0, 0],
  };

  return (
    <div className="relative w-full h-[600px] rounded-xl overflow-hidden">
      <div className="absolute top-4 right-4 z-10 space-x-2">
        {Object.keys(cameraPositions).map((pos) => (
          <button
            key={pos}
            className={`px-4 py-2 rounded-lg backdrop-blur-md ${
              viewAngle === pos 
                ? 'bg-white/30 text-white' 
                : 'bg-white/10 text-white/70'
            }`}
            onClick={() => setViewAngle(pos as any)}
          >
            {pos.charAt(0).toUpperCase() + pos.slice(1)} View
          </button>
        ))}
      </div>

      {hoveredItem && (
        <div className="absolute top-4 left-4 z-10 p-4 rounded-lg backdrop-blur-md bg-white/10 text-white">
          <h3 className="font-bold text-lg">{hoveredItem.name}</h3>
          <p className="text-sm opacity-80">{hoveredItem.category}</p>
          <div className="mt-2 text-sm">
            <p>Priority: {hoveredItem.priority}</p>
            <p>Size: {hoveredItem.width}w × {hoveredItem.height}h × {hoveredItem.depth}d</p>
          </div>
        </div>
      )}

      <Canvas shadows>
        <color attach="background" args={['#000920']} />
        <fog attach="fog" args={['#000920', 5, 100]} />
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />
        <pointLight position={[0, 0, 0]} intensity={0.8} color="#ffffff" />
        
        <PerspectiveCamera
          makeDefault
          position={cameraPositions[viewAngle] as [number, number, number]}
        />
        <OrbitControls 
          enableZoom={true}
          enablePan={true}
          maxDistance={100}
          minDistance={10}
        />

        <gridHelper args={[100, 20]} />
        <axesHelper args={[50]} />

        {items.map((item) => (
          <ItemMesh
            key={item.id}
            item={item}
            onHover={(show: boolean, item: Item) => setHoveredItem(show ? item : null)}
            isHovered={hoveredItem?.id === item.id}
          />
        ))}
      </Canvas>
    </div>
  );
}
