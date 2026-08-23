// ============================================================
// WarungScout Warung 列表页面
// 功能: 展示、筛选、排序、搜索 Warung 列表
// ============================================================

import React, { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  Store,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Eye,
  MessageCircle,
  Phone,
  Users,
  MapPin,
  Star,
  Download,
  RefreshCw,
  X,
  Check,
  AlertCircle,
} from 'lucide-react'

// ============================================================
// 类型定义
// ============================================================

interface Warung {
  id: string
  name: string
  phone: string
  address: string
  city: string
  region: string
  source: 'google_maps' | 'manual' | 'api'
  score: number
  grade: 'gold' | 'silver' | 'potential' | 'normal'
  step: number
  stepName: string
  lastContactAt?: string
  nextActionAt?: string
  createdAt: string
}

interface FilterState {
  grade: string
  step: string
  source: string
  region: string
  search: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

// ============================================================
// 模拟数据
// ============================================================

const MOCK_WARUNGS: Warung[] = [
  {
    id: '1',
    name: 'Warung Bu Siti',
    phone: '+62 812-3456-7890',
    address: 'Jl. Raya Canggu No. 45',
    city: 'Bali',
    region: 'Canggu',
    source: 'google_maps',
    score: 87,
    grade: 'gold',
    step: 2,
    stepName: '拜访',
    lastContactAt: '2026-08-20',
    nextActionAt: '2026-08-23',
    createdAt: '2026-08-15',
  },
  {
    id: '2',
    name: 'Warung Pak Made',
    phone: '+62 813-4567-8901',
    address: 'Jl. Sudirman No. 12',
    city: 'Jakarta',
    region: 'Selatan',
    source: 'google_maps',
    score: 82,
    grade: 'gold',
    step: 1,
    stepName: '破冰',
    lastContactAt: '2026-08-21',
    nextActionAt: '2026-08-24',
    createdAt: '2026-08-14',
  },
  {
    id: '3',
    name: 'Warung Bu Dewi',
    phone: '+62 814-5678-9012',
    address: 'Jl. Pemuda No. 8',
    city: 'Surabaya',
    region: 'Kota',
    source: 'manual',
    score: 75,
    grade: 'silver',
    step: 0,
    stepName: '未接触',
    lastContactAt: null,
    nextActionAt: null,
    createdAt: '2026-08-10',
  },
  {
    id: '4',
    name: 'Warung Pak Agus',
    phone: '+62 815-6789-0123',
    address: 'Jl. Asia Afrika No. 23',
    city: 'Bandung',
    region: 'Kota',
    source: 'google_maps',
    score: 55,
    grade: 'potential',
    step: 3,
    stepName: '推品',
    lastContactAt: '2026-08-18',
    nextActionAt: '2026-08-25',
    createdAt: '2026-08-12',
  },
  {
    id: '5',
    name: 'Warung Bu Rini',
    phone: '+62 816-7890-1234',
    address: 'Jl. Veteran No. 5',
    city: 'Medan',
    region: 'Kota',
    source: 'manual',
    score: 38,
    grade: 'normal',
    step: 0,
    stepName: '未接触',
    lastContactAt: null,
    nextActionAt: null,
    createdAt: '2026-08-08',
  },
  {
    id: '6',
    name: 'Warung Pak Wayan',
    phone: '+62 817-8901-2345',
    address: 'Jl. Sunset Road No. 100',
    city: 'Bali',
    region: 'Kuta',
    source: 'google_maps',
    score: 92,
    grade: 'gold',
    step: 4,
    stepName: '深度合作',
    lastContactAt: '2026-08-19',
    nextActionAt: '2026-08-26',
    createdAt: '2026-08-01',
  },
  {
    id: '7',
    name: 'Warung Bu Nita',
    phone: '+62 818-9012-3456',
    address: 'Jl. Diponegoro No. 15',
    city: 'Yogyakarta',
    region: 'Kota',
    source: 'manual',
    score: 68,
    grade: 'silver',
    step: 2,
    stepName: '拜访',
    lastContactAt: '2026-08-17',
    nextActionAt: '2026-08-22',
    createdAt: '2026-08-05',
  },
  {
    id: '8',
    name: 'Warung Pak Budi',
    phone: '+62 819-0123-4567',
    address: 'Jl. Ahmad Yani No. 32',
    city: 'Semarang',
    region: 'Kota',
    source: 'google_maps',
    score: 45,
    grade: 'potential',
    step: 1,
    stepName: '破冰',
    lastContactAt: '2026-08-16',
    nextActionAt: '2026-08-21',
    createdAt: '2026-08-09',
  },
]

// ============================================================
// 辅助函数
// ============================================================

const gradeConfig = {
  gold: { label: '黄金', emoji: '🔴', bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200' },
  silver: { label: '白银', emoji: '🟡', bg: 'bg-gray-200', text: 'text-gray-700', border: 'border-gray-300' },
  potential: { label: '潜力', emoji: '🟢', bg: 'bg-emerald-100', text: 'text-emerald-800', border: 'border-emerald-200' },
  normal: { label: '普通', emoji: '⚪', bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' },
}

const sourceConfig = {
  google_maps: { label: 'Google Maps', icon: '🌐' },
  manual: { label: '人工录入', icon: '📝' },
  api: { label: 'API 导入', icon: '🔌' },
}

const stepNames = ['未接触', '破冰', '拜访', '推品', '深度合作', '长期运营']

const cities = ['全部', 'Jakarta', 'Surabaya', 'Bandung', 'Bali', 'Medan', 'Yogyakarta', 'Semarang']

// ============================================================
// 组件
// ============================================================

function GradeBadge({ grade }: { grade: Warung['grade'] }) {
  const config = gradeConfig[grade]
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text} border ${config.border}`}>
      {config.emoji} {config.label}
    </span>
  )
}

function SourceBadge({ source }: { source: Warung['source'] }) {
  const config = sourceConfig[source]
  return (
    <span className="inline-flex items-center gap-1 text-xs text-gray-500">
      {config.icon} {config.label}
    </span>
  )
}

function StepBadge({ step }: { step: number }) {
  const name = stepNames[step] || '未知'
  const colors = [
    'bg-gray-100 text-gray-600',
    'bg-blue-100 text-blue-700',
    'bg-amber-100 text-amber-700',
    'bg-purple-100 text-purple-700',
    'bg-emerald-100 text-emerald-700',
    'bg-green-100 text-green-700',
  ]
  const color = colors[step] || colors[0]
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {name}
    </span>
  )
}

function ScoreBar({ score }: { score: number }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'bg-amber-500'
    if (s >= 60) return 'bg-gray-400'
    if (s >= 40) return 'bg-emerald-500'
    return 'bg-gray-300'
  }

  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${getColor(score)} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-900 w-8">{score}</span>
    </div>
  )
}

// ============================================================
// 主组件
// ============================================================

export default function WarungList() {
  const [warungs] = useState<Warung[]>(MOCK_WARUNGS)
  const [filters, setFilters] = useState<FilterState>({
    grade: 'all',
    step: 'all',
    source: 'all',
    region: 'all',
    search: '',
    sortBy: 'score',
    sortOrder: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)

  // ============================================================
  // 筛选逻辑
  // ============================================================

  const filteredWarungs = useMemo(() => {
    let result = [...warungs]

    // 搜索
    if (filters.search) {
      const query = filters.search.toLowerCase()
      result = result.filter(
        (w) =>
          w.name.toLowerCase().includes(query) ||
          w.phone.includes(query) ||
          w.city.toLowerCase().includes(query) ||
          w.address.toLowerCase().includes(query)
      )
    }

    // 等级
    if (filters.grade !== 'all') {
      result = result.filter((w) => w.grade === filters.grade)
    }

    // 步骤
    if (filters.step !== 'all') {
      result = result.filter((w) => w.step === parseInt(filters.step))
    }

    // 来源
    if (filters.source !== 'all') {
      result = result.filter((w) => w.source === filters.source)
    }

    // 区域
    if (filters.region !== 'all') {
      result = result.filter((w) => w.city === filters.region)
    }

    // 排序
    result.sort((a, b) => {
      let aVal: any = a[filters.sortBy as keyof Warung]
      let bVal: any = b[filters.sortBy as keyof Warung]

      if (filters.sortBy === 'score') {
        aVal = a.score
        bVal = b.score
      } else if (filters.sortBy === 'name') {
        aVal = a.name
        bVal = b.name
      } else if (filters.sortBy === 'createdAt') {
        aVal = new Date(a.createdAt).getTime()
        bVal = new Date(b.createdAt).getTime()
      }

      if (aVal < bVal) return filters.sortOrder === 'asc' ? -1 : 1
      if (aVal > bVal) return filters.sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return result
  }, [warungs, filters])

  // ============================================================
  // 统计
  // ============================================================

  const stats = useMemo(() => {
    const total = warungs.length
    const gold = warungs.filter((w) => w.grade === 'gold').length
    const silver = warungs.filter((w) => w.grade === 'silver').length
    const potential = warungs.filter((w) => w.grade === 'potential').length
    const normal = warungs.filter((w) => w.grade === 'normal').length
    const fromGmaps = warungs.filter((w) => w.source === 'google_maps').length
    const avgScore = Math.round(warungs.reduce((sum, w) => sum + w.score, 0) / total)
    return { total, gold, silver, potential, normal, fromGmaps, avgScore }
  }, [warungs])

  // ============================================================
  // 渲染
  // ============================================================

  return (
    <div>
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">📋 Warung 列表</h1>
          <p className="text-gray-500 text-sm mt-0.5">管理所有 Warung 线索，查看评分和跟进状态</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-4 h-4" />
            导出
          </button>
          <button className="flex items-center gap-1.5 px-3 py-2 text-sm text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors">
            <Store className="w-4 h-4" />
            新增 Warung
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">总计</p>
          <p className="text-xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border border-amber-200 px-4 py-3 bg-amber-50/50">
          <p className="text-xs text-amber-600">黄金</p>
          <p className="text-xl font-bold text-amber-700">{stats.gold}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">白银</p>
          <p className="text-xl font-bold text-gray-700">{stats.silver}</p>
        </div>
        <div className="bg-white rounded-xl border border-emerald-200 px-4 py-3 bg-emerald-50/50">
          <p className="text-xs text-emerald-600">潜力</p>
          <p className="text-xl font-bold text-emerald-700">{stats.potential}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">🌐 地图</p>
          <p className="text-xl font-bold text-gray-700">{stats.fromGmaps}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
          <p className="text-xs text-gray-500">平均分</p>
          <p className="text-xl font-bold text-gray-900">{stats.avgScore}</p>
        </div>
      </div>

      {/* 搜索和筛选栏 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* 搜索框 */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索 Warung 名称、电话、城市..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors text-sm"
            />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-4 py-2 text-sm border rounded-lg transition-colors ${
                showFilters
                  ? 'bg-primary-50 border-primary-200 text-primary-700'
                  : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-4 h-4" />
              筛选
              <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>

            <button
              onClick={() => {
                setFilters({
                  grade: 'all',
                  step: 'all',
                  source: 'all',
                  region: 'all',
                  search: '',
                  sortBy: 'score',
                  sortOrder: 'desc',
                })
                setShowFilters(false)
              }}
              className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              重置
            </button>
          </div>
        </div>

        {/* 筛选展开区域 */}
        {showFilters && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 pt-4 border-t border-gray-100">
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">等级</label>
              <select
                value={filters.grade}
                onChange={(e) => setFilters({ ...filters, grade: e.target.value })}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              >
                <option value="all">全部</option>
                <option value="gold">黄金</option>
                <option value="silver">白银</option>
                <option value="potential">潜力</option>
                <option value="normal">普通</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">步骤</label>
              <select
                value={filters.step}
                onChange={(e) => setFilters({ ...filters, step: e.target.value })}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              >
                <option value="all">全部</option>
                {stepNames.map((name, i) => (
                  <option key={i} value={i}>{name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">来源</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({ ...filters, source: e.target.value })}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              >
                <option value="all">全部</option>
                <option value="google_maps">Google Maps</option>
                <option value="manual">人工录入</option>
                <option value="api">API 导入</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">城市</label>
              <select
                value={filters.region}
                onChange={(e) => setFilters({ ...filters, region: e.target.value })}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              >
                {cities.map((city) => (
                  <option key={city} value={city === '全部' ? 'all' : city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">排序</label>
              <div className="flex gap-1">
                <select
                  value={filters.sortBy}
                  onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                  className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                >
                  <option value="score">分数</option>
                  <option value="name">名称</option>
                  <option value="createdAt">时间</option>
                </select>
                <button
                  onClick={() => setFilters({ ...filters, sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc' })}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {filters.sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 结果统计 */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          共 <span className="font-medium text-gray-700">{filteredWarungs.length}</span> 条记录
          {filters.search && (
            <span className="ml-2 text-gray-400">(搜索: "{filters.search}")</span>
          )}
        </p>
        <button className="text-sm text-gray-400 hover:text-gray-600 flex items-center gap-1">
          <RefreshCw className="w-3 h-3" />
          刷新
        </button>
      </div>

      {/* 表格 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Warung</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">区域</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">来源</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">评分</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">等级</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">步骤</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">下一步</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredWarungs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-gray-400">
                    <div className="flex flex-col items-center gap-2">
                      <AlertCircle className="w-8 h-8" />
                      <p className="text-sm">没有找到匹配的 Warung</p>
                      <p className="text-xs">尝试调整筛选条件</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredWarungs.map((warung) => (
                  <tr key={warung.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">{warung.name}</p>
                        <p className="text-xs text-gray-400">{warung.phone}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-gray-700">{warung.city}</p>
                        <p className="text-xs text-gray-400">{warung.region}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <SourceBadge source={warung.source} />
                    </td>
                    <td className="px-4 py-3">
                      <ScoreBar score={warung.score} />
                    </td>
                    <td className="px-4 py-3">
                      <GradeBadge grade={warung.grade} />
                    </td>
                    <td className="px-4 py-3">
                      <StepBadge step={warung.step} />
                    </td>
                    <td className="px-4 py-3">
                      {warung.nextActionAt ? (
                        <span className="text-xs text-gray-500">⏰ {warung.nextActionAt}</span>
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/warungs/${warung.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        查看
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 分页 */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-gray-500">
          显示 1-{Math.min(filteredWarungs.length, 10)} 条，共 {filteredWarungs.length} 条
        </p>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            上一页
          </button>
          <span className="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-lg">1</span>
          <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
            2
          </button>
          <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
            3
          </button>
          <span className="text-sm text-gray-400">...</span>
          <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
            下一页
          </button>
        </div>
      </div>
    </div>
  )
}
