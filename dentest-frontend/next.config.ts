import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://api.toothprep.com/api/:path*",
      },
    ];
  },
};

export default nextConfig;