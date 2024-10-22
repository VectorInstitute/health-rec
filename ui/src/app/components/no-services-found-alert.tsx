import React from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  VStack,
  Text,
  Button,
  useBreakpointValue,
  Link,
  useColorModeValue,
} from '@chakra-ui/react';
import NextLink from 'next/link';

interface NoServicesFoundAlertProps {
  message: string;
}

const NoServicesFoundAlert: React.FC<NoServicesFoundAlertProps> = ({ message }) => {
  const spacing = useBreakpointValue({ base: 4, md: 6 });
  const padding = useBreakpointValue({ base: 4, md: 8 });
  const titleFontSize = useBreakpointValue({ base: "xl", md: "2xl" });

  const bgColor = useColorModeValue('blue.50', 'blue.900');
  const textColor = useColorModeValue('blue.800', 'blue.100');
  const buttonColorScheme = useColorModeValue('blue', 'teal');

  return (
    <Alert
      status="info"
      variant="subtle"
      flexDirection="column"
      alignItems="flex-start"
      justifyContent="flex-start"
      textAlign="left"
      borderRadius="md"
      p={padding}
      width="100%"
      bg={bgColor}
      color={textColor}
    >
      <VStack spacing={spacing} width="100%" align="stretch">
        <AlertIcon boxSize={{ base: "30px", md: "40px" }} />
        <AlertTitle fontSize={titleFontSize} textAlign="center">No Services Found</AlertTitle>
        <AlertDescription>
          <Text>{message}</Text>
          <Box mt={spacing}>
            <Text fontWeight="bold">Suggestions:</Text>
            <VStack align="stretch" mt={2} spacing={2}>
              <Text>• Try expanding your search radius</Text>
              <Text>• Check for alternative services that might be available</Text>
              <Text>• Consider online or remote options if applicable</Text>
            </VStack>
          </Box>
          <Box mt={spacing} textAlign="center">
            <NextLink href="/" passHref>
              <Button as={Link} colorScheme={buttonColorScheme} size="lg">
                Start a New Search
              </Button>
            </NextLink>
          </Box>
        </AlertDescription>
      </VStack>
    </Alert>
  );
};

export default NoServicesFoundAlert;
