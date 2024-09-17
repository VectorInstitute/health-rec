'use client';

import React from 'react';
import { Box, Container } from '@chakra-ui/react';
import Header from '../components/header';

const DiscoverPage: React.FC = () => {
  return (
    <Box minHeight="100vh">
      <Header />
      <Box 
        bgGradient="linear(to-r, brand.pink, brand.purple)"
        position="relative"
        overflow="hidden"
        minHeight="calc(100vh - 80px)"
        pt={{ base: "80px", md: "100px" }}
      >
        <Container maxW="1200px" position="relative" zIndex={1}>
          {/* Content will go here in the future */}
        </Container>
        <Box 
          position="absolute" 
          top={{ base: "60%", md: "40%" }}
          right={{ base: "-20%", md: "-5%" }}
          width={{ base: "120%", md: "70%" }} 
          height={{ base: "100%", md: "140%" }} 
          bg="white" 
          borderTopLeftRadius={{ base: "30%", md: "50%" }}
          transform={{ base: "rotate(-5deg)", md: "rotate(-10deg)" }}
          boxShadow="0 -4px 30px rgba(0, 0, 0, 0.1)"
        />
      </Box>
    </Box>
  );
}

export default DiscoverPage;