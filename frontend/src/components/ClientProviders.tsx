'use client';

import { ReactNode } from 'react';
import { AlertProvider } from '@/context/AlertContext';

export default function ClientProviders({ children }: { children: ReactNode }) {
  return <AlertProvider>{children}</AlertProvider>;
}
