const { withLogtail } = require('@logtail/next');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    legacyBrowsers: false,
    browsersListForSwc: true,
  },
};

module.exports = withLogtail(nextConfig);
