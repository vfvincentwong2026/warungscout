// ============================================================
// WarungScout 数据抓取页面
// 功能: 从 Google Maps 抓取 Warung 数据
// ============================================================

import React, { useState } from 'react'
import {
  Download,
  Search,
  MapPin,
  Globe,
  Settings,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Trash2,
  RefreshCw,
  Eye,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'

// ============================================================
// 类型定义
// ============================================================

interface ImportTask {
  id: string
  query: string
  location: string
  maxResults: number
  sourceType: 'serpapi' | 'places_api' | 'playwright'
  status: 'pending' | 'running' | 'completed' | 'failed'
  totalFound: number
  totalImported: number
  startedAt: string
  completedAt?: string
  errorMessage?: string
}

interface ImportFormData {
  query: string
  location: string
  maxResults: number
  sourceType: 'serpapi' | 'places_api' | 'playwright'
}

// ============================================================
// 模拟数据
// ============================================================

const MOCK_TASKS: ImportTask[] = [
  {
    id: '1',
    query: 'warung Jakarta',
    location: '-6.2088,106.8456,14z',
    maxResults: 100,
    sourceType: 'serpapi',
    status: 'completed',
    totalFound: 52,
    totalImported: 48,
    startedAt: '2026-08-21 14:30',
    completedAt: '2026-08-21 14:32',
  },
  {
    id: '2',
    query: 'warung Bali',
    location: '-8.3405,115.0920,14z',
    maxResults: 50,
    sourceType: 'serpapi',
    status: 'completed',
    totalFound: 37,
    totalImported: 35,
    startedAt: '2026-08-21 10:00',
    completedAt: '2026-08-21 10:02',
  },
  {
    id: '3',
    query: 'warung Medan',
    location: '3.5952,98.6722,14z',
    maxResults: 50,
    sourceType: 'places_api',
    status: 'failed',
    totalFound: 0,
    totalImported: 0,
    startedAt: '2026-08-20 16:00',
    errorMessage: 'API Key 无效或已过期',
  },
  {
    id: '4',
    query: 'warung Bandung',
    location: '-6.9175,107.6191,14z',
    maxResults: 50,
    sourceType: 'serpapi',
    status: 'completed',
    totalFound: 29,
    totalImported: 28,
    startedAt: '2026-08-20 09:00',
    completedAt: '2026-08-20 09:01',
  },
  {
    id: '5',
    query: 'warung Surabaya',
    location: '-7.2575,112.7521,14z',
    maxResults: 80,
    sourceType: 'playwright',
    status: 'running',
    totalFound: 15,
    totalImported: 10,
    startedAt: '2026-08-22 09:00',
  },
]

// ============================================================
// 预置搜索词库
// ============================================================

const PRESET_QUERIES = [
  { label: 'Jakarta', query: 'warung Jakarta', location: '-6.2088,106.8456,14z' },
  { label: 'Surabaya', query: 'warung Surabaya', location: '-7.2575,112.7521,14z' },
  { label: 'Bali', query: 'warung Bali', location: '-8.3405,115.0920,14z' },
  { label: 'Bandung', query: 'warung Bandung', location: '-6.9175,107.6191,14z' },
  { label: 'Medan', query: 'warung Medan', location: '3.5952,98.6722,14z' },
  { label: 'Yogyakarta', query: 'warung Yogyakarta', location: '-7.7956,110.3695,14z' },
]

// ============================================================
// 组件
// ============================================================

function StatusBadge({ status }: { status: ImportTask['status'] }) {
  const configs = {
    pending: { label: '等待中', icon: <Clock className="w-3.5 h-3.5" />, className: 'bg-gray-100 text-gray-600' },
    running: { label: '抓取中', icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />, className: 'bg-blue-100 text-blue-700' },
    completed: { label: '已完成', icon: <CheckCircle className="w-3.5 h-3.5" />, className: 'bg-emerald-100 text-emerald-700' },
    failed: { label: '失败', icon: <XCircle className="w-3.5 h-3.5" />, className: 'bg-red-100 text-red-700' },
  }
  const config = configs[status]
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.className}`}>
      {config.icon} {config.label}
    </span>
  )
}

function SourceTypeBadge({ type }: { type: ImportTask['sourceType'] }) {
  const configs = {
    serpapi: { label: 'SerpApi', color: 'bg-purple-100 text-purple-700' },
    places_api: { label: 'Places API', color: 'bg-blue-100 text-blue-700' },
    playwright: { label: 'Playwright', color: 'bg-amber-100 text-amber-700' },
  }
  const config = configs[type]
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const percentage = max > 0 ? Math.min((value / max) * 100, 100) : 0
  return (
    <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
      <div
        className="h-full bg-primary-500 rounded-full transition-all duration-500"
        style={{ width: `${percentage}%` }}
      />
    </div>
  )
}

// ============================================================
// 主组件
// ============================================================

export default function Import() {
  const [tasks] = useState<ImportTask[]>(MOCK_TASKS)
  const [formData, setFormData] = useState<ImportFormData>({
    query: '',
    location: '',
    maxResults: 100,
    sourceType: 'serpapi',
  })
  const [isImporting, setIsImporting] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)

  // 处理预置词库选择
  const handlePresetSelect = (preset: typeof PRESET_QUERIES[0]) => {
    setSelectedPreset(preset.label)
    setFormData({
      ...formData,
      query: preset.query,
      location: preset.location,
    })
  }

  // 处理提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.query.trim()) return

    setIsImporting(true)

    // 模拟抓取过程
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // 模拟成功
    setIsImporting(false)
    // 这里可以添加成功提示
    // 实际调用 API: POST /api/import/google-maps
  }

  // 统计
  const stats = {
    total: tasks.length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    running: tasks.filter((t) => t.status === 'running').length,
    failed: tasks.filter((t) => t.status === 'failed').length,
    totalImported: tasks.reduce((sum, t) => sum + t.totalImported, 0),
  }

  return (
    <div>
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">📥 数据抓取</h1>
          <p className="text-gray-500 text-sm mt-0.5">从 Google Maps 自动抓取 Warung 数据，支持批量导入</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <RefreshCw className="w-4 h-4" />
            刷新
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">总任务</p>
          <p className="text-xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border border-emerald-200 px-4 py-3 bg-emerald-50/50">
          <p className="text-xs text-emerald-600">已完成</p>
          <p className="text-xl font-bold text-emerald-700">{stats.completed}</p>
        </div>
        <div className="bg-white rounded-xl border border-blue-200 px-4 py-3 bg-blue-50/50">
          <p className="text-xs text-blue-600">运行中</p>
          <p className="text-xl font-bold text-blue-700">{stats.running}</p>
        </div>
        <div className="bg-white rounded-xl border border-red-200 px-4 py-3 bg-red-50/50">
          <p className="text-xs text-red-600">失败</p>
          <p className="text-xl font-bold text-red-700">{stats.failed}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">已导入</p>
          <p className="text-xl font-bold text-gray-900">{stats.totalImported}</p>
        </div>
      </div>

      {/* 抓取表单 */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">🔄 触发新抓取</h2>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 搜索关键词 */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                搜索关键词 <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={formData.query}
                  onChange={(e) => setFormData({ ...formData, query: e.target.value })}
                  placeholder="例如: warung Jakarta"
                  className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors"
                  required
                />
              </div>
            </div>

            {/* 最大数量 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                最大数量
              </label>
              <input
                type="number"
                value={formData.maxResults}
                onChange={(e) => setFormData({ ...formData, maxResults: parseInt(e.target.value) || 100 })}
                min={10}
                max={500}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {/* 位置坐标 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                位置坐标 (可选)
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="如: -6.2088,106.8456,14z"
                  className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>

            {/* 数据来源 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                数据来源
              </label>
              <select
                value={formData.sourceType}
                onChange={(e) => setFormData({ ...formData, sourceType: e.target.value as ImportFormData['sourceType'] })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors"
              >
                <option value="serpapi">SerpApi (推荐)</option>
                <option value="places_api">Google Places API</option>
                <option value="playwright">Playwright (自建爬虫)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={isImporting || !formData.query.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-2.5 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isImporting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    抓取中...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    开始抓取
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* 预置词库 */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-500 mb-2">快速选择预置关键词：</p>
          <div className="flex flex-wrap gap-2">
            {PRESET_QUERIES.map((preset) => (
              <button
                key={preset.label}
                onClick={() => handlePresetSelect(preset)}
                className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                  selectedPreset === preset.label
                    ? 'bg-primary-50 border-primary-300 text-primary-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300'
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            <Info className="w-3 h-3 inline mr-0.5" />
            点击关键词自动填入搜索框
          </p>
        </div>
      </div>

      {/* 抓取任务列表 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <h2 className="font-semibold text-gray-900">抓取任务历史</h2>
            <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
              {tasks.length}
            </span>
          </div>
          <button className="text-sm text-gray-400 hover:text-gray-600">
            查看更多 →
          </button>
        </div>

        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-sm">暂无抓取任务</p>
            <p className="text-xs">使用上方表单开始抓取</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {tasks.map((task) => (
              <div key={task.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-gray-900">{task.query}</span>
                      <SourceTypeBadge type={task.sourceType} />
                      <StatusBadge status={task.status} />
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500 flex-wrap">
                      <span>📍 {task.location || '默认'}</span>
                      <span>🎯 {task.maxResults} 条</span>
                      <span>📊 找到 {task.totalFound} 条</span>
                      <span>✅ 导入 {task.totalImported} 条</span>
                      <span className="text-gray-400">🕐 {task.startedAt}</span>
                    </div>
                    {task.errorMessage && (
                      <div className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {task.errorMessage}
                      </div>
                    )}
                    {task.status === 'running' && (
                      <div className="mt-2">
                        <ProgressBar value={task.totalImported} max={task.maxResults} />
                        <p className="text-xs text-gray-400 mt-0.5">
                          已导入 {task.totalImported} / {task.maxResults} 条
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {task.status === 'completed' && (
                      <button className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                    )}
                    {task.status === 'failed' && (
                      <button className="p-1.5 text-primary-600 hover:text-primary-700 rounded-lg hover:bg-primary-50 transition-colors">
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    )}
                    <button className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
