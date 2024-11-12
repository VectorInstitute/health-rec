import React from 'react';
import parse, { HTMLReactParserOptions, Element, DOMNode, Text as DOMText } from 'html-react-parser';
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
  Link,
  Badge,
} from '@chakra-ui/react';
import { FaMapMarkerAlt, FaPhone, FaGlobe, FaClock, FaEnvelope } from 'react-icons/fa';
import { Service, PhoneNumber, Address } from '../types/service';

interface ServiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: Service;
}

const ServiceModal: React.FC<ServiceModalProps> = ({ isOpen, onClose, service }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'white');
  const sectionBgColor = useColorModeValue('gray.50', 'gray.700');
  const highlightColor = useColorModeValue('pink.50', 'pink.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const linkColor = useColorModeValue('pink.600', 'pink.300');

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

  const formatPhoneNumber = (phone: PhoneNumber): string => {
    let formatted = phone.number;
    if (phone.extension) {
      formatted += ` ext. ${phone.extension}`;
    }
    return formatted;
  };

  const renderHtml = (html: string) => {
    const options: HTMLReactParserOptions = {
      replace: (domNode: DOMNode) => {
        if (domNode instanceof Element && domNode.name === 'a' && domNode.attribs) {
          let href = domNode.attribs.href || '';
          if (href && !href.startsWith('http://') && !href.startsWith('https://')) {
            href = `https://${href}`;
          }
          return (
            <Link
              href={href}
              isExternal
              color={linkColor}
              textDecoration="underline"
            >
              {domNode.children[0] instanceof Element
                ? domNode.children[0].children[0] instanceof DOMText
                  ? domNode.children[0].children[0].data
                  : ''
                : domNode.children[0] instanceof DOMText
                  ? domNode.children[0].data
                  : ''}
            </Link>
          );
        }
        return undefined;
      },
    };
    return parse(html, options);
  };

  const renderMetadata = () => {
    if (!service.metadata || Object.keys(service.metadata).length === 0) {
      return null;
    }

    return (
      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
        {Object.entries(service.metadata).map(([key, value]) => {
          if (!value) return null;

          return (
            <GridItem key={key} colSpan={1}>
              <Box
                borderWidth={1}
                borderColor={borderColor}
                borderRadius="md"
                overflow="hidden"
              >
                <Box bg={highlightColor} p={2}>
                  <Text fontWeight="bold" fontSize="sm">
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                  </Text>
                </Box>
                <Box p={2}>
                  <Text fontSize="sm">
                    {Array.isArray(value)
                      ? value.join(', ')
                      : typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                  </Text>
                </Box>
              </Box>
            </GridItem>
          );
        })}
      </Grid>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={bgColor}>
        <ModalHeader color={textColor}>{service.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack align="stretch" spacing={6}>
            {service.description && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Heading as="h4" size="sm" color={textColor} mb={2}>
                  Description
                </Heading>
                <Box color={textColor}>{renderHtml(service.description)}</Box>
              </Box>
            )}

            {service.address && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaMapMarkerAlt} color="purple.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Address
                  </Heading>
                </Flex>
                <Text color={textColor}>{formatAddress(service.address)}</Text>
              </Box>
            )}

            {service.phone_numbers && service.phone_numbers.length > 0 && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaPhone} color="green.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Contact Numbers
                  </Heading>
                </Flex>
                <VStack align="stretch" spacing={2}>
                  {service.phone_numbers.map((phone, index) => (
                    <Flex key={index} justify="space-between" align="center">
                      <Text color={textColor}>
                        {formatPhoneNumber(phone)}
                        {phone.name && ` (${phone.name})`}
                      </Text>
                      {phone.type && (
                        <Badge colorScheme="purple" ml={2}>
                          {phone.type}
                        </Badge>
                      )}
                    </Flex>
                  ))}
                </VStack>
              </Box>
            )}

            {service.email && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaEnvelope} color="blue.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Email
                  </Heading>
                </Flex>
                <Link href={`mailto:${service.email}`} color={linkColor}>
                  {service.email}
                </Link>
              </Box>
            )}

            {service.metadata?.website && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaGlobe} color="purple.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Website
                  </Heading>
                </Flex>
                <Link
                  href={service.metadata.website.startsWith('http')
                    ? service.metadata.website
                    : `https://${service.metadata.website}`}
                  isExternal
                  color={linkColor}
                >
                  {service.metadata.website}
                </Link>
              </Box>
            )}

            {service.metadata?.hours && (
              <Box bg={sectionBgColor} p={4} borderRadius="md">
                <Flex align="center" mb={2}>
                  <Icon as={FaClock} color="orange.500" mr={2} />
                  <Heading as="h4" size="sm" color={textColor}>
                    Hours
                  </Heading>
                </Flex>
                <Text color={textColor}>
                  {Array.isArray(service.metadata.hours)
                    ? service.metadata.hours.join(', ')
                    : service.metadata.hours}
                </Text>
              </Box>
            )}

            <Divider />

            <Box>
              <Heading as="h4" size="sm" color={textColor} mb={4}>
                Additional Information
              </Heading>
              {renderMetadata()}
            </Box>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="pink" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ServiceModal;
