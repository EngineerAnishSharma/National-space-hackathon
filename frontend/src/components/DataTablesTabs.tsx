'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ItemsTable } from "@/components/ItemsTable";
import { ContainersTable } from "@/components/ContainersTable";
import { Package, Archive } from "lucide-react";

export function DataTablesTabs() {
  const handleExport = async () => {
    try {
      const response = await fetch(
        "https://national-space-hackathon-1-91717359690.us-central1.run.app/api/export/arrangement"
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const csvData = await response.text();
      const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "inventory_data.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error exporting CSV:", error);
      // Handle error (e.g., show a notification to the user)
    }
  };

  return (
    <div className="w-full bg-gray-800 text-gray-100 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center">
            <Package size={18} className="text-white" />
          </div>
          <h2 className="text-xl font-bold tracking-tight">Inventory Data</h2>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="items" className="w-full">
        <div className="flex justify-between items-center">
        <TabsList className="grid w-auto grid-cols-2 border-b border-gray-700 bg-gray-800">
          <TabsTrigger
            value="items"
            className="data-[state=active]:bg-gray-700 data-[state=active]:text-white data-[state=inactive]:text-gray-400"
          >
            Items
          </TabsTrigger>
          <TabsTrigger
            value="containers"
            className="data-[state=active]:bg-gray-700 data-[state=active]:text-white data-[state=inactive]:text-gray-400"
          >
            Containers
          </TabsTrigger>
        </TabsList>

        <button
          onClick={handleExport}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-2 rounded mr-4"
        >
          Export CSV
        </button>
        </div>

        <TabsContent value="items" className="p-4">
          <ItemsTable />
        </TabsContent>
        <TabsContent value="containers" className="p-4">
          <ContainersTable />
        </TabsContent>
      </Tabs>
    </div>
  );
}