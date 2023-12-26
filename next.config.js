const { withLogtail } = require("@logtail/next");

/** @type {import('next').NextConfig} */
const nextConfig = {
  i18n: {
    locales: ["ru", "en"],
    defaultLocale: "ru",
  },
  experimental: {
    swcPlugins: [["@lingui/swc-plugin", {}]],
  },
};

module.exports = withLogtail(nextConfig);
