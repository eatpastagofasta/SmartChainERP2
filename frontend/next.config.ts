import { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  trailingSlash: true,  // Fixes missing pages issue
  images: {
    domains: ["https://smartchainerp2.onrender.com/"], // Allow image loading from backend
  },
};

module.exports = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/authentication',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;