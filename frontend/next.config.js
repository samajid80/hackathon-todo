/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  // T153: Enable compression for production builds
  compress: true,

  // T153: Optimize package imports for better code splitting
  experimental: {
    optimizePackageImports: ['@better-auth/react'],
  },

  // T153: Production optimizations
  swcMinify: true, // Use SWC for faster minification

  // T153: Configure webpack for better bundle optimization
  webpack: (config, { dev, isServer }) => {
    // Enable tree shaking for production builds
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
      };
    }

    return config;
  },

  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // T153: Configure image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // T158: Content Security Policy (CSP) headers
  async headers() {
    return [
      {
        // Apply security headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              // Default: Only allow resources from same origin
              "default-src 'self'",

              // Scripts: Allow same-origin and inline scripts (required for Next.js)
              // Note: 'unsafe-inline' is needed for Next.js development and some runtime features
              // For production, consider using nonce or hash-based CSP
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",

              // Styles: Allow same-origin and inline styles (required for Tailwind CSS)
              // Tailwind uses style injection, which requires 'unsafe-inline'
              "style-src 'self' 'unsafe-inline'",

              // Images: Allow same-origin, data URIs, and HTTPS images
              // data: is needed for base64-encoded images
              // https: allows loading images from CDNs
              "img-src 'self' data: https:",

              // Fonts: Allow same-origin fonts
              // Add 'https:' if using external font providers (Google Fonts, etc.)
              "font-src 'self'",

              // Connect: Allow API connections to backend
              // In development: localhost:8000
              // In production: Replace with actual API domain
              `connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}`,

              // Object: Disallow Flash and other plugins
              "object-src 'none'",

              // Media: Allow same-origin media
              "media-src 'self'",

              // Frame: Disallow embedding in iframes (prevent clickjacking)
              "frame-src 'none'",

              // Base URI: Restrict base tag to same origin
              "base-uri 'self'",

              // Form Action: Only allow forms to submit to same origin
              "form-action 'self'",

              // Frame Ancestors: Prevent page from being embedded
              "frame-ancestors 'none'",

              // Upgrade Insecure Requests: Automatically upgrade HTTP to HTTPS (production)
              // Commented out for development (HTTP localhost)
              // Uncomment for production:
              // "upgrade-insecure-requests",
            ].join('; '),
          },
          {
            // X-DNS-Prefetch-Control: Control DNS prefetching
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            // X-Frame-Options: Prevent clickjacking (legacy, CSP frame-ancestors is preferred)
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            // X-Content-Type-Options: Prevent MIME sniffing
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            // Referrer-Policy: Control referrer information
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            // Permissions-Policy: Control browser features
            // Disable unnecessary features like geolocation, camera, microphone
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
          },
        ],
      },
    ];
  },
}

module.exports = nextConfig
