// ============================================================
// WarungScout 设置页面
// 功能: 系统配置、评分权重调整、API 设置
// ============================================================

import React, { useState } from 'react'
import {
  Settings,
  Save,
  RefreshCw,
  Key,
  Database,
  Sliders,
  Bell,
  User,
  Globe,
  Shield,
  HelpCircle,
  LogOut,
  Check,
  X,
  AlertCircle,
  Info,
  ChevronRight,
  Moon,
  Sun,
  Monitor,
} from 'lucide-react'

// ============================================================
// 类型定义
// ============================================================

interface WeightConfig {
  id: string
  name: string
  description: string
  value: number
  min: number
  max: number
  step: number
}

interface ApiConfig {
  id: string
  name: string
  status: 'configured' | 'not_configured' | 'error'
  key: string
  maskedKey: string
}

// ============================================================
// 模拟数据
// ============================================================

const MOCK_WEIGHTS: WeightConfig[] = [
  { id: 'location', name: '地理位置价值', description: '周边设施、商圈热度', value: 25, min: 5, max: 40, step: 1 },
  { id: 'activity', name: '店主活跃度', description: 'WA 活跃、响应速度', value: 20, min: 5, max: 35, step: 1 },
  { id: 'competition', name: '竞争密度', description: '500m 内竞品数量', value: 15, min: 5, max: 30, step: 1 },
  { id: 'cooperation', name: '配合度', description: '历史配合程度', value: 15, min: 5, max: 25, step: 1 },
  { id: 'digital', name: '数字化接受度', description: '数字支付、WA 使用', value: 15, min: 5, max: 25, step: 1 },
  { id: 'owner', name: '店主画像', description: '年龄、学历、经营年限', value: 5, min: 0, max: 15, step: 0.5 },
  { id: 'region', name: '区域潜力', description: '城市 Tier 分级', value: 5, min: 0, max: 10, step: 0.5 },
]

const MOCK_APIS: ApiConfig[] = [
  {
    id: 'serpapi',
    name: 'SerpApi',
    status: 'configured',
    key: 'sk_live_xxxxxxxxxxxxxxxxxxxx',
    maskedKey: 'sk_live_••••••••••••••••••••',
  },
  {
    id: 'places_api',
    name: 'Google Places API',
    status: 'error',
    key: '',
    maskedKey: '未配置',
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp Business API',
    status: 'not_configured',
    key: '',
    maskedKey: '未配置',
  },
]

// ============================================================
// 组件
// ============================================================

function ApiStatusBadge({ status }: { status: ApiConfig['status'] }) {
  const configs = {
    configured: { label: '已配置', icon: <Check className="w-3.5 h-3.5" />, className: 'bg-emerald-100 text-emerald-700' },
    not_configured: { label: '未配置', icon: <X className="w-3.5 h-3.5" />, className: 'bg-gray-100 text-gray-500' },
    error: { label: '异常', icon: <AlertCircle className="w-3.5 h-3.5" />, className: 'bg-red-100 text-red-700' },
  }
  const config = configs[status]
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.icon} {config.label}
    </span>
  )
}

// ============================================================
// 主组件
// ============================================================

