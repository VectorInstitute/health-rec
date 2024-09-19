'use client';

import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  Badge,
  Flex,
} from '@chakra-ui/react';
import ServiceCard from '../components/service-card';
import Header from '../components/header';
import { useRecommendationStore } from '../stores/recommendation-store';
import { useRouter } from 'next/navigation';

interface Service {
  id: string;
  PublicName: string;
  Description?: string;
  [key: string]: any;
}

interface Recommendation {
  is_emergency: boolean;
  message: string;
  services: Service[];
}

const RecommendationPage: React.FC = () => {
  const recommendation = useRecommendationStore((state) => state.recommendation);
  const router = useRouter();

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const textColor = useColorModeValue('gray.800', 'white');
  const cardBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  React.useEffect(() => {
    if (!recommendation) {
      router.push('/');
    }
  }, [recommendation, router]);

  if (!recommendation) {
    return null;
  }

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

  const renderRecommendationCard = (recommendation: Recommendation) => {
    const [overviewWithLabel, ...reasoningParts] = recommendation.message.split('\n').filter(part => part.trim() !== '');
    const overview = overviewWithLabel.replace('Overview:', '').trim();
    const reasoning = reasoningParts.join('\n').replace('Reasoning:', '').trim();

    return (
      <Box bg={cardBgColor} p={8} borderRadius="lg" boxShadow="xl" borderWidth={1} borderColor={borderColor}>
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

  const renderRecommendedServices = (services: Service[]) => (
    <>
      <Heading as="h2" size="xl" color={textColor} mt={12} mb={6}>
        Recommended Services
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
        {services.map((service) => (
          <ServiceCard key={service.id} service={service} />
        ))}
      </SimpleGrid>
    </>
  );

  return (
    <Box minHeight="100vh" bg={bgColor}>
      <Header />
      <Container maxW="1200px" py={20}>
        <VStack spacing={8} align="stretch">
          <Flex justifyContent="space-between" alignItems="center">
            <Heading as="h1" size="2xl" color={textColor}>
              Your Recommendation
            </Heading>
            <Badge colorScheme="blue" fontSize="md" p={2} borderRadius="md">
              Personalized Result
            </Badge>
          </Flex>
          {recommendation.is_emergency
            ? renderEmergencyAlert(recommendation.message)
            : renderRecommendationCard(recommendation)}
          {!recommendation.is_emergency && renderRecommendedServices(recommendation.services)}
        </VStack>
      </Container>
    </Box>
  );
};

export default RecommendationPage;
