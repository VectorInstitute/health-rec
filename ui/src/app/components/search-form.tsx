'use client';

/// <reference types="@types/google.maps" />

import React, { useState, useEffect, useCallback, memo, useRef, useMemo } from 'react';
import { Box, Container, Input, Button, Text, VStack, InputGroup, InputRightElement, Flex, useBreakpointValue, Skeleton, useToast } from '@chakra-ui/react'
import { SearchIcon } from '@chakra-ui/icons'
import { MdMyLocation } from 'react-icons/md'
import { useRouter } from 'next/navigation';
import { useRecommendationStore, RecommendationStore, Query } from '../stores/recommendation-store';
import { Loader } from "@googlemaps/js-api-loader"
import debounce from 'lodash/debounce';

interface FilterButtonsProps {
  distances: string[];
  selectedDistance: string;
  onDistanceChange: (distance: string) => void;
}

const FilterButtons: React.FC<FilterButtonsProps> = memo(({ distances, selectedDistance, onDistanceChange }) => (
  <>
    {distances.map((distance) => (
      <Button
        key={distance}
        variant={selectedDistance === distance ? "solid" : "outline"}
        size="sm"
        onClick={() => onDistanceChange(distance)}
      >
        {distance}
      </Button>
    ))}
  </>
));

FilterButtons.displayName = 'FilterButtons';

const SearchForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedDistance, setSelectedDistance] = useState('Any');
  const [isGeolocating, setIsGeolocating] = useState(false);
  const formPadding = useBreakpointValue({ base: 4, md: 8 });
  const buttonSize = useBreakpointValue({ base: "md", md: "lg" });
  const router = useRouter();
  const toast = useToast();
  const { setRecommendation, setStoreQuery } = useRecommendationStore() as RecommendationStore;
  const [geocoder, setGeocoder] = useState<google.maps.Geocoder | null>(null);
  const [autocompleteService, setAutocompleteService] = useState<google.maps.places.AutocompleteService | null>(null);
  const [placesService, setPlacesService] = useState<google.maps.places.PlacesService | null>(null);
  const [predictions, setPredictions] = useState<google.maps.places.AutocompletePrediction[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const loader = new Loader({
      apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
      version: "weekly",
      libraries: ["places", "geocoding"]
    });

    loader.importLibrary('places').then(() => {
      setGeocoder(new google.maps.Geocoder());
      setAutocompleteService(new google.maps.places.AutocompleteService());
      setPlacesService(new google.maps.places.PlacesService(document.createElement('div')));
    }).catch((error: Error) => {
      console.error('Error loading Google Maps API:', error);
      toast({
        title: "API Error",
        description: "Failed to load Google Maps API. Please try again later.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    });
  }, [toast]);

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

    if (selectedDistance !== 'Any' && !location) {
      toast({
        title: "Location missing",
        description: "Please enter a location or use your current location when a specific radius is selected.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSearching(true);
    setRecommendation(null);

    const queryObject: Query = {
      query,
      latitude,
      longitude,
      radius: selectedDistance === 'Any' ? null : parseFloat(selectedDistance.replace('km', ''))
    };

    setStoreQuery(queryObject);

    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryObject),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      if (data && Object.keys(data).length > 0) {
        setRecommendation(data);
        router.push('/recommendation');
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
    } finally {
      setIsSearching(false);
    }
  }, [query, latitude, longitude, selectedDistance, location, toast, setRecommendation, setStoreQuery, router]);

  const handleClearSearch = useCallback(() => {
    setQuery('');
    setLocation('');
    setLatitude(null);
    setLongitude(null);
    setSelectedDistance('Any');
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }, []);


  const handleDistanceChange = useCallback((distance: string) => {
    setSelectedDistance(distance);
  }, []);

  const debouncedHandleLocationChangeRef = useRef<(value: string) => void>(() => {});

  useEffect(() => {
    debouncedHandleLocationChangeRef.current = debounce((value: string) => {
      if (autocompleteService && value) {
        autocompleteService.getPlacePredictions({ input: value }, (predictions, status) => {
          if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
            setPredictions(predictions);
          } else {
            setPredictions([]);
          }
        });
      } else {
        setPredictions([]);
      }
    }, 300),
    [autocompleteService]
  );

  const handleLocationChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocation(value);
    debouncedHandleLocationChange(value);
  }, [debouncedHandleLocationChange]);

  const handlePredictionSelect = useCallback((prediction: google.maps.places.AutocompletePrediction) => {
    if (placesService) {
      placesService.getDetails({ placeId: prediction.place_id }, (place, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && place && place.geometry && place.geometry.location) {
          setLocation(prediction.description);
          setLatitude(place.geometry.location.lat());
          setLongitude(place.geometry.location.lng());
          setPredictions([]);
        }
      });
    }
  }, [placesService]);

  const handleGetCurrentLocation = useCallback(() => {
    if ("geolocation" in navigator) {
      setIsGeolocating(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude);
          setLongitude(position.coords.longitude);
          if (geocoder) {
            geocoder.geocode({ location: { lat: position.coords.latitude, lng: position.coords.longitude } }, (results, status) => {
              if (status === 'OK' && results && results[0]) {
                setLocation(results[0].formatted_address);
                if (inputRef.current) {
                  inputRef.current.value = results[0].formatted_address;
                }
              } else {
                toast({
                  title: "Geocoding Error",
                  description: "Unable to retrieve address for your location.",
                  status: "error",
                  duration: 3000,
                  isClosable: true,
                });
              }
              setIsGeolocating(false);
            });
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
          toast({
            title: "Location Error",
            description: "Unable to retrieve your location. Please check your browser settings.",
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          setIsGeolocating(false);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      toast({
        title: "Geolocation Unavailable",
        description: "Your browser doesn't support geolocation.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  }, [geocoder, toast]);

  return (
    <Box bg="transparent" py={12} mt={{ base: "-10vh", md: "-20vh" }} position="relative" zIndex={2}>
      <Container maxW="1200px">
        <VStack spacing={8} align="stretch" bg="white" p={formPadding} borderRadius="lg" boxShadow="xl">
          <Flex gap={6} direction={{ base: 'column', md: 'row' }}>
            <Box flex={1}>
              <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
                <Text fontWeight="semibold" mb={2}>What are you looking for?</Text>
                <InputGroup>
                  <InputRightElement pointerEvents="none">
                    <SearchIcon color="gray.300" />
                  </InputRightElement>
                  <Input
                    placeholder="Search service, condition, etc."
                    aria-label="Search box"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </InputGroup>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  Tell us a little about yourself and what you&apos;re looking for! The more you share, the better we can tailor our recommendations to suit your needs.
                </Text>
              </Skeleton>
            </Box>
            <Box flex={1} position="relative">
              <Skeleton isLoaded={!isLoading} fadeDuration={0.5}>
                <Text fontWeight="semibold" mb={2}>Where are you located?</Text>
                <InputGroup>
                  <Input
                    ref={inputRef}
                    placeholder="Enter location"
                    aria-label="Location box"
                    value={location}
                    onChange={handleLocationChange}
                    disabled={isGeolocating}
                  />
                  <InputRightElement width="4.5rem">
                    <Button h="1.75rem" size="sm" onClick={handleGetCurrentLocation} bg="transparent" _hover={{ bg: "gray.100" }} isLoading={isGeolocating}>
                      <MdMyLocation />
                    </Button>
                  </InputRightElement>
                </InputGroup>
                {predictions.length > 0 && (
                  <Box position="absolute" top="100%" left={0} right={0} zIndex={10} bg="white" boxShadow="md" borderRadius="md" mt={2}>
                    {predictions.map((prediction) => (
                      <Box
                        key={prediction.place_id}
                        p={2}
                        cursor="pointer"
                        _hover={{ bg: "gray.100" }}
                        onClick={() => handlePredictionSelect(prediction)}
                      >
                        {prediction.description}
                      </Box>
                    ))}
                  </Box>
                )}
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
                  distances={['Any', '2 km', '5 km', '10 km', '50 km']}
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