export default function SettingsPage() {
  const [weights, setWeights] = useState<WeightConfig[]>(MOCK_WEIGHTS)
  const [apis] = useState<ApiConfig[]>(MOCK_APIS)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system')
  const [notifications, setNotifications] = useState({
    taskReminder: true,
    scoreUpdate: true,
    importComplete: true,
    weeklyReport: false,
  })

  // 权重更新
  const updateWeight = (id: string, value: number) => {
    setWeights(weights.map((w) => (w.id === id ? { ...w, value: Math.round(value * 10) / 10 } : w)))
  }

  // 重置权重
  const resetWeights = () => {
    setWeights(MOCK_WEIGHTS)
  }

  // 检查权重总和
  const totalWeight = weights.reduce((sum, w) => sum + w.value, 0)
  const isValidWeight = Math.abs(totalWeight - 100) < 0.1

  // 保存设置
  const handleSave = async () => {
    setIsSaving(true)
    setSaveSuccess(false)
    await new Promise((resolve) => setTimeout(resolve, 1500))
    setIsSaving(false)
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  return (
    <div>
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">⚙️ 设置</h1>
          <p className="text-gray-500 text-sm mt-0.5">系统配置、评分权重与 API 管理</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={resetWeights}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            重置
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !isValidWeight}
            className="flex items-center gap-1.5 px-4 py-2 text-sm text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                保存中...
              </>
            ) : saveSuccess ? (
              <>
                <Check className="w-4 h-4" />
                已保存
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                保存设置
              </>
            )}
          </button>
        </div>
      </div>

      {/* 保存提示 */}
      {!isValidWeight && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">权重总和必须等于 100%</p>
            <p className="text-sm text-amber-700">当前总和: {totalWeight}%</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 主设置区域 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 评分权重配置 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Sliders className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">评分权重配置</h2>
                <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                  {totalWeight}%
                </span>
              </div>
              <span className={`text-xs font-medium ${isValidWeight ? 'text-emerald-600' : 'text-amber-600'}`}>
                {isValidWeight ? '✅ 权重平衡' : '⚠️ 请调整'}
              </span>
            </div>

            <div className="p-6 space-y-4">
              {weights.map((weight) => (
                <div key={weight.id}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div>
                      <span className="text-sm font-medium text-gray-700">{weight.name}</span>
                      <span className="ml-2 text-xs text-gray-400">{weight.description}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 w-12 text-right">
                      {weight.value}%
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <input
                      type="range"
                      min={weight.min}
                      max={weight.max}
                      step={weight.step}
                      value={weight.value}
                      onChange={(e) => updateWeight(weight.id, parseFloat(e.target.value))}
                      className="flex-1 h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary-600"
                    />
                    <span className="text-xs text-gray-400 w-8 text-right">
                      {weight.min}%
                    </span>
                  </div>
                </div>
              ))}

              <div className="pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">权重总和</span>
                  <span className={`font-semibold ${isValidWeight ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {totalWeight}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* API 配置 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Key className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">API 配置</h2>
              </div>
              <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                管理 →
              </button>
            </div>

            <div className="p-6 space-y-4">
              {apis.map((api) => (
                <div key={api.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-500">
                      {api.id === 'serpapi' && <Globe className="w-4 h-4" />}
                      {api.id === 'places_api' && <MapPin className="w-4 h-4" />}
                      {api.id === 'whatsapp' && <Bell className="w-4 h-4" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{api.name}</p>
                      <p className="text-xs text-gray-400">{api.maskedKey}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <ApiStatusBadge status={api.status} />
                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                      {api.status === 'configured' ? '更新' : '配置'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 数据管理 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">数据管理</h2>
              </div>
            </div>

            <div className="p-6 space-y-3">
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-gray-700">导出数据</p>
                  <p className="text-xs text-gray-400">导出为 CSV / JSON 格式</p>
                </div>
                <button className="px-4 py-1.5 text-sm text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors">
                  导出
                </button>
              </div>
              <div className="flex items-center justify-between py-2 border-t border-gray-50">
                <div>
                  <p className="text-sm font-medium text-gray-700">导入数据</p>
                  <p className="text-xs text-gray-400">从 CSV / JSON 文件导入</p>
                </div>
                <button className="px-4 py-1.5 text-sm text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors">
                  导入
                </button>
              </div>
              <div className="flex items-center justify-between py-2 border-t border-gray-50">
                <div>
                  <p className="text-sm font-medium text-gray-700">清除所有数据</p>
                  <p className="text-xs text-red-400">此操作不可撤销</p>
                </div>
                <button className="px-4 py-1.5 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors">
                  清除
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 侧边设置 */}
        <div className="space-y-6">
          {/* 主题设置 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Monitor className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">主题</h2>
              </div>
            </div>
            <div className="p-4 space-y-2">
              <button
                onClick={() => setTheme('light')}
                className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg border transition-colors ${
                  theme === 'light' ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Sun className="w-4 h-4" />
                <span className="text-sm font-medium">浅色</span>
                {theme === 'light' && <Check className="w-4 h-4 ml-auto text-primary-600" />}
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg border transition-colors ${
                  theme === 'dark' ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Moon className="w-4 h-4" />
                <span className="text-sm font-medium">深色</span>
                {theme === 'dark' && <Check className="w-4 h-4 ml-auto text-primary-600" />}
              </button>
              <button
                onClick={() => setTheme('system')}
                className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg border transition-colors ${
                  theme === 'system' ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span className="text-sm font-medium">跟随系统</span>
                {theme === 'system' && <Check className="w-4 h-4 ml-auto text-primary-600" />}
              </button>
            </div>
          </div>

          {/* 通知设置 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">通知</h2>
              </div>
            </div>
            <div className="p-4 space-y-3">
              {Object.entries(notifications).map(([key, value]) => (
                <label key={key} className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-gray-700">
                    {key === 'taskReminder' && '任务提醒'}
                    {key === 'scoreUpdate' && '评分更新通知'}
                    {key === 'importComplete' && '抓取完成通知'}
                    {key === 'weeklyReport' && '周报'}
                  </span>
                  <div
                    onClick={() => setNotifications({ ...notifications, [key]: !value })}
                    className={`relative w-10 h-5 rounded-full transition-colors cursor-pointer ${
                      value ? 'bg-primary-600' : 'bg-gray-300'
                    }`}
                  >
                    <div
                      className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
                        value ? 'translate-x-5' : 'translate-x-0.5'
                      }`}
                    />
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* 帮助与支持 */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-gray-500" />
                <h2 className="font-semibold text-gray-900">帮助与支持</h2>
              </div>
            </div>
            <div className="p-2">
              <a
                href="#"
                className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
                  <User className="w-4 h-4" />
                </div>
                <span className="text-sm text-gray-700">文档与指南</span>
                <ChevronRight className="w-4 h-4 ml-auto text-gray-400" />
              </a>
              <a
                href="#"
                className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
                  <Shield className="w-4 h-4" />
                </div>
                <span className="text-sm text-gray-700">隐私与安全</span>
                <ChevronRight className="w-4 h-4 ml-auto text-gray-400" />
              </a>
              <button className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg hover:bg-red-50 transition-colors text-red-600">
                <div className="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center text-red-500">
                  <LogOut className="w-4 h-4" />
                </div>
                <span className="text-sm font-medium">退出登录</span>
                <ChevronRight className="w-4 h-4 ml-auto text-red-300" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ============================================================
// 辅助组件
// ============================================================

function MapPin(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}
