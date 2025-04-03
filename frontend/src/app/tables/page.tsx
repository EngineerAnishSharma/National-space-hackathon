'use client';

import { DataTablesTabs } from '@/components/DataTablesTabs';

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-6">
          Inventory Overview
        </h1>
        <DataTablesTabs />
      </div>
    </main>
  );
}
