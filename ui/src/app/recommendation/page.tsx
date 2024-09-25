'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Container, Heading, Text, VStack, SimpleGrid, useColorModeValue,
  Alert, AlertIcon, AlertTitle, AlertDescription, Divider, Badge, Flex,
  Grid, GridItem, Skeleton, SkeletonText, SkeletonCircle
} from '@chakra-ui/react';
import ServiceCard from '../components/service-card';
import Header from '../components/header';
import Map, { computeViewState, TORONTO_COORDINATES } from '../components/map';
import { Service, Location } from '../types/service';
import { useRecommendationStore, Recommendation } from '../stores/recommendation-store';
import { useRouter } from 'next/navigation'

const RecommendationPage: React.FC = () => {
  const recommendation = useRecommendationStore((state) => state.recommendation);
  const router = useRouter();
  const [mapViewState, setMapViewState] = useState(TORONTO_COORDINATES);
  const [isLoading, setIsLoading] = useState(true);

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const textColor = useColorModeValue('gray.800', 'white');
  const cardBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const mapHeight = '400px';
  const mapWidth = '100%';

  useEffect(() => {
    let isActive = true;

    if (recommendation === undefined) {
      router.replace('/');
    } else {
      // Simulate loading delay
      setTimeout(() => {
        if (isActive) {
          setIsLoading(false);
        }
      }, 1500);
    }

    return () => {
      isActive = false;
    };
  }, [recommendation, router]);

  const mapLocations: Location[] = useMemo(() => recommendation?.services
    .filter((service): service is Service & Required<Pick<Service, 'Latitude' | 'Longitude'>> =>
      typeof service.Latitude === 'number' &&
      typeof service.Longitude === 'number' &&
      !isNaN(service.Latitude) &&
      !isNaN(service.Longitude)
    )
    .map(service => ({
      id: service.id,
      name: service.PublicName,
      latitude: service.Latitude,
      longitude: service.Longitude,
      description: service.Description || '',
      address: service.Address || '',
      phone: service.Phone || '',
    })) || [], [recommendation]);

  useEffect(() => {
    if (mapLocations.length > 0) {
      const newViewState = computeViewState(mapLocations);
      setMapViewState(newViewState);
    }
  }, [mapLocations]);

  const renderEmergencyAlert = (message: string) => (
    <Alert
      status="error"
      variant="subtle"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      height="200px"
      borderRadius="md"
    >
      <AlertIcon boxSize="40px" mr={0} />
      <AlertTitle mt={4} mb={1} fontSize="lg">
        Emergency Situation Detected
      </AlertTitle>
      <AlertDescription maxWidth="sm">{message}</AlertDescription>
    </Alert>
  );

  const renderRecommendationCard = (recommendation: Recommendation | null) => {
    if (isLoading) {
      return (
        <Box bg={cardBgColor} p={8} borderRadius="lg" boxShadow="xl" borderWidth={1} borderColor={borderColor} height="100%">
          <VStack spacing={6} align="stretch">
            <Skeleton height="20px" width="40%" />
            <SkeletonText mt="4" noOfLines={4} spacing="4" skeletonHeight="2" />
            <Divider />
            <Skeleton height="20px" width="30%" />
            <SkeletonText mt="4" noOfLines={6} spacing="4" skeletonHeight="2" />
          </VStack>
        </Box>
      );
    }

    if (!recommendation) return null;

    const [overviewWithLabel, ...reasoningParts] = recommendation.message.split('\n').filter(part => part.trim() !== '');
    const overview = overviewWithLabel.replace('Overview:', '').trim();
    const reasoning = reasoningParts.join('\n').replace('Reasoning:', '').trim();

    return (
      <Box bg={cardBgColor} p={8} borderRadius="lg" boxShadow="xl" borderWidth={1} borderColor={borderColor} height="100%">
        <VStack spacing={6} align="stretch">
          <Box>
            <Badge colorScheme="blue" fontSize="sm" mb={2}>
              Overview
            </Badge>
            <Text fontSize="lg">{overview}</Text>
          </Box>
          <Divider />
          <Box>
            <Badge colorScheme="green" fontSize="sm" mb={2}>
              Reasoning
            </Badge>
            <Text fontSize="md">{reasoning}</Text>
          </Box>
        </VStack>
      </Box>
    );
  };

  const renderRecommendedServices = (services: Service[] | null) => (
    <>
      <Heading as="h2" size="xl" color={textColor} mt={12} mb={6}>
        Recommended Services
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
        {isLoading ? (
          Array.from({ length: 6 }).map((_, index) => (
            <Box key={index} bg={cardBgColor} p={6} borderRadius="lg" boxShadow="md" borderWidth={1} borderColor={borderColor}>
              <VStack align="stretch" spacing={4}>
                <Skeleton height="20px" width="60%" />
                <SkeletonText mt="2" noOfLines={3} spacing="2" skeletonHeight="2" />
                <Skeleton height="20px" width="40%" />
                <Flex>
                  <SkeletonCircle size="8" mr={2} />
                  <Skeleton height="20px" width="30%" />
                </Flex>
              </VStack>
            </Box>
          ))
        ) : (
          services?.map((service) => (
            <ServiceCard key={service.id} service={service} />
          ))
        )}
      </SimpleGrid>
    </>
  );

  return (
    <Box minHeight="100vh" bg={bgColor}>
      <Header />
      <Container maxW="1400px" py={20}>
        <VStack spacing={8} align="stretch">
          <Flex justifyContent="space-between" alignItems="center">
            <Heading as="h1" size="2xl" color={textColor}>
              Your Recommendation
            </Heading>
            <Badge colorScheme="blue" fontSize="md" p={2} borderRadius="md">
              Personalized Result
            </Badge>
          </Flex>
          {recommendation?.is_emergency ? (
            renderEmergencyAlert(recommendation.message)
          ) : (
            <>
              <Grid templateColumns={{ base: "1fr", lg: "3fr 2fr" }} gap={8}>
                <GridItem>
                  {renderRecommendationCard(recommendation)}
                </GridItem>
                <GridItem>
                  <Box height="100%">
                    <Heading as="h3" size="md" color={textColor} mb={4}>
                      Service Locations
                    </Heading>
                    <Box height="calc(100% - 2rem)">
                      {isLoading ? (
                        <Skeleton height="100%" borderRadius="lg" />
                      ) : (
                        <Map
                          locations={mapLocations}
                          height={mapHeight}
                          width={mapWidth}
                          initialViewState={mapViewState}
                        />
                      )}
                    </Box>
                  </Box>
                </GridItem>
              </Grid>
              {renderRecommendedServices(recommendation?.services || null)}
            </>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default RecommendationPage;
