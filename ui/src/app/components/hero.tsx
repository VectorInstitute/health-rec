'use client';

import React, { useState, useEffect, memo } from 'react';
import { Box, Container, Heading, Text, VStack, useBreakpointValue, Skeleton } from '@chakra-ui/react'

const Hero: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true)
  const headingSize = useBreakpointValue({ base: "2xl", md: "3xl", lg: "4xl" });
  const textSize = useBreakpointValue({ base: "md", md: "lg", lg: "xl" });

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Box
      bgGradient="linear(to-r, brand.pink, brand.purple)"
      position="relative"
      overflow="hidden"
      minHeight={{ base: "70vh", md: "80vh" }}
      pt={{ base: "80px", md: "100px" }}
    >
      <Container maxW="1200px" h="full" position="relative" zIndex={1}>
        <VStack
          spacing={6}
          alignItems={{ base: "center", md: "flex-start" }}
          justifyContent="center"
          h="full"
          maxW={{ base: "100%", md: "60%", lg: "50%" }}
          textAlign={{ base: "center", md: "left" }}
        >
          <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
            <Heading as="h1" size={headingSize} color="white" fontWeight="bold">
              Discover your community services!
            </Heading>
          </Skeleton>
          <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
            <Text fontSize={textSize} color="white">
              Try our smart search tool to easily find health and community services for you and your family.
            </Text>
          </Skeleton>
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
        transition="all 0.3s ease-in-out"
      />
    </Box>
  )
}

export default memo(Hero);
