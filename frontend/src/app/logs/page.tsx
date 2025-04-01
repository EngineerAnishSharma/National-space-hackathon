"use client";
import React, { useState } from "react";
import { format } from "date-fns";
import { User, ArrowRight, Package, Clock } from "lucide-react";

// Define types
type ActionType = "placement" | "retrieval" | "rearrangement" | "disposal";

interface LogDetails {
  fromContainer?: string;
  toContainer?: string;
  reason?: string;
}

interface Log {
  timestamp: string;
  userId: string;
  actionType: ActionType;
  itemId: string;
  details: LogDetails;
}

interface LogsData {
  logs: Log[];
}

// Sample data (replace with your actual data if different)
const sampleData: LogsData = {
  logs: [
    {
      timestamp: "2025-03-30T10:23:15Z",
      userId: "user_789",
      actionType: "placement",
      itemId: "item_5612",
      details: {
        fromContainer: "Warehouse A",
        toContainer: "Shelf B3",
        reason: "New stock arrival",
      },
    },
    {
      timestamp: "2025-03-31T14:45:22Z",
      userId: "user_456",
      actionType: "retrieval",
      itemId: "item_7890",
      details: {
        fromContainer: "Shelf C1",
        toContainer: "Checkout",
        reason: "Customer order",
      },
    },
    {
      timestamp: "2025-04-01T09:15:30Z",
      userId: "user_123",
      actionType: "rearrangement",
      itemId: "item_2345",
      details: {
        fromContainer: "Shelf A1",
        toContainer: "Shelf A2",
        reason: "Inventory optimization",
      },
    },
    {
      timestamp: "2025-04-02T11:00:00Z",
      userId: "user_789",
      actionType: "disposal",
      itemId: "item_6789",
      details: {
        fromContainer: "Warehouse B",
        toContainer: "",
        reason: "Expired item",
      },
    },
    {
      timestamp: "2025-04-03T16:30:45Z",
      userId: "user_456",
      actionType: "placement",
      itemId: "item_1234",
      details: {
        fromContainer: "Warehouse C",
        toContainer: "Shelf D1",
        reason: "New stock arrival",
      },
    },
    {
      timestamp: "2025-04-04T08:00:00Z",
      userId: "user_123",
      actionType: "retrieval",
      itemId: "item_5678",
      details: {
        fromContainer: "Shelf E2",
        toContainer: "Checkout",
        reason: "Customer order",
      },
    },

    {
      timestamp: "2025-04-05T12:45:00Z",
      userId: "user_789",
      actionType: "rearrangement",
      itemId: "item_9101",
      details: {
        fromContainer: "Shelf F3",
        toContainer: "Shelf F4",
        reason: "Inventory optimization",
      },
    },
    {
      timestamp: "2025-04-06T15:30:00Z",
      userId: "user_456",
      actionType: "disposal",
      itemId: "item_2345",
      details: {
        fromContainer: "Warehouse A",
        toContainer: "",
        reason: "Expired item",
      },
    },
  ],
};

// Action badge styling
const getActionBadge = (actionType: ActionType) => {
  const styles = {
    placement: "bg-emerald-600",
    retrieval: "bg-blue-500",
    rearrangement: "bg-amber-500",
    disposal: "bg-rose-600",
  };
  return (
    <div
      className={`px-3 py-1 rounded-full ${
        styles[actionType] || "bg-gray-600"
      } text-white text-xs font-medium inline-flex items-center`}
    >
      {actionType.charAt(0).toUpperCase() + actionType.slice(1)}
    </div>
  );
};

// Row styling
const getRowStyle = (actionType: ActionType) => {
  const styles = {
    placement:
      "border-l-4 border-emerald-500 bg-emerald-700/20 hover:bg-emerald-600/30",
    retrieval: "border-l-4 border-blue-500 bg-blue-700/20 hover:bg-blue-600/30",
    rearrangement:
      "border-l-4 border-amber-500 bg-amber-700/20 hover:bg-amber-600/30",
    disposal: "border-l-4 border-rose-600 bg-rose-700/20 hover:bg-rose-600/30",
  };
  return styles[actionType] || "border-l-4 border-gray-500 hover:bg-gray-700";
};

// Format timestamp
const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    return {
      date: format(date, "MMM dd, yyyy"),
      time: format(date, "HH:mm:ss"),
    };
  } catch (e) {
    return { date: "Invalid date", time: "" };
  }
};

