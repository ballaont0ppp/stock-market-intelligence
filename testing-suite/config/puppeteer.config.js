/**
 * Puppeteer Configuration
 * Centralized configuration for browser automation
 */

module.exports = {
  // Browser launch options
  browser: {
    headless: process.env.HEADLESS !== 'false',
    devtools: process.env.PUPPETEER_DEVTOOLS === 'true',
    defaultViewport: { width: 1280, height: 720 },
    timeout: 30000,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding',
      '--disable-web-security', // For testing environments only
      '--disable-features=VizDisplayCompositor'
    ]
  },
  
  // Test configuration
  test: {
    baseUrl: process.env.TEST_URL || 'http://localhost:3000',
    timeout: 30000,
    retries: 0,
    screenshotOnFailure: process.env.SCREENSHOT_ON_FAILURE === 'true',
    videoRecording: process.env.VIDEO_RECORDING === 'true',
    slowMo: parseInt(process.env.SLOW_MO || '0'), // Slow down operations in ms
    viewport: {
      width: parseInt(process.env.VIEWPORT_WIDTH || '1280'),
      height: parseInt(process.env.VIEWPORT_HEIGHT || '720')
    }
  },
  
  // Network configuration
  network: {
    offline: process.env.TEST_OFFLINE === 'true',
    slowNetwork: process.env.TEST_SLOW_NETWORK === 'true',
    cacheEnabled: process.env.CACHE_ENABLED !== 'false'
  },
  
  // Environment specific settings
  environments: {
    development: {
      browser: { headless: false, devtools: true }
    },
    staging: {
      browser: { headless: true }
    },
    production: {
      browser: { headless: true }
    },
    test: {
      browser: { headless: true }
    }
  },
  
  // Screenshot and video settings
  artifacts: {
    screenshotsDir: 'results/screenshots',
    videosDir: 'results/videos',
    tracesDir: 'results/traces'
  },
  
  // Device emulation
  devices: {
    desktop: { width: 1280, height: 720, deviceScaleFactor: 1 },
    tablet: { width: 768, height: 1024, deviceScaleFactor: 2 },
    mobile: { width: 375, height: 667, deviceScaleFactor: 2 }
  },
  
  // Timeouts
  timeouts: {
    navigation: 30000,
    pageLoad: 30000,
    elementWait: 10000,
    script: 5000
  }
};