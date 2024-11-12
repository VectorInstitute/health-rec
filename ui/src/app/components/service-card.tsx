import React from 'react';
import parse, { Element, HTMLReactParserOptions, domToReact, DOMNode } from 'html-react-parser';
import {
  Box,
  Heading,
  Text,
  VStack,
  useColorModeValue,
  useDisclosure,
  Flex,
  Badge,
  Icon,
  Link,
} from '@chakra-ui/react';
import { FaMapMarkerAlt, FaPhone, FaEnvelope, FaGlobe } from 'react-icons/fa';
import ServiceModal from './service-modal';
import { Service, Address } from '../types/service';

interface ServiceCardProps {
  service: Service;
  bgColor?: string;
}

const ServiceCard: React.FC<ServiceCardProps> = ({ service, bgColor }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const defaultBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedColor = useColorModeValue('gray.600', 'gray.400');

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

  const renderHtml = (html: string) => {
    const options: HTMLReactParserOptions = {
      replace: (domNode) => {
        if (domNode instanceof Element && domNode.name === 'a' && domNode.attribs) {
          return (
            <Text
              as="a"
              href={domNode.attribs.href || ''}
              target="_blank"
              rel="noopener noreferrer"
              color="pink.500"
              textDecoration="underline"
              onClick={(e) => e.stopPropagation()}
            >
              {domToReact(domNode.children as DOMNode[], options)}
            </Text>
          );
        }
        return undefined;
      },
    };
    return parse(html, options);
  };

  const primaryPhone = service.phone_numbers[0]?.number;
  const website = service.metadata?.website;

  return (
    <>
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        p={6}
        bg={bgColor || defaultBgColor}
        borderColor={borderColor}
        cursor="pointer"
        onClick={onOpen}
        transition="all 0.3s"
        _hover={{ transform: 'translateY(-5px)', boxShadow: 'lg' }}
        height="100%"
        display="flex"
        flexDirection="column"
        justifyContent="space-between"
      >
        <VStack align="start" spacing={4}>
          <Heading as="h3" size="md" color={textColor}>
            {service.name}
          </Heading>

          {service.description && (
            <Box
              noOfLines={3}
              color={textColor}
              overflow="hidden"
              textOverflow="ellipsis"
              css={{
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {renderHtml(service.description)}
            </Box>
          )}

          <VStack align="start" spacing={2} width="100%">
            {service.address && (
              <Flex align="center" width="100%">
                <Icon as={FaMapMarkerAlt} color="pink.500" mr={2} />
                <Text fontSize="sm" color={mutedColor} noOfLines={1}>
                  {formatAddress(service.address)}
                </Text>
              </Flex>
            )}

            {primaryPhone && (
              <Flex align="center" width="100%">
                <Icon as={FaPhone} color="pink.500" mr={2} />
                <Link
                  href={`tel:${primaryPhone}`}
                  color={mutedColor}
                  fontSize="sm"
                  onClick={(e) => e.stopPropagation()}
                >
                  {primaryPhone}
                </Link>
              </Flex>
            )}

            {service.email && (
              <Flex align="center" width="100%">
                <Icon as={FaEnvelope} color="pink.500" mr={2} />
                <Link
                  href={`mailto:${service.email}`}
                  color={mutedColor}
                  fontSize="sm"
                  onClick={(e) => e.stopPropagation()}
                >
                  {service.email}
                </Link>
              </Flex>
            )}

            {website && (
              <Flex align="center" width="100%">
                <Icon as={FaGlobe} color="pink.500" mr={2} />
                <Link
                  href={website}
                  target="_blank"
                  rel="noopener noreferrer"
                  color={mutedColor}
                  fontSize="sm"
                  onClick={(e) => e.stopPropagation()}
                >
                  Website
                </Link>
              </Flex>
            )}
          </VStack>
        </VStack>

        <Flex mt={4} align="center" justify="space-between">
          {service.metadata?.services && (
            <Flex gap={2} flexWrap="wrap">
              {(Array.isArray(service.metadata.services)
                ? service.metadata.services
                : [service.metadata.services]
              ).slice(0, 2).map((serviceName, index) => (
                <Badge
                  key={index}
                  colorScheme="purple"
                  fontSize="xs"
                >
                  {serviceName}
                </Badge>
              ))}
              {(Array.isArray(service.metadata.services)
                ? service.metadata.services.length
                : 1) > 2 && (
                <Badge colorScheme="gray" fontSize="xs">
                  +{(Array.isArray(service.metadata.services)
                    ? service.metadata.services.length
                    : 1) - 2} more
                </Badge>
              )}
            </Flex>
          )}
          <Badge colorScheme="pink">View Details</Badge>
        </Flex>
      </Box>
      <ServiceModal isOpen={isOpen} onClose={onClose} service={service} />
    </>
  );
};

export default ServiceCard;
