/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    css: true,
    // Exclude E2E tests and other non-unit test files
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/e2e/**',
      '**/playwright/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,cypress,tsup,build}.config.*'
    ],
    // Support MSW (Mock Service Worker)
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
        '**/dist/**',
        '**/.next/**',
        '**/e2e/**',
        '**/playwright/**',
        '**/__tests__/**',
        '**/test-results/**',
        '**/playwright-report/**',
        '**/lighthouserc.json',
        '**/next.config.js',
        '**/postcss.config.js',
        '**/tailwind.config.ts',
        '**/tsconfig.json',
        '**/vitest.config.mts',
        '**/vitest.setup.ts',
        '**/playwright.config.ts',
        '**/middleware.ts',
        '**/next-env.d.ts',
        '**/app/globals.css',
        '**/styles/**',
        '**/components.json',
        '**/bun.lock',
        '**/package-lock.json',
        '**/pnpm-lock.yaml',
        '**/tsconfig.tsbuildinfo',
        '**/README.md',
        '**/COMPONENT_LIBRARY_SUMMARY.md',
        '**/COMPONENTS_REFERENCE.md',
        '**/lighthouserc.json',
        '**/__mocks__/**',
        '**/test/**',
        '**/e2e-pages/**',
        '**/test-results/**',
        '**/playwright-report/**'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    },
  },
  resolve: {
    alias: {
      // Match Next.js path aliases
      '@': path.resolve(__dirname, './'),
      '@/components': path.resolve(__dirname, './components'),
      '@/lib': path.resolve(__dirname, './lib'),
      '@/app': path.resolve(__dirname, './app'),
      '@/styles': path.resolve(__dirname, './styles'),
    },
  },
})