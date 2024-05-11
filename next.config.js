const { withLogtail } = require("@logtail/next");

/** @type {import('next').NextConfig} */
const nextConfig = {
  i18n: {
    locales: ["ru"],
    defaultLocale: "ru",
  },
  experimental: {
    swcPlugins: [["@lingui/swc-plugin", {}]],
    serverMinification: false,
  },
  async redirects() {
    return [
      {
        source: "/2023/:userId",
        destination: "/404",
        permanent: true,
      },
    ];
  },
};

if (process.env.STANDALONE === "true") {
  nextConfig.output = "standalone";
}

module.exports = withLogtail(nextConfig);
