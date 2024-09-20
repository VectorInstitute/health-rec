'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Box, Container, Heading, Text, VStack, Alert, AlertIcon, useBreakpointValue, Divider, CloseButton, Button, Skeleton } from '@chakra-ui/react';
import { WebMercatorViewport } from '@deck.gl/core';
import 'mapbox-gl/dist/mapbox-gl.css';

const MapGL = dynamic(() => import('react-map-gl'), { ssr: false });
const Marker = dynamic(() => import('react-map-gl').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-map-gl').then(mod => mod.Popup), { ssr: false });

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_API_KEY;

interface Service {
  id: string;
  public_name: string;
  latitude: number | null;
  longitude: number | null;
  description?: string;
  service_area?: string[];
}

interface ValidService extends Omit<Service, 'latitude' | 'longitude'> {
  latitude: number;
  longitude: number;
}

interface ViewState {
  longitude: number;
  latitude: number;
  zoom: number;
}

const DevPage: React.FC = () => {
  const [services, setServices] = useState<ValidService[]>([]);
  const [count, setCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedService, setSelectedService] = useState<ValidService | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewState, setViewState] = useState<ViewState>({ longitude: -79.4, latitude: 43.65, zoom: 10 });
  const [initialViewState, setInitialViewState] = useState<ViewState>({ longitude: -79.4, latitude: 43.65, zoom: 10 });

  const mapHeight = useBreakpointValue({ base: '400px', md: '600px' });
  const mapWidth = useBreakpointValue({ base: '100%', md: '100%', lg: '100%' });

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
        const countData = await countResponse.json();

        const validServices: ValidService[] = servicesData.filter(
          (service): service is ValidService =>
            typeof service.latitude === 'number' &&
            typeof service.longitude === 'number' &&
            !isNaN(service.latitude) &&
            !isNaN(service.longitude) &&
            !(service.latitude === 0 && service.longitude === 0)
        );

        setServices(validServices);
        setCount(countData);

        if (validServices.length > 0) {
          const bounds = validServices.reduce<[number, number, number, number]>(
            (acc, service) => [
              Math.min(acc[0], service.longitude),
              Math.min(acc[1], service.latitude),
              Math.max(acc[2], service.longitude),
              Math.max(acc[3], service.latitude),
            ],
            [Infinity, Infinity, -Infinity, -Infinity]
          );

          const viewport = new WebMercatorViewport({ width: 800, height: 600 })
            .fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], { padding: 40 });

          const newViewState: ViewState = {
            longitude: viewport.longitude,
            latitude: viewport.latitude,
            zoom: viewport.zoom,
          };

          setViewState(newViewState);
          setInitialViewState(newViewState);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const markers = useMemo(() => services.map((service) => (
    <Marker
      key={service.id}
      latitude={service.latitude}
      longitude={service.longitude}
      onClick={(e) => {
        e.originalEvent.stopPropagation();
        setSelectedService(service);
      }}
    >
      <div style={{
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        backgroundColor: '#3182CE',
        border: '2px solid #FFFFFF',
        boxShadow: '0 0 0 2px #3182CE',
        transition: 'transform 0.2s'
      }} />
    </Marker>
  )), [services]);

  const resetViewport = useCallback(() => {
    setViewState(initialViewState);
  }, [initialViewState]);

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
        <Button onClick={resetViewport} colorScheme="blue" isDisabled={loading}>Reset Map View</Button>
        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}
        <Box height={mapHeight} width={mapWidth}>
          <Skeleton isLoaded={!loading} height="100%">
            <MapGL
              {...viewState}
              onMove={evt => setViewState(evt.viewState)}
              style={{ width: '100%', height: '100%' }}
              mapStyle="mapbox://styles/mapbox/dark-v11"
              mapboxAccessToken={MAPBOX_TOKEN}
              onClick={() => setSelectedService(null)}
            >
              {markers}
              {selectedService && (
                <Popup
                  latitude={selectedService.latitude}
                  longitude={selectedService.longitude}
                  closeOnClick={false}
                  anchor="bottom"
                  offset={[0, -10]}
                  onClose={() => setSelectedService(null)}
                >
                  <Box p={3} bg="white" borderRadius="md" boxShadow="md" maxWidth="300px">
                    <CloseButton
                      size="sm"
                      position="absolute"
                      right={2}
                      top={2}
                      onClick={() => setSelectedService(null)}
                    />
                    <Heading as="h3" size="sm" mb={2}>{selectedService.public_name}</Heading>
                    <Divider my={2} />
                    <Text fontSize="sm" color="gray.600">
                      <strong>Coordinates:</strong> {selectedService.latitude.toFixed(4)}, {selectedService.longitude.toFixed(4)}
                    </Text>
                    {selectedService.service_area && (
                      <Text fontSize="sm" color="gray.600" mt={2}>
                        <strong>Service Area:</strong> {selectedService.service_area.join(', ')}
                      </Text>
                    )}
                  </Box>
                </Popup>
              )}
            </MapGL>
          </Skeleton>
        </Box>
      </VStack>
    </Container>
  );
};

export default DevPage;