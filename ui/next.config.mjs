/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: `http://${process.env.NEXT_PUBLIC_BACKEND_HOST || 'localhost'}:${process.env.NEXT_PUBLIC_BACKEND_PORT || '8000'}/:path*`, // Proxy to Backend
        },
      ]
    },
    serverRuntimeConfig: {
      backendHost: process.env.NEXT_PUBLIC_BACKEND_HOST || 'localhost',
      backendPort: process.env.NEXT_PUBLIC_BACKEND_PORT || '8000',
    },
    publicRuntimeConfig: {
      backendHost: process.env.NEXT_PUBLIC_BACKEND_HOST || 'localhost',
      backendPort: process.env.NEXT_PUBLIC_BACKEND_PORT || '8000',
    },
  }

  export default nextConfig
