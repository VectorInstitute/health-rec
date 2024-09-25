'use client';

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import Map, { Marker, Popup, NavigationControl, ViewStateChangeEvent, MapRef } from 'react-map-gl';
import { Box, Text, VStack, Flex, Badge, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, Icon } from '@chakra-ui/react';
import { FaBuilding } from 'react-icons/fa';
import 'mapbox-gl/dist/mapbox-gl.css';
import mapboxgl from 'mapbox-gl';
import { Location } from '../types/service';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_API_KEY;

interface MapProps {
  locations: Location[];
  onMarkerClick?: (location: Location) => void;
  height: string;
  width: string;
  initialViewState?: ViewState;
}

interface ViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  padding?: { top: number; bottom: number; left: number; right: number };
}

export const TORONTO_COORDINATES: ViewState = {
  longitude: -79.3832,
  latitude: 43.6532,
  zoom: 11
};

export const computeViewState = (locations: Location[]): ViewState => {
  if (locations.length === 0) return TORONTO_COORDINATES;
  const bounds = new mapboxgl.LngLatBounds();
  locations.forEach(location => bounds.extend([location.longitude, location.latitude]));
  return {
    ...bounds.getCenter(),
    zoom: 11,
    padding: { top: 40, bottom: 40, left: 40, right: 40 }
  };
};

const MapComponent: React.FC<MapProps> = ({ locations, onMarkerClick, height, width, initialViewState }) => {
  const [viewState, setViewState] = useState<ViewState>(initialViewState || TORONTO_COORDINATES);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [isFullScreenMapOpen, setIsFullScreenMapOpen] = useState(false);
  const mapRef = useRef<MapRef>(null);

  const handleMarkerClick = useCallback((location: Location) => {
    setSelectedLocation(location);
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [location.longitude, location.latitude],
        zoom: 15,
        duration: 1000,
        essential: true
      });
    }
    onMarkerClick && onMarkerClick(location);
  }, [onMarkerClick]);

  useEffect(() => {
    if (locations.length > 0 && mapRef.current) {
      const bounds = new mapboxgl.LngLatBounds();
      locations.forEach(location => bounds.extend([location.longitude, location.latitude]));
      mapRef.current.fitBounds(bounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        maxZoom: 15,
        duration: 1000
      });
    }
  }, [locations]);

  const handleViewStateChange = useCallback((evt: ViewStateChangeEvent) => {
    setViewState(evt.viewState);
  }, []);

  const markers = useMemo(() => locations.map((location) => (
    <Marker
      key={location.id}
      latitude={location.latitude}
      longitude={location.longitude}
      onClick={(e) => {
        e.originalEvent.stopPropagation();
        handleMarkerClick(location);
      }}
    >
      <Box
        width="24px"
        height="24px"
        borderRadius="50%"
        bg="teal.500"
        display="flex"
        alignItems="center"
        justifyContent="center"
        color="white"
        fontWeight="bold"
        fontSize="xs"
        boxShadow="0 0 0 2px white"
        cursor="pointer"
      >
        S
      </Box>
    </Marker>
  )), [locations, handleMarkerClick]);

  const renderLocationsList = () => (
    <VStack align="stretch" spacing={4} overflowY="auto" height="100%">
      {locations.map(location => (
        <Flex key={location.id} p={2} borderWidth={1} borderRadius="md" alignItems="center" cursor="pointer" onClick={() => handleMarkerClick(location)}>
          <Icon as={FaBuilding} boxSize="30px" color="teal.500" mr={3} />
          <VStack align="start" spacing={0}>
            <Text fontWeight="bold" fontSize="sm">{location.name}</Text>
            <Flex alignItems="center">
              {location.rating !== undefined && (
                <Badge colorScheme="teal" mr={1}>{location.rating.toFixed(1)}</Badge>
              )}
              {location.reviewCount !== undefined && (
                <Text fontSize="xs">{location.reviewCount} reviews</Text>
              )}
            </Flex>
          </VStack>
        </Flex>
      ))}
    </VStack>
  );

  if (!MAPBOX_TOKEN) return <Box>Error: Mapbox token is not set</Box>;

  return (
    <>
      <Box height={height} width={width} onClick={() => setIsFullScreenMapOpen(true)} cursor="pointer">
        <Map
          ref={mapRef}
          initialViewState={viewState}
          style={{ width: '100%', height: '100%' }}
          mapStyle="mapbox://styles/mapbox/light-v10"
          mapboxAccessToken={MAPBOX_TOKEN}
          interactive={false}
        >
          {markers}
        </Map>
      </Box>

      <Modal isOpen={isFullScreenMapOpen} onClose={() => setIsFullScreenMapOpen(false)} size="full">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Nearby Services</ModalHeader>
          <ModalCloseButton />
          <ModalBody p={0}>
            <Flex height="calc(100vh - 60px)">
              <Box flex={1}>
                <Map
                  ref={mapRef}
                  initialViewState={viewState}
                  onMove={handleViewStateChange}
                  style={{ width: '100%', height: '100%' }}
                  mapStyle="mapbox://styles/mapbox/light-v10"
                  mapboxAccessToken={MAPBOX_TOKEN}
                  interactive={true}
                >
                  {markers}
                  <NavigationControl position="top-right" />
                  {selectedLocation && (
                    <Popup
                      latitude={selectedLocation.latitude}
                      longitude={selectedLocation.longitude}
                      closeOnClick={false}
                      onClose={() => setSelectedLocation(null)}
                      anchor="bottom"
                    >
                      <Box p={2} maxWidth="200px">
                        <Text fontWeight="bold">{selectedLocation.name}</Text>
                        <Text fontSize="sm">{selectedLocation.address}</Text>
                        <Text fontSize="sm">{selectedLocation.phone}</Text>
                      </Box>
                    </Popup>
                  )}
                </Map>
              </Box>
              <Box width="300px" p={4} overflowY="auto">
                {renderLocationsList()}
              </Box>
            </Flex>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default MapComponent;