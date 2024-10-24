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
  radius?: number;
  center?: [number, number];
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
  if (!locations.length) {
    return TORONTO_COORDINATES;
  }

  const min_longitude = Math.min(...locations.map(loc => loc.longitude));
  const max_longitude = Math.max(...locations.map(loc => loc.longitude));
  const min_latitude = Math.min(...locations.map(loc => loc.latitude));
  const max_latitude = Math.max(...locations.map(loc => loc.latitude));

  const center_longitude = (min_longitude + max_longitude) / 2;
  const center_latitude = (min_latitude + max_latitude) / 2;

  const padding = { top: 40, bottom: 40, left: 40, right: 40 };

  return {
    longitude: center_longitude,
    latitude: center_latitude,
    zoom: 11,
    padding
  };
};

const MapComponent: React.FC<MapProps> = ({ locations, onMarkerClick, height, width, initialViewState, radius, center }) => {
  const [viewState, setViewState] = useState<ViewState>(computeViewState(locations));
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [isFullScreenMapOpen, setIsFullScreenMapOpen] = useState(false);
  const mapRef = useRef<MapRef>(null);

  useEffect(() => {
    setViewState(computeViewState(locations));
  }, [locations]);

  const handleMarkerClick = useCallback((location: Location) => {
    setSelectedLocation(location);
    if (mapRef.current && isFullScreenMapOpen) {
      mapRef.current.flyTo({
        center: [location.longitude, location.latitude],
        zoom: 15,
        duration: 1000
      });
    }
    onMarkerClick && onMarkerClick(location);
  }, [onMarkerClick, isFullScreenMapOpen]);

  const handleViewStateChange = useCallback((evt: ViewStateChangeEvent) => {
    if (isFullScreenMapOpen) {
      setViewState(evt.viewState);
    }
  }, [isFullScreenMapOpen]);

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

  const radiusLayer = useMemo(() => {
    if (!radius || !center) return null;

    return (
      <Source
        id="radius-source"
        type="geojson"
        data={{
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: center
          },
          properties: {
            radius: radius
          }
        }}
      >
        <Layer
          id="radius-layer"
          type="circle"
          paint={{
            'circle-radius': ['*', ['get', 'radius'], radius],
            'circle-color': 'rgba(255, 192, 203, 0.2)',
            'circle-stroke-width': 2,
            'circle-stroke-color': 'rgba(255, 192, 203, 0.8)'
          }}
        />
      </Source>
    );
  }, [radius, center]);

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
  }, []);

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
          {markers}
          {radiusLayer}
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
