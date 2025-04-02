"use client";
import React from "react";

interface SimulateButtonProps {
  isLoading: boolean;
  handleSimulate: () => void;
}

export function SimulateButton({
  isLoading,
  handleSimulate,
}: SimulateButtonProps) {
  return (
    <div className="w-full md:w-1/5">
      <button
        onClick={handleSimulate}
        disabled={isLoading}
        className={`w-full bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-500 transition-all duration-300 font-medium shadow-lg shadow-indigo-700/20 border-2 border-indigo-700 ${
          isLoading ? "opacity-70 cursor-not-allowed" : ""
        }`}
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Processing...
          </div>
        ) : (
          "Simulate"
        )}
      </button>
    </div>
  );
}
