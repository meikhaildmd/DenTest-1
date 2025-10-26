import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No dynamic key here — remove it if it’s present
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
};

export default nextConfig;