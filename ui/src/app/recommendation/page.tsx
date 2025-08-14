'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  useColorModeValue,
  Divider,
  Badge,
  Flex,
  Grid,
  GridItem,
  Skeleton,
  SkeletonText,
  SkeletonCircle,
} from '@chakra-ui/react';
import ServiceCard from '../components/service-card';
import Header from '../components/header';
import Map, { computeViewState, TORONTO_COORDINATES } from '../components/map';
import { Service, Location, Address } from '../types/service';
import {
  useRecommendationStore,
  Recommendation,
  RecommendationStore,
} from '../stores/recommendation-store';
import { useRouter } from 'next/navigation';
import AdditionalQuestions from '../components/additional-questions';
import EmergencyAlert from '../components/emergency-alert';
import OutOfScopeAlert from '../components/out-of-scope-alert';
import NoServicesFoundAlert from '../components/no-services-found-alert';

const RecommendationPage: React.FC = () => {
  const recommendation = useRecommendationStore(
    (state: RecommendationStore) => state.recommendation
  );
  const setRecommendation = useRecommendationStore(
    (state: RecommendationStore) => state.setRecommendation
  );
  const originalQuery = useRecommendationStore(
    (state: RecommendationStore) => state.query
  );
  const router = useRouter();
  const [mapViewState, setMapViewState] = useState(TORONTO_COORDINATES);
  const [isLoading, setIsLoading] = useState(true);
  const [additionalQuestions, setAdditionalQuestions] = useState<string[]>([]);

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const textColor = useColorModeValue('gray.800', 'white');
  const cardBgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('brand.pink', 'brand.purple');
  const highlightColor = useColorModeValue('pink.100', 'brand.purple');
  const dividerColor = useColorModeValue('gray.200', 'gray.700');

  const mapHeight = '400px';
  const mapWidth = '100%';

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

  const fetchAdditionalQuestions = useCallback(async () => {
    if (!recommendation?.message || !originalQuery) {
      console.error('No recommendation message or original query available');
      return;
    }

    try {
      const response = await fetch(
        `/api/questions?query=${encodeURIComponent(
          originalQuery.query
        )}&recommendation=${encodeURIComponent(recommendation.message)}`
      );
      const data = await response.json();
      setAdditionalQuestions(data.questions);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching additional questions:', error);
      setIsLoading(false);
    }
  }, [recommendation?.message, originalQuery]);

  useEffect(() => {
    if (!recommendation || !originalQuery) {
      router.replace('/');
    } else {
      fetchAdditionalQuestions();
    }
  }, [recommendation, originalQuery, router, fetchAdditionalQuestions]);

  const handleRefineRecommendations = async (answers: string[]) => {
    if (!recommendation || !originalQuery) {
      console.error('No recommendation or original query available');
      return;
    }

    setIsLoading(true);
    try {
      const refineRequest = {
        query: originalQuery,
        recommendation: recommendation.message,
        questions: additionalQuestions,
        answers: answers,
      };

      const response = await fetch('/api/refine_recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(refineRequest),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to refine recommendations');
      }

      const refinedRecommendation: Recommendation = await response.json();
      setRecommendation(refinedRecommendation);

      if (refinedRecommendation.services) {
        updateMapViewState(refinedRecommendation.services);
      }
    } catch (error) {
      console.error('Error refining recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateMapViewState = (services: Service[]) => {
    if (services && services.length > 0) {
      const newMapLocations = services.map((service) => ({
        id: service.id,
        name: service.name,
        latitude: service.latitude,
        longitude: service.longitude,
        description: service.description,
        address: formatAddress(service.address),
        phone: service.phone_numbers[0]?.number || '',
      }));

      const newViewState = computeViewState(newMapLocations);
      setMapViewState(newViewState);
    }
  };

  const mapLocations: Location[] = useMemo(() => {
    if (!recommendation?.services) return [];

    return recommendation.services.map((service) => ({
      id: service.id,
      name: service.name,
      latitude: service.latitude,
      longitude: service.longitude,
      description: service.description,
      address: formatAddress(service.address),
      phone: service.phone_numbers[0]?.number || '',
    }));
  }, [recommendation]);

  useEffect(() => {
    if (mapLocations.length > 0) {
      const newViewState = computeViewState(mapLocations);
      setMapViewState(newViewState);
    }
  }, [mapLocations]);

  const renderRecommendationCard = (recommendation: Recommendation | null) => {
    if (!recommendation?.message) return null;

    const [overviewWithLabel, ...reasoningParts] = recommendation.message
      .split('\n')
      .filter((part) => part.trim() !== '');
    const overview = overviewWithLabel.replace('Overview:', '').trim();
    const reasoning = reasoningParts.join('\n').replace('Reasoning:', '').trim();

    const serviceName = recommendation.services?.[0]?.name || 'Unknown Service';
    const updatedOverview = `<b>${serviceName}</b><br><br>${overview}`;

    return (
      <Box
        bg={cardBgColor}
        p={8}
        borderRadius="lg"
        boxShadow="xl"
        borderWidth={1}
        borderColor={borderColor}
        height="100%"
      >
        <VStack spacing={6} align="stretch">
          <Box>
            <Box dangerouslySetInnerHTML={{ __html: updatedOverview }} />
          </Box>
          <Divider />
          <Box>
            <Badge colorScheme="purple" fontSize="sm" mb={2}>
              Reasoning
            </Badge>
            <Text fontSize="md">{reasoning}</Text>
          </Box>
        </VStack>
      </Box>
    );
  };

  const renderRecommendedServices = (services: Service[] | null) => {
    if (!services) return null;

    const coloredServices = services.map((service, index) => ({
      ...service,
      bgColor: index === 0 ? highlightColor : cardBgColor,
    }));

    return (
      <>
        <Heading as="h2" size="xl" color={textColor} mt={1} mb={1}>
          Recommended Services
        </Heading>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {isLoading ? (
            Array.from({ length: 6 }).map((_, index) => (
              <Box
                key={index}
                bg={cardBgColor}
                p={6}
                borderRadius="lg"
                boxShadow="md"
                borderWidth={1}
                borderColor={borderColor}
              >
                <VStack align="stretch" spacing={4}>
                  <Skeleton height="20px" width="60%" />
                  <SkeletonText
                    mt="2"
                    noOfLines={3}
                    spacing="2"
                    skeletonHeight="2"
                  />
                  <Skeleton height="20px" width="40%" />
                  <Flex>
                    <SkeletonCircle size="8" mr={2} />
                    <Skeleton height="20px" width="30%" />
                  </Flex>
                </VStack>
              </Box>
            ))
          ) : (
            coloredServices.map((service) => (
              <ServiceCard
                key={service.id}
                service={service}
                bgColor={service.bgColor}
              />
            ))
          )}
        </SimpleGrid>
      </>
    );
  };

  const renderContent = () => {
    if (recommendation?.is_emergency) {
      return <EmergencyAlert message={recommendation.message} />;
    }

    if (recommendation?.is_out_of_scope) {
      return <OutOfScopeAlert message={recommendation.message} />;
    }

    if (recommendation?.no_services_found) {
      return (
        <NoServicesFoundAlert message="No services found within the specified radius." />
      );
    }

    return (
      <>
        <Grid templateColumns={{ base: '1fr', lg: '3fr 2fr' }} gap={8}>
          <GridItem>
            {isLoading ? (
              <Box
                bg={cardBgColor}
                p={8}
                borderRadius="lg"
                boxShadow="xl"
                borderWidth={1}
                borderColor={borderColor}
                height="100%"
              >
                <VStack spacing={6} align="stretch">
                  <Skeleton height="20px" width="40%" />
                  <SkeletonText
                    mt="4"
                    noOfLines={4}
                    spacing="4"
                    skeletonHeight="2"
                  />
                  <Divider />
                  <Skeleton height="20px" width="30%" />
                  <SkeletonText
                    mt="4"
                    noOfLines={6}
                    spacing="4"
                    skeletonHeight="2"
                  />
                </VStack>
              </Box>
            ) : (
              renderRecommendationCard(recommendation)
            )}
          </GridItem>
          <GridItem>
            <Box height="100%">
              <Heading as="h3" size="md" color={textColor} mb={4}>
                Service Locations
              </Heading>
              <Box height="calc(100% - 2rem)">
                <Map
                  locations={mapLocations}
                  height={mapHeight}
                  width={mapWidth}
                  initialViewState={mapViewState}
                />
              </Box>
            </Box>
          </GridItem>
        </Grid>
        <Divider my={1} borderColor={dividerColor} borderWidth={2} />
        {renderRecommendedServices(recommendation?.services || null)}
        <Divider my={1} borderColor={dividerColor} borderWidth={2} />
        <Box mt={1}>
          <Heading as="h3" size="lg" color={textColor} mb={8}>
            Refine Your Request
          </Heading>
          <AdditionalQuestions
            questions={additionalQuestions}
            onSubmit={handleRefineRecommendations}
            submitButtonText="Refine Recommendations"
          />
        </Box>
      </>
    );
  };

  return (
    <Box minHeight="100vh" bg={bgColor}>
      <Header />
      <Container maxW="1400px" py={20}>
        <VStack spacing={12} align="stretch">
          <Heading as="h1" size="2xl" color={textColor}>
            Your Recommendation
          </Heading>
          {renderContent()}
        </VStack>
      </Container>
    </Box>
  );
};

export default RecommendationPage;
