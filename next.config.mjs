///** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure API routes for longer timeouts
  experimental: {
    // Increase the timeout for API routes to 20 minutes
    serverComponentsExternalPackages: [],
  },
  // Configure API routes timeout
  api: {
    // Disable body parser size limit and increase timeout
    bodyParser: {
      sizeLimit: '50mb',
    },
    responseLimit: false,
    // Set timeout to 2 hours for long running processes
    timeout: 120 * 60 * 1000, // 120 minutes in milliseconds
  },
  // Configure server timeout
  serverRuntimeConfig: {
    // Increase timeout for long-running operations
timeout: 120 * 60 * 1000, // 120 minutes
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
