"use client";

import { Toaster } from "react-hot-toast";

const Providers = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
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
    </>
  );
};

export default Providers;
