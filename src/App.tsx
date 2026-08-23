// ============================================================
// WarungScout 根组件
// ============================================================

import React, { useState } from 'react'
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Store, 
  Download, 
  Settings, 
  Users, 
  Bell, 
  Search,
  ChevronDown,
  LogOut,
  User,
  Menu,
  X,
  Sparkles,
} from 'lucide-react'

// ============================================================
// 页面导入
// ============================================================

// 注意：这些页面组件将在后续创建
// 暂时使用占位符组件
const DashboardPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900">📊 总览</h1>
    <p className="text-gray-500 mt-2">销售作战室仪表板</p>
  </div>
)

const WarungListPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900">📋 Warung 列表</h1>
    <p className="text-gray-500 mt-2">查看和管理所有 Warung</p>
  </div>
)

const ImportPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900">📥 数据抓取</h1>
    <p className="text-gray-500 mt-2">从 Google Maps 抓取 Warung 数据</p>
  </div>
)

const SettingsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900">⚙️ 设置</h1>
    <p className="text-gray-500 mt-2">系统配置</p>
  </div>
)

// ============================================================
// 导航配置
// ============================================================

interface NavItem {
  path: string
  label: string
  icon: React.ReactNode
}

const NAV_ITEMS: NavItem[] = [
  { path: '/', label: '总览', icon: <LayoutDashboard className="w-5 h-5" /> },
  { path: '/warungs', label: 'Warung 列表', icon: <Store className="w-5 h-5" /> },
  { path: '/import', label: '数据抓取', icon: <Download className="w-5 h-5" /> },
  { path: '/settings', label: '设置', icon: <Settings className="w-5 h-5" /> },
]

// ============================================================
// 布局组件
// ============================================================

interface LayoutProps {
  children: React.ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ============================================
      侧边栏
      ============================================ */}
      <aside
        className={`
          fixed top-0 left-0 z-40 h-full w-64 bg-white border-r border-gray-200
          transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-2 px-6 h-16 border-b border-gray-100">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">🏪</span>
          </div>
          <span className="text-lg font-bold text-gray-900">WarungScout</span>
          <span className="ml-auto text-xs text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">v1.0</span>
        </div>

        {/* 导航菜单 */}
        <nav className="p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path))
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium
                  transition-colors duration-150
                  ${isActive 
                    ? 'bg-primary-50 text-primary-700' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                {item.icon}
                {item.label}
                {isActive && (
                  <span className="ml-auto w-1.5 h-6 rounded-full bg-primary-500" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* 底部：用户信息 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100">
          <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
              JD
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">John Doe</p>
              <p className="text-xs text-gray-500 truncate">销售团队</p>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </aside>

      {/* ============================================
      主内容
      ============================================ */}
      <main className={`
        transition-all duration-300 ease-in-out
        ${sidebarOpen ? 'lg:ml-64' : 'ml-0'}
      `}>
        {/* 顶部导航栏 */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 h-16">
            <div className="flex items-center gap-4">
              {/* 移动端菜单按钮 */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-600"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>

              {/* 面包屑/标题 */}
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  {NAV_ITEMS.find(item => item.path === location.pathname)?.label || '总览'}
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* 搜索 */}
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-500">
                <Search className="w-4 h-4" />
                <span>搜索 Warung...</span>
                <kbd className="px-1.5 py-0.5 text-xs bg-white rounded border border-gray-200">⌘K</kbd>
              </div>

              {/* 通知 */}
              <button className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-600">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
              </button>

              {/* AI 助手按钮 */}
              <button className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white text-sm font-medium rounded-lg hover:from-primary-600 hover:to-primary-700 transition-colors">
                <Sparkles className="w-4 h-4" />
                AI 建议
              </button>
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <div className="p-6">
          {children}
        </div>
      </main>

      {/* 移动端遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

// ============================================================
// App 根组件
// ============================================================

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/warungs" element={<WarungListPage />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
