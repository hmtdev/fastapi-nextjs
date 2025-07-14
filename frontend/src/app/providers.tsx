'use client'
import { useState } from "react";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'sonner'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
      defaultOptions: {
          queries: {
              refetchOnWindowFocus: false,
              retry: 1,
              staleTime: 1000 * 60 * 5, // 5 minutes
          },
      },
  }));
  return (
   <QueryClientProvider client={queryClient}>
      {children}
    <ReactQueryDevtools initialIsOpen={false} />
    <Toaster position="top-right" />
  </QueryClientProvider>
)
}