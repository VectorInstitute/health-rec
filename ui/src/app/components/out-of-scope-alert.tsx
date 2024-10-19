import React from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  VStack,
  Text,
  useBreakpointValue,
} from '@chakra-ui/react';

interface OutOfScopeAlertProps {
  message: string;
}

const OutOfScopeAlert: React.FC<OutOfScopeAlertProps> = ({ message }) => {
  const [responseWithLabel, reasoningWithLabel] = message.split('Reasoning:').map((part: string) => part.trim());
  const response = responseWithLabel.replace(/^Response:\s*/, '').trim();
  const reasoning = reasoningWithLabel?.trim();

  const spacing = useBreakpointValue({ base: 4, md: 6 });
  const padding = useBreakpointValue({ base: 4, md: 8 });
  const titleFontSize = useBreakpointValue({ base: "xl", md: "2xl" });

  return (
    <Alert
      status="warning"
      variant="subtle"
      flexDirection="column"
      alignItems="flex-start"
      justifyContent="flex-start"
      textAlign="left"
      borderRadius="md"
      p={padding}
      width="100%"
      bg="yellow.50"
      color="yellow.800"
    >
      <VStack spacing={spacing} width="100%" align="stretch">
        <AlertIcon boxSize={{ base: "30px", md: "40px" }} />
        <AlertTitle fontSize={titleFontSize} textAlign="center">Out of Scope Request</AlertTitle>
        <AlertDescription>
          <Text>{response}</Text>
          {reasoning && (
            <Box mt={spacing}>
              <Text fontWeight="bold">Reasoning:</Text>
              <Text mt={2}>{reasoning}</Text>
            </Box>
          )}
        </AlertDescription>
      </VStack>
    </Alert>
  );
};

export default OutOfScopeAlert;
