import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    
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
