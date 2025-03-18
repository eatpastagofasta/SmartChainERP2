import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Add this line to enable static export
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