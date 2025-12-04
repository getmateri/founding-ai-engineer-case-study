/** @type {import('next').NextConfig} */
const nextConfig = {
  // Increase timeout for long-running API calls (extraction takes ~60s)
  experimental: {
    proxyTimeout: 120000, // 2 minutes
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;

