/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure API routes for longer timeouts
  experimental: {
    // Increase the timeout for API routes to 20 minutes
    serverComponentsExternalPackages: [],
  },
  // Configure server timeout
  serverRuntimeConfig: {
    // Increase timeout for long-running operations
    timeout: 20 * 60 * 1000, // 20 minutes
  },
  // Add headers timeout configuration
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
          {
            key: 'Connection',
            value: 'keep-alive',
          },
        ],
      },
    ]
  },
};

export default nextConfig;
