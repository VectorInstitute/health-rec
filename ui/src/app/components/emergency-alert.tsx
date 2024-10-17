import React from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  VStack,
  Text,
  Link,
  UnorderedList,
  ListItem,
  OrderedList,
} from '@chakra-ui/react';

interface EmergencyAlertProps {
  message: string;
}

const EmergencyAlert: React.FC<EmergencyAlertProps> = ({ message }) => {
  const formatMessage = (msg: string): React.ReactNode[] => {
    const sections = msg.trim().split('\n\n');
    return sections.map((section, sectionIndex) => {
      const lines = section.split('\n');
      const title = lines[0];
      const content = lines.slice(1);

      if (title.endsWith(':')) {
        return (
          <Box key={sectionIndex} mt={4}>
            <Text fontWeight="bold">{title}</Text>
            {content.map((line, lineIndex) => {
              if (line.startsWith('•')) {
                return (
                  <UnorderedList key={lineIndex} mt={2}>
                    <ListItem>{formatLinks(line.slice(1).trim())}</ListItem>
                  </UnorderedList>
                );
              } else if (line.match(/^\d+\./)) {
                return (
                  <OrderedList key={lineIndex} mt={2}>
                    <ListItem>{formatLinks(line.replace(/^\d+\./, '').trim())}</ListItem>
                  </OrderedList>
                );
              } else {
                return <Text key={lineIndex} mt={2}>{formatLinks(line)}</Text>;
              }
            })}
          </Box>
        );
      } else {
        return <Text key={sectionIndex} mt={4}>{formatLinks(section)}</Text>;
      }
    });
  };

  const formatLinks = (text: string): React.ReactNode => {
    const parts = text.split(/(https?:\/\/[^\s]+)/g);
    return parts.map((part, index) =>
      part.match(/^https?:\/\//) ? (
        <Link key={index} href={part} isExternal color="blue.600" textDecoration="underline">
          {part}
        </Link>
      ) : (
        part
      )
    );
  };

  return (
    <Alert
      status="error"
      variant="subtle"
      flexDirection="column"
      alignItems="flex-start"
      justifyContent="flex-start"
      textAlign="left"
      borderRadius="md"
      p={8}
      width="100%"
      bg="red.50"
      color="red.800"
    >
      <VStack spacing={4} width="100%" align="stretch">
        <AlertIcon boxSize="40px" />
        <AlertTitle fontSize="2xl" textAlign="center">Emergency Situation Detected</AlertTitle>
        <AlertDescription>
          {formatMessage(message)}
        </AlertDescription>
      </VStack>
    </Alert>
  );
};

export default EmergencyAlert;
