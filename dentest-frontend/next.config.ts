import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },

  // Allow optimized image loading from your Django backend and localhost
  images: {
    domains: ["api.toothprep.com", "127.0.0.1", "localhost"],
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