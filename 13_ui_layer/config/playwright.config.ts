import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 30000,
  testDir: '13_ui_layer/e2e',
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:8080',
    headless: true,
  },
});