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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Item, PaginatedItemResponse, ItemStatus } from '@/data/types';
import { format } from 'date-fns';

const ITEMS_PER_PAGE = 10;

export function ItemsTable() {
  const [items, setItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<ItemStatus | ''>('');
  const [preferredZoneFilter, setPreferredZoneFilter] = useState('');
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
    if (debouncedSearchTerm) params.append('search', debouncedSearchTerm);
    if (statusFilter) params.append('status', statusFilter);
    if (preferredZoneFilter) params.append('preferred_zone', preferredZoneFilter);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_URL}/api/tables/items?${params.toString()}`
      );
      if (!response.ok) throw new Error(`Error ${response.status}`);
      const data: PaginatedItemResponse = await response.json();
      setItems(data.items);
      setTotalItems(data.total);
      const total = Math.ceil(data.total / ITEMS_PER_PAGE);
      setTotalPages(total);
      if (currentPage > total && total > 0) setCurrentPage(total);
      else if (data.total === 0) setCurrentPage(1);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch items');
      setItems([]);
      setTotalItems(0);
      setTotalPages(1);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, debouncedSearchTerm, statusFilter, preferredZoneFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleExport = () => {
    console.log('Export Items Table Data...');
  };

  const getStatusBadge = (status: ItemStatus) => {
    const colorMap = {
      ACTIVE: 'bg-green-600',
      WASTE_EXPIRED: 'bg-rose-600',
      WASTE_DEPLETED: 'bg-amber-500',
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium text-white ${
          colorMap[status] || 'bg-gray-500'
        }`}
      >
        {status.replace('_', ' ').toLowerCase().replace(/(^\w|\s\w)/g, (m) =>
          m.toUpperCase()
        )}
      </span>
    );
  };

  return (
    <div className="w-full bg-gray-800 text-gray-100 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800">
        <h2 className="text-xl font-bold">Items Overview</h2>
        <div className="text-sm text-gray-400">{totalItems} entries</div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-700 bg-gray-800 flex flex-col gap-4 sm:flex-row sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <Input
            placeholder="Search name, ID, zones..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-gray-700 text-white border-gray-600"
          />
          <Select
            value={statusFilter || 'all'}
            onValueChange={(value) =>
              setStatusFilter(value === 'all' ? '' : (value as ItemStatus))
            }
          >
            <SelectTrigger className="w-[180px] bg-gray-700 text-white border-gray-600">
              <SelectValue placeholder="Filter by Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              {Object.values(ItemStatus).map((status) => (
                <SelectItem key={status} value={status}>
                  {status.replace('_', ' ').toLowerCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            placeholder="Filter Preferred Zone"
            value={preferredZoneFilter}
            onChange={(e) => setPreferredZoneFilter(e.target.value)}
            className="w-[180px] bg-gray-700 text-white border-gray-600"
          />
        </div>
        <Button onClick={handleExport} variant="outline">
          Export to CSV
        </Button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader >
            <TableRow className="!bg-white-800  border-b border-gray-700">
              <TableHead>Name</TableHead>
              <TableHead>Item ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Container</TableHead>
              <TableHead>Current Zone</TableHead>
              <TableHead>Preferred Zone</TableHead>
              <TableHead>Expiry</TableHead>
              <TableHead>Uses</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Dimensions</TableHead>
              <TableHead>Mass</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
  {isLoading ? (
    <TableRow key="loading">
      <TableCell colSpan={11} className="text-center py-6">
        Loading...
      </TableCell>
    </TableRow>
  ) : error ? (
    <TableRow key="error">
      <TableCell colSpan={11} className="text-center text-red-500 py-6">
        {error}
      </TableCell>
    </TableRow>
  ) : items.length === 0 ? (
    <TableRow key="no-items">
      <TableCell colSpan={11} className="text-center py-6">
        No items found.
      </TableCell>
    </TableRow>
  ) : (
    items.map((item) => (
      <TableRow key={item.id} className="hover:bg-indigo-900/20 transition">
        <TableCell className="font-medium">{item.name}</TableCell>
        <TableCell className="font-mono text-sm">{item.id}</TableCell>
        <TableCell>{getStatusBadge(item.status)}</TableCell>
        <TableCell>{item.containerId || 'N/A'}</TableCell>
        <TableCell>{item.currentZone || 'N/A'}</TableCell>
        <TableCell>{item.preferredZone || 'N/A'}</TableCell>
        <TableCell>
          {item.expirationDate
            ? format(new Date(item.expirationDate), 'PP')
            : 'N/A'}
        </TableCell>
        <TableCell>
          {item.currentUses} / {item.usageLimit ?? '∞'}
        </TableCell>
        <TableCell>{item.priority}</TableCell>
        <TableCell className="text-xs">
          {`${item.width}×${item.depth}×${item.height}`}
        </TableCell>
        <TableCell>{item.mass} kg</TableCell>
      </TableRow>
    ))
  )}
</TableBody>

        </Table>
      </div>

      {/* Pagination */}
      {totalItems > 0 && (
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
