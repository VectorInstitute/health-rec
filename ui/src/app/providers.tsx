'use client';

import { ChakraProvider, extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      pink: '#eb088a',
      purple: '#8a08eb',
    },
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      },
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return <ChakraProvider theme={theme}>{children}</ChakraProvider>;
}
