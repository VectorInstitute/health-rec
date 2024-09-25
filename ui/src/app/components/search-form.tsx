'use client';

import React, { useState, useEffect, useCallback, memo } from 'react';
import { Box, Container, Input, Button, Text, VStack, InputGroup, InputLeftElement, Flex, useBreakpointValue, Skeleton, useToast } from '@chakra-ui/react'
import { SearchIcon } from '@chakra-ui/icons'
import { useRouter } from 'next/navigation';
import { useRecommendationStore } from '../stores/recommendation-store';

interface FilterButtonsProps {
  distances: string[];
  selectedDistance: string;
  onDistanceChange: (distance: string) => void;
}

const FilterButtons: React.FC<FilterButtonsProps> = memo(({ distances, selectedDistance, onDistanceChange }) => (
  distances.map((distance) => (
    <Button
      key={distance}
      variant={selectedDistance === distance ? "solid" : "outline"}
      size="sm"
      onClick={() => onDistanceChange(distance)}
    >
      {distance}
    </Button>
  ))
));

FilterButtons.displayName = 'FilterButtons';

const SearchForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedDistance, setSelectedDistance] = useState('Any');
  const formPadding = useBreakpointValue({ base: 4, md: 8 });
  const buttonSize = useBreakpointValue({ base: "md", md: "lg" });
  const router = useRouter();
  const toast = useToast();
  const { setRecommendation, setStoreQuery } = useRecommendationStore();

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      toast({
        title: "Empty search",
        description: "Please enter a search query.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSearching(true);
    setRecommendation(null);
    setStoreQuery(query);
    router.push('/recommendation');

    try {
      const response = await fetch(`/api/recommend?query=${encodeURIComponent(query)}&distance=${selectedDistance}`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      if (data && Object.keys(data).length > 0) {
        setRecommendation(data);
      } else {
        throw new Error('No recommendations found');
      }
    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search failed",
        description: "An error occurred while searching. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      router.push('/');
    } finally {
      setIsSearching(false);
    }
  }, [query, selectedDistance, toast, setRecommendation, setStoreQuery, router]);

  const handleClearSearch = useCallback(() => {
    setQuery('');
    setSelectedDistance('Any');
  }, []);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  const handleDistanceChange = useCallback((distance: string) => {
    setSelectedDistance(distance);
  }, []);

  return (
    <Box bg="transparent" py={12} mt={{ base: "-10vh", md: "-20vh" }} position="relative" zIndex={2}>
      <Container maxW="1200px">
        <VStack spacing={8} align="stretch" bg="white" p={formPadding} borderRadius="lg" boxShadow="xl">
          <Flex gap={6} direction={{ base: 'column', md: 'row' }}>
            <Box flex={1}>
              <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
                <Text fontWeight="semibold" mb={2}>What you&apos;re looking for?</Text>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <SearchIcon color="gray.300" />
                  </InputLeftElement>
                  <Input
                    placeholder="Search service, condition, etc."
                    aria-label="Search box"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                </InputGroup>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  Tell us a little about yourself and what you&apos;re looking for? The more you share, the better we can tailor our recommendations to suit your needs.
                </Text>
              </Skeleton>
            </Box>
            <Box flex={1}>
              <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
                <Text fontWeight="semibold" mb={2}>Where are you located?</Text>
                <Input placeholder="Enter location" aria-label="Location box" disabled />
                <Text fontSize="sm" color="gray.500" mt={2}>
                  You can use a city, postal code, street address or intersection.
                </Text>
              </Skeleton>
            </Box>
          </Flex>
          <Flex justify="space-between" direction={{ base: 'column', md: 'row' }} gap={4}>
            <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
              <Button variant="link" colorScheme="gray" onClick={handleClearSearch}>Clear search</Button>
            </Skeleton>
            <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
              <Flex align="center" gap={2} wrap="wrap">
                <Text fontWeight="semibold">Filter results to within:</Text>
                <FilterButtons
                  distances={['Any', '3km', '5km', '10km', '20km']}
                  selectedDistance={selectedDistance}
                  onDistanceChange={handleDistanceChange}
                />
              </Flex>
            </Skeleton>
          </Flex>
          <Box textAlign="right">
            <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
              <Button
                colorScheme="pink"
                size={buttonSize}
                aria-label="Search"
                onClick={handleSearch}
                isLoading={isSearching}
              >
                Search
              </Button>
            </Skeleton>
          </Box>
        </VStack>
        <Text fontSize="xs" color="gray.500" mt={4}>
          Disclaimer: The information provided by our smart search tool is for general informational purposes only and is not a substitute for professional medical advice. The Vector Institute is not liable for any actions taken based on the search results. Always consult a healthcare provider for personalized advice.
        </Text>
      </Container>
    </Box>
  )
}

export default memo(SearchForm);
