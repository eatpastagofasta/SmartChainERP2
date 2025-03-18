import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export', // ✅ Enables static export mode
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