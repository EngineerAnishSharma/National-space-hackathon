'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Container, PaginatedContainerResponse } from '@/data/types';

const ITEMS_PER_PAGE = 10;

export function ContainersTable() {
  const [containers, setContainers] = useState<Container[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalContainers, setTotalContainers] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(searchTerm);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
      setCurrentPage(1);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const params = new URLSearchParams();
    params.append('page', currentPage.toString());
    params.append('size', ITEMS_PER_PAGE.toString());
    if (debouncedSearchTerm) {
      params.append('search', debouncedSearchTerm);
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_URL}/api/tables/containers?${params.toString()}`
      );
      if (!response.ok) throw new Error(`Error ${response.status}`);
      const data: PaginatedContainerResponse = await response.json();
      setContainers(data.items);
      setTotalContainers(data.total);
      const total = Math.ceil(data.total / ITEMS_PER_PAGE);
      setTotalPages(total);
      if (currentPage > total && total > 0) setCurrentPage(total);
      else if (data.total === 0) setCurrentPage(1);
    } catch (err: any) {
      setError(err.message || 'Fetch error');
      setContainers([]);
      setTotalPages(1);
      setTotalContainers(0);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, debouncedSearchTerm]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleExport = () => {
    console.log('Export Containers Table Data...');
  };

  return (
    <div className="w-full bg-gray-800 text-gray-100 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800">
        <h2 className="text-xl font-bold">Container Overview</h2>
        <div className="text-sm text-gray-400">{totalContainers} entries</div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-700 bg-gray-800 flex flex-col sm:flex-row justify-between gap-4">
        <Input
          placeholder="Search ID or Zone..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-gray-700 text-white border-gray-600 focus:ring-indigo-500"
        />
        <Button onClick={handleExport} variant="outline">
          Export to CSV
        </Button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-800 text-gray-300 border-b border-gray-700">
              <TableHead>Container ID</TableHead>
              <TableHead>Zone ID</TableHead>
              <TableHead>Dimensions</TableHead>
              <TableHead>Total Items</TableHead>
              <TableHead>Expired</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-6">
                  Loading...
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-red-500 py-6">
                  {error}
                </TableCell>
              </TableRow>
            ) : containers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-6">
                  No containers found.
                </TableCell>
              </TableRow>
            ) : (
              containers.map((container) => (
                <TableRow
                  key={container.containerId}
                  className="hover:bg-indigo-900/20 transition"
                >
                  <TableCell className="font-medium">{container.containerId}</TableCell>
                  <TableCell>{container.zone}</TableCell>
                  <TableCell className="text-xs">{`${container.width}×${container.depth}×${container.height}`}</TableCell>
                  <TableCell>{container.item_count}</TableCell>
                  <TableCell>
                    <span
                      className={`text-sm font-medium ${
                        container.expired_item_count > 0
                          ? 'text-red-500'
                          : 'text-gray-300'
                      }`}
                    >
                      {container.expired_item_count}
                    </span>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalContainers > 0 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-700">
          <span className="text-sm text-gray-400">
            Page {currentPage} of {totalPages}
          </span>
          <div className="space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1 || isLoading}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages || isLoading}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
