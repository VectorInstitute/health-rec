'use client';

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import Map, {
  Marker,
  Popup,
  NavigationControl,
  ViewStateChangeEvent,
  MapRef,
  Source,
  Layer
} from 'react-map-gl';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Box, Text, VStack, Flex, Badge, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, Icon } from '@chakra-ui/react';
import { FaBuilding } from 'react-icons/fa';
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

  // Calculate the center and appropriate zoom level
  const center = bounds.getCenter();

  // Calculate the appropriate zoom level based on bounds
  const maxZoom = 15;
  const padding = { top: 50, bottom: 50, left: 50, right: 50 };

  return {
    longitude: center.lng,
    latitude: center.lat,
    zoom: getBoundsZoomLevel(bounds, { width: 400, height: 400 }, padding, maxZoom),
    padding
  };
};

function getBoundsZoomLevel(bounds: mapboxgl.LngLatBounds, mapDimensions: { width: number, height: number }, padding: { top: number; bottom: number; left: number; right: number }, maxZoom: number) {
  const WORLD_DIM = { height: 256, width: 256 };
  const ZOOM_MAX = maxZoom;

  function latRad(lat: number) {
    const sin = Math.sin((lat * Math.PI) / 180);
    const radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
    return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
  }

  function zoom(mapPx: number, worldPx: number, fraction: number) {
    return Math.log2(mapPx / worldPx / fraction);
  }

  const ne = bounds.getNorthEast();
  const sw = bounds.getSouthWest();

  const latFraction = (latRad(ne.lat) - latRad(sw.lat)) / Math.PI;

  const lngDiff = ne.lng - sw.lng;
  const lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

  const latZoom = zoom(
    mapDimensions.height - padding.top - padding.bottom,
    WORLD_DIM.height,
    latFraction
  );
  const lngZoom = zoom(
    mapDimensions.width - padding.left - padding.right,
    WORLD_DIM.width,
    lngFraction
  );

  return Math.min(Math.min(latZoom, lngZoom), ZOOM_MAX);
}

const MapComponent: React.FC<MapProps> = ({ locations, onMarkerClick, height, width }) => {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState<ViewState>(() =>
    computeViewState(locations)
  );
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [isFullScreenMapOpen, setIsFullScreenMapOpen] = useState(false);

  const handleMarkerClick = useCallback((location: Location) => {
    setSelectedLocation(location);
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [location.longitude, location.latitude],
        zoom: 15,
        duration: 1000
      });
    }
    onMarkerClick && onMarkerClick(location);
  }, [onMarkerClick]);

  const fitMapToLocations = useCallback(() => {
    if (locations.length > 0 && mapRef.current) {
      const bounds = new mapboxgl.LngLatBounds();
      locations.forEach(location => bounds.extend([location.longitude, location.latitude]));

      mapRef.current.fitBounds(bounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        maxZoom: 15,
        duration: 0
      });
    }
  }, [locations]);

  useEffect(() => {
    const newViewState = computeViewState(locations);
    setViewState(newViewState);
    fitMapToLocations();
  }, [locations, fitMapToLocations]);

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
        bg="brand.pink"
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

  const renderLocationsList = useCallback(() => (
    <VStack align="stretch" spacing={4} overflowY="auto" height="100%">
      {locations.map(location => (
        <Flex key={location.id} p={2} borderWidth={1} borderRadius="md" alignItems="center" cursor="pointer" onClick={() => handleMarkerClick(location)}>
          <Icon as={FaBuilding} boxSize="30px" color="brand.pink" mr={3} />
          <VStack align="start" spacing={0}>
            <Text fontWeight="bold" fontSize="sm">{location.name}</Text>
            <Flex alignItems="center">
              {location.rating !== undefined && (
                <Badge colorScheme="brand.pink" mr={1}>{location.rating.toFixed(1)}</Badge>
              )}
              {location.reviewCount !== undefined && (
                <Text fontSize="xs">{location.reviewCount} reviews</Text>
              )}
            </Flex>
          </VStack>
        </Flex>
      ))}
    </VStack>
  ), [locations, handleMarkerClick]);

  const handleFullScreenMapOpen = useCallback(() => {
    setIsFullScreenMapOpen(true);
    // Delay the fitMapToLocations call to ensure the map is fully rendered
    setTimeout(() => {
      fitMapToLocations();
    }, 100);
  }, [fitMapToLocations]);

  if (!MAPBOX_TOKEN) return <Box>Error: Mapbox token is not set</Box>;

  return (
    <>
      <Box height={height} width={width} onClick={handleFullScreenMapOpen} cursor="pointer">
        <Map
          ref={mapRef}
          initialViewState={viewState}
          style={{ width: '100%', height: '100%' }}
          mapStyle="mapbox://styles/mapbox/light-v10"
          mapboxAccessToken={MAPBOX_TOKEN}
          interactive={false}
          reuseMaps
        >
          <Source id="locations" type="geojson" data={{
            type: 'FeatureCollection',
            features: locations.map(location => ({
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [location.longitude, location.latitude]
              },
              properties: {
                id: location.id,
                name: location.name
              }
            }))
          }}>
            <Layer
              id="locations-layer"
              type="circle"
              paint={{
                'circle-radius': 8,
                'circle-color': '#eb088a',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
              }}
            />
          </Source>
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
                  reuseMaps
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
