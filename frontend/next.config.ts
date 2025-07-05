import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    } else {
      // Server-side fallbacks to prevent issues with browser-only modules
      config.resolve.fallback = {
        ...config.resolve.fallback,
        'pino-pretty': false,
      };
    }
    
    // Ignore browser-only modules on server
    config.externals = config.externals || [];
    if (isServer) {
      config.externals.push({
        'pino-pretty': 'pino-pretty',
      });
    }
    
    return config;
  },
  images: {
    unoptimized: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  serverExternalPackages: ['@walletconnect/logger'],
};

export default nextConfig;
