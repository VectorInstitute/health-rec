'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  Alert,
  AlertIcon,
  useBreakpointValue,
  Button,
  Skeleton
} from '@chakra-ui/react';
import { Service, Address, Location } from '../types/service';
import Map, { computeViewState, TORONTO_COORDINATES } from '../components/map';

const DevPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [count, setCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [mapViewState, setMapViewState] = useState(TORONTO_COORDINATES);
  const [selectedService, setSelectedService] = useState<Service | null>(null);

  const mapHeight = useBreakpointValue({ base: '400px', md: '600px' }) ?? '400px';
  const mapWidth = useBreakpointValue({ base: '100%', md: '100%', lg: '100%' }) ?? '100%';

  const formatAddress = (address: Address): string => {
    const parts = [
      address.street1,
      address.street2,
      address.city,
      address.province,
      address.postal_code,
      address.country,
    ].filter(Boolean);
    return parts.join(', ');
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [servicesResponse, countResponse] = await Promise.all([
          fetch('/api/services/all'),
          fetch('/api/services/count')
        ]);

        if (!servicesResponse.ok || !countResponse.ok) {
          throw new Error('Failed to fetch data');
        }

        const servicesData: Service[] = await servicesResponse.json();
        const countData: number = await countResponse.json();

        const validServices = servicesData.filter(
          (service): service is Service & Required<Pick<Service, 'latitude' | 'longitude'>> =>
            typeof service.latitude === 'number' &&
            typeof service.longitude === 'number' &&
            !isNaN(service.latitude) &&
            !isNaN(service.longitude) &&
            !(service.latitude === 0 && service.longitude === 0)
        );

        setServices(validServices);
        setCount(countData);

        if (validServices.length > 0) {
          const locations = validServices.map(service => ({
            id: service.id,
            name: service.name,
            latitude: service.latitude,
            longitude: service.longitude,
            description: service.description,
            address: formatAddress(service.address),
          }));
          const newViewState = computeViewState(locations);
          setMapViewState(newViewState);
        } else {
          setMapViewState(TORONTO_COORDINATES);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data. Please try again later.');
        setMapViewState(TORONTO_COORDINATES);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const resetViewport = useCallback(() => {
    setMapViewState(TORONTO_COORDINATES);
    setSelectedService(null);
  }, []);

  const handleLocationClick = useCallback((location: Location) => {
    const service = services.find(s => s.id === location.id);
    setSelectedService(service || null);
  }, [services]);

  const locations = services.map(service => ({
    id: service.id,
    name: service.name,
    latitude: service.latitude,
    longitude: service.longitude,
    address: formatAddress(service.address),
    description: service.description,
    phone: service.phone_numbers?.[0]?.number || '',
  }));


  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading as="h1" size="2xl">
          Service Development Dashboard
        </Heading>
        <Skeleton isLoaded={!loading}>
          <Text fontSize="xl">Total number of services: {count}</Text>
        </Skeleton>
        <Skeleton isLoaded={!loading}>
          <Text fontSize="md">Services with valid coordinates: {services.length}</Text>
        </Skeleton>
        <Button onClick={resetViewport} colorScheme="blue" isDisabled={loading}>
          Reset Map View
        </Button>
        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}
        <Box height={mapHeight} width={mapWidth}>
          <Skeleton isLoaded={!loading} height="100%">
            <Map
              locations={locations}
              height={mapHeight}
              width={mapWidth}
              initialViewState={mapViewState}
              onMarkerClick={handleMarkerClick}
            />
          </Skeleton>
        </Box>
        {selectedService && (
          <Box p={4} borderWidth={1} borderRadius="md" bg="white">
            <VStack align="start" spacing={2}>
              <Heading size="md">{selectedService.name}</Heading>
              <Text><strong>Address:</strong> {formatAddress(selectedService.address)}</Text>
              {selectedService.phone_numbers?.[0]?.number && (
                <Text><strong>Phone:</strong> {selectedService.phone_numbers[0].number}</Text>
              )}
              {selectedService.description && (
                <Text><strong>Description:</strong> {selectedService.description}</Text>
              )}
            </VStack>
          </Box>
        )}
      </VStack>
    </Container>
  );
};

export default DevPage;
