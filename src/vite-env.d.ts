// ============================================================
// WarungScout Vite 环境类型声明
// 用于 TypeScript 识别 Vite 特有类型
// ============================================================

/// <reference types="vite/client" />

// ============================================================
// 环境变量类型声明
// ============================================================

interface ImportMetaEnv {
  /** API 基础地址 */
  readonly VITE_API_BASE_URL: string
  /** 应用环境 */
  readonly VITE_APP_ENV: 'development' | 'preview' | 'production'
  /** 应用名称 */
  readonly VITE_APP_NAME: string
  /** 应用版本 */
  readonly VITE_APP_VERSION: string
  /** 是否启用调试模式 */
  readonly VITE_DEBUG: string
  /** 是否启用 AI 功能 */
  readonly VITE_ENABLE_AI: string
  /** Google Maps API Key */
  readonly VITE_GOOGLE_MAPS_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// ============================================================
// 声明全局变量
// ============================================================

declare const __APP_VERSION__: string

// ============================================================
// CSS 模块声明
// ============================================================

declare module '*.css' {
  const content: { [className: string]: string }
  export default content
}

declare module '*.scss' {
  const content: { [className: string]: string }
  export default content
}

// ============================================================
// 图片资源声明
// ============================================================

declare module '*.png' {
  const src: string
  export default src
}

declare module '*.jpg' {
  const src: string
  export default src
}

declare module '*.jpeg' {
  const src: string
  export default src
}

declare module '*.svg' {
  import * as React from 'react'
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  const src: string
  export default src
}

declare module '*.webp' {
  const src: string
  export default src
}
