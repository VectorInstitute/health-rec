'use client';

import { ChakraProvider, extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      pink: '#eb088a',
      purple: '#8a08eb',
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return <ChakraProvider theme={theme}>{children}</ChakraProvider>;
}