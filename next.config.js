const { withLogtail } = require("@logtail/next");

/** @type {import('next').NextConfig} */
const nextConfig = {
  i18n: {
    locales: ["ru", "en"],
    defaultLocale: "ru",
  },
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    legacyBrowsers: false,
    swcPlugins: [["@lingui/swc-plugin", {}]],
  },
};

module.exports = withLogtail(nextConfig);
