/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable App Router (default in Next.js 15)
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb'
    }
  },

  // API proxy configuration
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8080/api/v1/:path*'
      }
    ];
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1'
  }
};

module.exports = nextConfig;
