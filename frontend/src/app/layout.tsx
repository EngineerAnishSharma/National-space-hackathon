import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Providers from '@/providers/Providers';
require('dotenv').config()

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ISS Inventory Management',
  description: 'Manage and track inventory on the International Space Station',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body  suppressHydrationWarning className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
