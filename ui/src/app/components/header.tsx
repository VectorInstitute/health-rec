'use client';

import React, { memo } from 'react';
import { Box, Flex, Link, Container, Image, useBreakpointValue, IconButton, Drawer, DrawerBody, DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton, useDisclosure } from '@chakra-ui/react'
import NextLink from 'next/link'
import { HamburgerIcon } from '@chakra-ui/icons'
import { useRouter } from 'next/navigation'

const NavLinks: React.FC = memo(() => (
  <>
    <Link as={NextLink} href="/discover" color="white" fontWeight="semibold">
      Discover
    </Link>
    <Link as={NextLink} href="/about" color="white" fontWeight="semibold">
      About
    </Link>
  </>
));

NavLinks.displayName = 'NavLinks';

const Header: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const logoSize = useBreakpointValue({ base: "120px", md: "150px" })
  const isMobile = useBreakpointValue({ base: true, md: false })
  const router = useRouter()

  const handleLogoClick = () => {
    router.push('/')
  }

  return (
    <Box as="header" position="absolute" top={0} left={0} right={0} zIndex={10} bg="transparent">
      <Container maxW="1200px">
        <Flex justify="space-between" align="center" py={4}>
          <Box
            width={logoSize}
            height="40px"
            position="relative"
            cursor="pointer"
            onClick={handleLogoClick}
          >
            <Image
              src="/images/vector-logo.png"
              alt="Vector Institute"
              objectFit="contain"
              width="100%"
              height="100%"
            />
          </Box>
          {isMobile ? (
            <>
              <IconButton
                aria-label="Open menu"
                icon={<HamburgerIcon />}
                onClick={onOpen}
                variant="outline"
                color="white"
              />
              <Drawer isOpen={isOpen} placement="right" onClose={onClose}>
                <DrawerOverlay />
                <DrawerContent>
                  <DrawerCloseButton />
                  <DrawerHeader>Menu</DrawerHeader>
                  <DrawerBody>
                    <Flex direction="column" gap={4}>
                      <NavLinks />
                    </Flex>
                  </DrawerBody>
                </DrawerContent>
              </Drawer>
            </>
          ) : (
            <Flex gap={6}>
              <NavLinks />
            </Flex>
          )}
        </Flex>
      </Container>
    </Box>
  )
}

export default memo(Header);
