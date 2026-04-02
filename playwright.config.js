// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '*.spec.js',
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'npx serve . -l 3000 --no-clipboard --no-request-logging',
    port: 3000,
    reuseExistingServer: true,
  },
  projects: [
    {
      name: 'desktop',
      use: { viewport: { width: 1440, height: 900 } },
    },
    {
      name: 'mobile',
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
});
