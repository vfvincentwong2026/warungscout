// ============================================================
// WarungScout Vite 构建配置
// 用于 React 前端项目
// ============================================================

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // 支持 Fast Refresh
      fastRefresh: true,
    }),
  ],

  // 路径别名
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@api': path.resolve(__dirname, './src/api'),
      '@types': path.resolve(__dirname, './src/types'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },

  // 开发服务器配置
  server: {
    port: 5173,
    host: true,
    open: true,
    // API 代理（开发环境）
    proxy: {
      '/api': {
        target: 'http://localhost:8787',
        changeOrigin: true,
      },
    },
  },

  // 预览服务器配置
  preview: {
    port: 4173,
    host: true,
  },

  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        // 代码分割
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          charts: ['recharts'],
          utils: ['date-fns', 'clsx', 'tailwind-merge'],
        },
      },
    },
    // 压缩选项
    target: 'es2020',
    chunkSizeWarningLimit: 1000,
  },

  // CSS 配置
  css: {
    postcss: './postcss.config.js',
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },

  // 环境变量前缀
  envPrefix: 'VITE_',

  // 优化依赖预构建
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'recharts'],
  },

  // 静态资源处理
  assetsInclude: ['**/*.png', '**/*.jpg', '**/*.svg'],

  // 定义全局变量
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
  },
})
