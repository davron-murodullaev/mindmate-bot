/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/dashboard',
  assetPrefix: '/dashboard',
  images: { unoptimized: true },
  trailingSlash: true,
}

module.exports = nextConfig
