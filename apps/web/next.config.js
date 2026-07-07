/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: { allowedOrigins: ['localhost:3000'] }
  },
  async rewrites() {
    return [
      { source: '/api/server/:path*', destination: `${process.env.SERVER_URL || 'http://localhost:4000'}/:path*` }
    ]
  }
}
module.exports = nextConfig