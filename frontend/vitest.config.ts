import { defineConfig } from 'vitest/config';

// https://vite.dev/config/
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setupTests.ts',
    include: ['tests/**/*.{test,spec}.{ts,js,tsx,jsx}'],
    exclude: [
      'tests/e2e/**',
      'node_modules/**'
    ],
  },
})