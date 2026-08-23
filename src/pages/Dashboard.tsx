// ============================================================
// WarungScout 总览页面
// 功能: 销售作战室仪表板
// ============================================================

import React, { useState } from 'react'
import { 
  Store, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Clock,
  ChevronRight,
  Download,
  RefreshCw,
  Eye,
  MessageCircle,
  Phone,
  MapPin,
  Star,
  Sparkles,
} from 'lucide-react'

// ============================================================
// 类型定义
// ============================================================

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  change?: number
  changeLabel?: string
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red' | 'gray'
}

interface TaskItem {
  id: string
  warungName: string
  warungId: string
  action: string
  priority: 'high' | 'medium' | 'low'
  deadline: string
  channel: 'whatsapp' | 'visit' | 'call'
  avatar?: string
}

interface RecentActivity {
  id: string
  type: 'import' | 'score_change' | 'visit' | 'feedback' | 'task_done'
  warungName: string
  description: string
  time: string
}

// ============================================================
// 模拟数据
// ============================================================

const MOCK_STATS: StatCardProps[] = [
  { title: '总 Warung', value: 520, icon: <Store className="w-5 h-5" />, color: 'blue' },
  { title: '黄金 Warung', value: 78, icon: <Star className="w-5 h-5" />, color: 'yellow', change: 12, changeLabel: '较上周' },
  { title: '今日待办', value: 5, icon: <Clock className="w-5 h-5" />, color: 'purple', change: -2, changeLabel: '较昨日' },
  { title: '平均评分', value: 62, icon: <TrendingUp className="w-5 h-5" />, color: 'green', change: 3, changeLabel: '较上周' },
]

const MOCK_TASKS: TaskItem[] = [
  { id: '1', warungName: 'Warung Bu Siti', warungId: 'w1', action: 'WA 破冰联系', priority: 'high', deadline: '今日', channel: 'whatsapp' },
  { id: '2', warungName: 'Warung Pak Made', warungId: 'w2', action: '上门拜访', priority: 'high', deadline: '明日', channel: 'visit' },
  { id: '3', warungName: 'Warung Bu Dewi', warungId: 'w3', action: 'WA 跟进', priority: 'medium', deadline: '3 天后', channel: 'whatsapp' },
  { id: '4', warungName: 'Warung Pak Agus', warungId: 'w4', action: '推品确认', priority: 'medium', deadline: '5 天后', channel: 'visit' },
  { id: '5', warungName: 'Warung Bu Rini', warungId: 'w5', action: '初次联系', priority: 'low', deadline: '7 天后', channel: 'whatsapp' },
]

const MOCK_ACTIVITIES: RecentActivity[] = [
  { id: '1', type: 'import', warungName: 'Jakarta', description: '从 Google Maps 抓取 50 条新 Warung', time: '10 分钟前' },
  { id: '2', type: 'score_change', warungName: 'Warung Bu Siti', description: '评分更新: 72 → 87 (黄金)', time: '35 分钟前' },
  { id: '3', type: 'visit', warungName: 'Warung Pak Made', description: '完成首次拜访，沟通顺畅', time: '1 小时前' },
  { id: '4', type: 'feedback', warungName: 'Warung Bu Dewi', description: '提交反馈: 试销订单已确认', time: '2 小时前' },
  { id: '5', type: 'task_done', warungName: 'Warung Pak Agus', description: '完成 WA 破冰，已约访', time: '3 小时前' },
]

// ============================================================
// 统计卡片组件
// ============================================================

const colorMap = {
  blue: { bg: 'bg-blue-50', text: 'text-blue-600', iconBg: 'bg-blue-100' },
  green: { bg: 'bg-emerald-50', text: 'text-emerald-600', iconBg: 'bg-emerald-100' },
  yellow: { bg: 'bg-amber-50', text: 'text-amber-600', iconBg: 'bg-amber-100' },
  purple: { bg: 'bg-purple-50', text: 'text-purple-600', iconBg: 'bg-purple-100' },
  red: { bg: 'bg-red-50', text: 'text-red-600', iconBg: 'bg-red-100' },
  gray: { bg: 'bg-gray-50', text: 'text-gray-600', iconBg: 'bg-gray-100' },
}

