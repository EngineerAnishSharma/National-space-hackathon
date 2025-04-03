"use client";

import dynamic from 'next/dynamic';
import { Suspense } from 'react';

const Toaster = dynamic(
  () => import('react-hot-toast').then((mod) => mod.Toaster),
  {
    ssr: false,
    loading: () => null,
  }
);

const Providers = ({ children }: { children: React.ReactNode }) => {
  return (
    <Suspense fallback={null}>
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1f2937',
            color: '#fff',
          },
        }}
      />
      {children}
    </Suspense>
  );
};

export default Providers;
