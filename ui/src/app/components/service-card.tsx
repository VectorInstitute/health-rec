import React from 'react';
import parse, { Element, HTMLReactParserOptions, domToReact, DOMNode } from 'html-react-parser';
import { Box, Heading, Text, VStack, useColorModeValue, useDisclosure, Flex, Badge, Icon } from '@chakra-ui/react';
import { FaMapMarkerAlt } from 'react-icons/fa';
import ServiceModal from './service-modal';
import { Service } from '../types/service';

interface ServiceCardProps {
  service: Service;
}

const ServiceCard: React.FC<ServiceCardProps> = ({ service }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');

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
              color="blue.500"
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

  return (
    <>
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        p={6}
        bg={bgColor}
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
        <VStack align="start" spacing={3}>
          <Heading as="h3" size="md" color={textColor}>
            {service.PublicName}
          </Heading>
          {service.Description && (
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
              {renderHtml(service.Description)}
            </Box>
          )}
        </VStack>
        <Flex mt={4} align="center" justify="space-between">
          {service.ServiceArea && (
            <Flex align="center">
              <Icon as={FaMapMarkerAlt} color="blue.500" mr={2} />
              <Text fontSize="sm" color={textColor}>
                {Array.isArray(service.ServiceArea) ? service.ServiceArea[0] : service.ServiceArea}
              </Text>
            </Flex>
          )}
          <Badge colorScheme="green">View Details</Badge>
        </Flex>
      </Box>
      <ServiceModal isOpen={isOpen} onClose={onClose} service={service} />
    </>
  );
};

export default ServiceCard;
