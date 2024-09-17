'use client';

import React, { memo } from 'react';
import { Box, Container, Flex, Heading, Text, Image, VStack, Link } from '@chakra-ui/react';
import NextLink from 'next/link';
import Header from '../components/header';

const About: React.FC = () => {
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
          <VStack spacing={8} alignItems="center" color="white" textAlign="center">
            <Heading as="h1" size="2xl">About Our Tool</Heading>
            <Text fontSize="xl" maxW="800px">
              This smart search tool is designed by the Vector Institute using data from Ontario 211 
              to help you easily find health and community services for you and your family.
            </Text>
            <Flex gap={8} alignItems="center" flexWrap="wrap" justifyContent="center">
              <Link as={NextLink} href="https://vectorinstitute.ai" isExternal>
                <Image 
                  src="/images/vector-logo.png" 
                  alt="Vector Institute" 
                  width={150} 
                  height={40} 
                  objectFit="contain"
                />
              </Link>
              <Link as={NextLink} href="https://211ontario.ca" isExternal>
                <Image 
                  src="/images/211-logo.png" 
                  alt="Ontario 211" 
                  width={150} 
                  height={40} 
                  objectFit="contain"
                />
              </Link>
            </Flex>
          </VStack>
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

export default memo(About);