export default function LogsTable() {
  // State for filters
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [itemId, setItemId] = useState("");
  const [userId, setUserId] = useState("");
  const [actionType, setActionType] = useState("");
  const [filteredLogs, setFilteredLogs] = useState(sampleData.logs);

  // Apply filters function
  const applyFilters = () => {
    let filtered = sampleData.logs;

    if (startDate) {
      const start = `${startDate}T00:00:00Z`;
      filtered = filtered.filter((log) => log.timestamp >= start);
    }

    if (endDate) {
      const end = `${endDate}T23:59:59Z`;
      filtered = filtered.filter((log) => log.timestamp <= end);
    }

    if (itemId) {
      filtered = filtered.filter((log) => log.itemId === itemId);
    }

    if (userId) {
      filtered = filtered.filter((log) => log.userId === userId);
    }

    if (actionType) {
      filtered = filtered.filter((log) => log.actionType === actionType);
    }

    setFilteredLogs(filtered);
  };

  // Clear filters function
  const clearFilters = () => {
    setStartDate("");
    setEndDate("");
    setItemId("");
    setUserId("");
    setActionType("");
    setFilteredLogs(sampleData.logs);
  };

  return (
    <div className="w-full h-full bg-gray-800 text-gray-100 rounded-lg shadow-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-md bg-indigo-500 flex items-center justify-center">
            <Clock size={18} className="text-white" />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            Activity Logs
          </h2>
        </div>
        <div className="text-sm px-3 py-1 rounded-md bg-gray-700 text-gray-300">
          {filteredLogs.length} entries
        </div>
      </div>

      {/* Filter Section */}
      <div className="p-4 bg-gray-800 border-b border-gray-700">
        <div className="flex flex-wrap gap-4">
          {/* Start Date */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-gray-700 text-gray-100 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* End Date */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-gray-700 text-gray-100 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Item ID */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Item ID
            </label>
            <input
              type="text"
              value={itemId}
              onChange={(e) => setItemId(e.target.value)}
              className="w-full bg-gray-700 text-gray-100 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* User ID */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              User ID
            </label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full bg-gray-700 text-gray-100 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Action Type */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Action Type
            </label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full bg-gray-700 text-gray-100 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All</option>
              <option value="placement">Placement</option>
              <option value="retrieval">Retrieval</option>
              <option value="rearrangement">Rearrangement</option>
              <option value="disposal">Disposal</option>
            </select>
          </div>

          {/* Buttons */}
          <div className="flex items-end space-x-2">
            <button
              onClick={applyFilters}
              className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 transition-colors duration-200"
            >
              Filter
            </button>
            <button
              onClick={clearFilters}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors duration-200"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full table-auto">
          <thead className="sticky top-0 z-10">
            <tr className="bg-gray-800 text-gray-300 border-b border-gray-700">
              <th className="px-4 py-3 text-left font-medium">
                <div className="flex items-center space-x-2">
                  <Clock size={14} />
                  <span>Timestamp</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left font-medium">
                <div className="flex items-center space-x-2">
                  <User size={14} />
                  <span>User</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left font-medium">Action</th>
              <th className="px-4 py-3 text-left font-medium">
                <div className="flex items-center space-x-2">
                  <Package size={14} />
                  <span>Item</span>
                </div>
              </th>
              <th className="px-4 py-3 text-left font-medium">
                Movement & Reason
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length > 0 ? (
              filteredLogs.map((log, index) => {
                const { date, time } = formatTimestamp(log.timestamp);
                return (
                  <tr
                    key={index}
                    className={`${getRowStyle(
                      log.actionType
                    )} transition-all duration-150`}
                  >
                    <td className="px-4 py-3">
                      <div className="font-medium">{date}</div>
                      <div className="text-xs text-gray-400">{time}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span>{log.userId}</span>
                    </td>
                    <td className="px-4 py-3">
                      {getActionBadge(log.actionType)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-sm">{log.itemId}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col">
                        <div className="flex items-center text-sm">
                          <span className="font-medium">
                            {log.details.fromContainer}
                          </span>
                          <ArrowRight size={14} className="inline mx-1" />
                          <span className="font-medium">
                            {log.details.toContainer}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {log.details.reason}
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={5} className="text-center py-4 text-gray-400">
                  No logs found matching the filters
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