function StatCard({ title, value, icon, change, changeLabel, color = 'blue' }: StatCardProps) {
  const colors = colorMap[color]
  const isPositive = change && change > 0
  const isNegative = change && change < 0

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div className={`${colors.iconBg} rounded-lg p-2.5`}>
          <div className={`${colors.text}`}>{icon}</div>
        </div>
        {change !== undefined && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${isPositive ? 'bg-emerald-50 text-emerald-600' : isNegative ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-500'}`}>
            {isPositive ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900 mt-3">{value}</p>
      <p className="text-sm text-gray-500">{title}</p>
      {changeLabel && (
        <p className="text-xs text-gray-400 mt-1">{changeLabel}</p>
      )}
    </div>
  )
}

// ============================================================
// 待办任务组件
// ============================================================

const priorityMap = {
  high: { label: '高', class: 'bg-red-100 text-red-700' },
  medium: { label: '中', class: 'bg-amber-100 text-amber-700' },
  low: { label: '低', class: 'bg-gray-100 text-gray-600' },
}

const channelMap = {
  whatsapp: { icon: <MessageCircle className="w-4 h-4" />, label: 'WA' },
  visit: { icon: <Users className="w-4 h-4" />, label: '拜访' },
  call: { icon: <Phone className="w-4 h-4" />, label: '电话' },
}

function TaskItem({ task }: { task: TaskItem }) {
  const priority = priorityMap[task.priority]
  const channel = channelMap[task.channel]

  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${priority.class}`}>
            {priority.label}
          </span>
          <span className="font-medium text-gray-900 truncate">{task.warungName}</span>
        </div>
        <div className="flex items-center gap-3 mt-0.5 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            {channel.icon}
            {channel.label}
          </span>
          <span>•</span>
          <span>{task.action}</span>
          <span>•</span>
          <span className="text-gray-400">⏰ {task.deadline}</span>
        </div>
      </div>
      <button className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
        处理
        <ChevronRight className="w-3 h-3" />
      </button>
    </div>
  )
}

// ============================================================
// 最近活动组件
// ============================================================

const activityIconMap = {
  import: { icon: <Download className="w-4 h-4" />, color: 'text-blue-500' },
  score_change: { icon: <TrendingUp className="w-4 h-4" />, color: 'text-amber-500' },
  visit: { icon: <Users className="w-4 h-4" />, color: 'text-emerald-500' },
  feedback: { icon: <MessageCircle className="w-4 h-4" />, color: 'text-purple-500' },
  task_done: { icon: <Check className="w-4 h-4" />, color: 'text-green-500' },
}

function ActivityItem({ activity }: { activity: RecentActivity }) {
  const iconInfo = activityIconMap[activity.type] || activityIconMap.import

  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-gray-100 last:border-0">
      <div className={`mt-0.5 ${iconInfo.color}`}>{iconInfo.icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-700">
          <span className="font-medium">{activity.warungName}</span>
          {' '}
          {activity.description}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">{activity.time}</p>
      </div>
    </div>
  )
}

// ============================================================
// 主组件
// ============================================================

export default function Dashboard() {
  const [stats] = useState(MOCK_STATS)
  const [tasks] = useState(MOCK_TASKS)
  const [activities] = useState(MOCK_ACTIVITIES)

  const highPriorityTasks = tasks.filter(t => t.priority === 'high')
  const todayTasks = tasks.filter(t => t.deadline === '今日' || t.deadline === '明日')

  return (
    <div>
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">📊 总览</h1>
          <p className="text-gray-500 text-sm mt-0.5">销售作战室仪表板，实时追踪 Warung 拓展进度</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <RefreshCw className="w-4 h-4" />
            刷新
          </button>
          <button className="flex items-center gap-1.5 px-3 py-2 text-sm text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors">
            <Sparkles className="w-4 h-4" />
            AI 分析报告
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 待办任务 */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-500" />
              <h2 className="font-semibold text-gray-900">今日待办</h2>
              <span className="px-2 py-0.5 text-xs font-medium bg-primary-50 text-primary-600 rounded-full">
                {todayTasks.length} 项
              </span>
            </div>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              查看全部 →
            </button>
          </div>

          <div className="divide-y divide-gray-100">
            {tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <div className="text-4xl mb-3">🎉</div>
                <p className="text-sm">今日暂无待办任务</p>
                <p className="text-xs">继续加油！</p>
              </div>
            ) : (
              tasks.map((task) => <TaskItem key={task.id} task={task} />)
            )}
          </div>
        </div>

        {/* 最近活动 */}
        <div className="bg-white rounded-xl border border-gray-200">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-gray-500" />
              <h2 className="font-semibold text-gray-900">最近动态</h2>
            </div>
            <button className="text-sm text-gray-400 hover:text-gray-600">
              全部 →
            </button>
          </div>

          <div className="px-4 py-2">
            {activities.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                <p className="text-sm">暂无动态</p>
              </div>
            ) : (
              activities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))
            )}
          </div>
        </div>
      </div>

      {/* 快速入口 */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <a
          href="/warungs"
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-200 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
            <Store className="w-5 h-5" />
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">Warung 列表</p>
            <p className="text-xs text-gray-400">管理所有线索</p>
          </div>
        </a>
        <a
          href="/import"
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-200 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
            <Download className="w-5 h-5" />
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">数据抓取</p>
            <p className="text-xs text-gray-400">导入新 Warung</p>
          </div>
        </a>
        <a
          href="#"
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-200 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">区域分析</p>
            <p className="text-xs text-gray-400">查看分布热力图</p>
          </div>
        </a>
        <a
          href="#"
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-200 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">AI 建议</p>
            <p className="text-xs text-gray-400">智能评分与推荐</p>
          </div>
        </a>
      </div>
    </div>
  )
}

// ============================================================
// 辅助组件
// ============================================================

function Check(props: React.SVGProps<SVGSVGElement>) {
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
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}
