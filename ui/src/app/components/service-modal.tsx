import React from 'react';
import parse from 'html-react-parser';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Text,
  VStack,
  Heading,
  Box,
  useColorModeValue,
  Flex,
  Icon,
  Divider,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import { FaMapMarkerAlt, FaPhone, FaGlobe, FaClock } from 'react-icons/fa';

interface Service {
  PublicName: string;
  Description?: string;
  ServiceArea?: string | string[];
  PhoneNumber?: string;
  WebsiteUrl?: string;
  Hours?: string;
  [key: string]: any;
}

interface ServiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: Service;
}

const ServiceModal: React.FC<ServiceModalProps> = ({ isOpen, onClose, service }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'white');
  const sectionBgColor = useColorModeValue('gray.50', 'gray.700');
  const highlightColor = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const formatServiceArea = (serviceArea: string | string[] | undefined): string => {
    if (Array.isArray(serviceArea)) {
      return serviceArea.join(', ');
    } else if (typeof serviceArea === 'string') {
      return serviceArea;
    }
    return 'Not specified';
  };

  const renderHtml = (html: string) => {
    const options = {
      replace: (domNode: any) => {
        if (domNode.type === 'tag' && domNode.name === 'a') {
          return (
            <Text
              as="a"
              href={domNode.attribs.href}
              target="_blank"
              rel="noopener noreferrer"
              color="blue.500"
              textDecoration="underline"
            >
              {domNode.children[0].data}
            </Text>
          );
        }
      },
    };
    return parse(html, options);
  };

  const renderAdditionalInfo = () => {
    const excludedKeys = ['id', 'ParentId', 'Score', 'Hours2', 'RecordOwner', 'UniqueIDPriorSystem', 'Latitude', 'Longitude', 'TaxonomyCodes', 'TaxonomyTerm', 'TaxonomyTerms', 'PublicName', 'Description', 'ServiceArea', 'PhoneNumber', 'WebsiteUrl', 'Hours'];
    const additionalInfo = Object.entries(service).filter(([key]) => !excludedKeys.includes(key));

    return (
      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
        {additionalInfo.map(([key, value]) => (
          <GridItem key={key} colSpan={1}>
            <Box
              borderWidth={1}
              borderColor={borderColor}
              borderRadius="md"
              overflow="hidden"
            >
              <Box bg={highlightColor} p={2}>
                <Text fontWeight="bold" fontSize="sm">
                  {key}
                </Text>
              </Box>
              <Box p={2}>
                <Text fontSize="sm">
                  {typeof value === 'string' ? value : JSON.stringify(value)}
                </Text>
              </Box>
            </Box>
          </GridItem>
        ))}
      </Grid>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={bgColor}>
        <ModalHeader color={textColor}>{service.PublicName}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack align="stretch" spacing={6}>
            {service.Description && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Heading as="h4" size="sm" color={textColor} mb={2}>
                  Description
                </Heading>
                <Box color={textColor}>{renderHtml(service.Description)}</Box>
              </Box>
            )}
            {service.ServiceArea && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaMapMarkerAlt} color="blue.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Service Area
                  </Heading>
                </Flex>
                <Text color={textColor}>{formatServiceArea(service.ServiceArea)}</Text>
              </Box>
            )}
            {service.PhoneNumber && (
              <Flex align="center">
                <Icon as={FaPhone} color="green.500" mr={2} />
                <Text color={textColor}>{service.PhoneNumber}</Text>
              </Flex>
            )}
            {service.WebsiteUrl && (
              <Flex align="center">
                <Icon as={FaGlobe} color="purple.500" mr={2} />
                <Text
                  color={textColor}
                  as="a"
                  href={service.WebsiteUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {service.WebsiteUrl}
                </Text>
              </Flex>
            )}
            {service.Hours && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaClock} color="orange.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Hours
                  </Heading>
                </Flex>
                <Text color={textColor}>{service.Hours}</Text>
              </Box>
            )}
            <Divider />
            <Box>
              <Heading as="h4" size="sm" color={textColor} mb={4}>
                Additional Information
              </Heading>
              {renderAdditionalInfo()}
            </Box>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ServiceModal;
