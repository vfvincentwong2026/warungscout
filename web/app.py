# ============================================================
# WarungScout Web 界面 (Streamlit)
# 功能: 销售作战室 Dashboard
# 运行: streamlit run web/app.py
# 版本: v1.0.0
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import time

# ============================================================
# 1. 页面配置
# ============================================================

st.set_page_config(
    page_title="WarungScout 销售作战室",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. 样式
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .score-badge-gold {
        background: #fbbf24;
        color: #1f2937;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }
    .score-badge-silver {
        background: #9ca3af;
        color: #1f2937;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }
    .score-badge-potential {
        background: #34d399;
        color: #1f2937;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }
    .score-badge-normal {
        background: #d1d5db;
        color: #1f2937;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
    .priority-high {
        color: #dc2626;
        font-weight: 600;
    }
    .priority-medium {
        color: #f59e0b;
        font-weight: 600;
    }
    .priority-low {
        color: #6b7280;
        font-weight: 600;
    }
    .step-timeline {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: #6b7280;
    }
    .step-done {
        color: #10b981;
        font-weight: 600;
    }
    .step-active {
        color: #3b82f6;
        font-weight: 600;
    }
    .step-pending {
        color: #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. 模拟数据（后续替换为真实 API 调用）
# ============================================================

# 模拟统计数据
MOCK_STATS = {
    "total": 520,
    "gold_count": 78,
    "silver_count": 156,
    "potential_count": 186,
    "normal_count": 100,
    "from_google_maps": 320,
    "from_manual": 200,
    "avg_score": 62,
    "today_tasks": 5,
}

# 模拟待办任务
MOCK_TASKS = [
    {"id": "t1", "warung_name": "Warung Bu Siti", "action": "WA破冰", "priority": "high", "deadline": "今日", "channel": "whatsapp"},
    {"id": "t2", "warung_name": "Warung Pak Made", "action": "拜访", "priority": "high", "deadline": "明日", "channel": "visit"},
    {"id": "t3", "warung_name": "Warung Bu Dewi", "action": "WA跟进", "priority": "medium", "deadline": "3天后", "channel": "whatsapp"},
    {"id": "t4", "warung_name": "Warung Pak Agus", "action": "推品确认", "priority": "medium", "deadline": "5天后", "channel": "visit"},
    {"id": "t5", "warung_name": "Warung Bu Rini", "action": "初次联系", "priority": "low", "deadline": "7天后", "channel": "whatsapp"},
]

# 模拟 Warung 列表（前10条）
MOCK_WARUNGS = [
    {"id": "w1", "name": "Warung Bu Siti", "city": "Bali", "region": "Canggu", "score": 87, "grade": "gold", "step": 2, "step_name": "拜访", "source": "google_maps"},
    {"id": "w2", "name": "Warung Pak Made", "city": "Jakarta", "region": "Selatan", "score": 82, "grade": "gold", "step": 1, "step_name": "破冰", "source": "google_maps"},
    {"id": "w3", "name": "Warung Bu Dewi", "city": "Surabaya", "region": "Kota", "score": 75, "grade": "silver", "step": 0, "step_name": "未接触", "source": "manual"},
    {"id": "w4", "name": "Warung Pak Agus", "city": "Bandung", "region": "Kota", "score": 55, "grade": "potential", "step": 3, "step_name": "推品", "source": "google_maps"},
    {"id": "w5", "name": "Warung Bu Rini", "city": "Medan", "region": "Kota", "score": 38, "grade": "normal", "step": 0, "step_name": "未接触", "source": "manual"},
]

# ============================================================
# 4. API 调用函数（后续替换为真实 API）
# ============================================================

def get_stats():
    """获取统计数据"""
    # TODO: 替换为真实 API 调用
    # response = requests.get("http://localhost:8787/api/stats")
    # return response.json()
    return MOCK_STATS

def get_tasks():
    """获取待办任务"""
    # TODO: 替换为真实 API 调用
    # response = requests.get("http://localhost:8787/api/tasks")
    # return response.json()
    return MOCK_TASKS

def get_warungs():
    """获取 Warung 列表"""
    # TODO: 替换为真实 API 调用
    # response = requests.get("http://localhost:8787/api/warungs")
    # return response.json()
    return MOCK_WARUNGS

def get_warung_detail(warung_id: str):
    """获取 Warung 详情"""
    # TODO: 替换为真实 API 调用
    # response = requests.get(f"http://localhost:8787/api/warungs/{warung_id}")
    # return response.json()
    return None

def submit_feedback(warung_id: str, feedback_type: str, note: str = ""):
    """提交反馈"""
    # TODO: 替换为真实 API 调用
    # response = requests.post("http://localhost:8787/api/feedback", json={...})
    # return response.json()
    return {"success": True, "message": "反馈已提交"}

# ============================================================
# 5. 侧边栏
# ============================================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f2937/ffffff?text=🏪+WarungScout", use_container_width=True)
    st.markdown("---")

    # 导航
    nav = st.radio(
        "导航",
        ["📊 总览", "📋 Warung列表", "📥 数据抓取", "⚙️ 设置"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 用户信息
    st.caption("👤 销售团队")
    st.caption("📅 " + datetime.now().strftime("%Y-%m-%d %H:%M"))

# ============================================================
# 6. 页面内容
# ============================================================

if nav == "📊 总览":
    # ============================================================
    # 6.1 总览页面
    # ============================================================

    st.markdown('<p class="main-header">📊 销售作战室总览</p>', unsafe_allow_html=True)

    # 获取数据
    stats = get_stats()
    tasks = get_tasks()

    # 关键指标行
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("🏪 总 Warung", stats["total"])
    with col2:
        st.metric("🔴 黄金", stats["gold_count"])
    with col3:
        st.metric("🟡 白银", stats["silver_count"])
    with col4:
        st.metric("🟢 潜力", stats["potential_count"])
    with col5:
        st.metric("📈 平均分", stats["avg_score"])
    with col6:
        st.metric("📋 今日待办", stats["today_tasks"])

    st.markdown("---")

    # 待办任务 + 图表 两列布局
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("📋 今日待办")

        if tasks:
            for task in tasks:
                priority_class = {
                    "high": "priority-high",
                    "medium": "priority-medium",
                    "low": "priority-low",
                }.get(task.get("priority", "low"), "")

                channel_icon = "💬" if task.get("channel") == "whatsapp" else "🚶" if task.get("channel") == "visit" else "📞"

                with st.container():
                    c1, c2, c3, c4 = st.columns([0.6, 2.5, 1.2, 0.8])
                    with c1:
                        st.markdown(f'<span class="{priority_class}">●</span>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{task['warung_name']}**")
                    with c3:
                        st.caption(f"{channel_icon} {task['action']}")
                    with c4:
                        st.caption(f"⏰ {task['deadline']}")

                # 分割线
                if task != tasks[-1]:
                    st.divider()
        else:
            st.info("🎉 今日暂无待办任务！")

    with col2:
        st.subheader("📊 评分分布")

        # 创建饼图
        labels = ['黄金 (80-100)', '白银 (60-79)', '潜力 (40-59)', '普通 (<40)']
        values = [stats["gold_count"], stats["silver_count"], stats["potential_count"], stats["normal_count"]]
        colors = ['#fbbf24', '#9ca3af', '#34d399', '#d1d5db']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='inside',
            hole=0.4,
        )])
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 数据来源
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌐 Google Maps 抓取", stats["from_google_maps"])
    with col2:
        st.metric("📝 人工录入", stats["from_manual"])
    with col3:
        st.metric("📥 本周新增", "23")

    # 最近活动
    st.subheader("📝 最近活动")
    activities = [
        "2026-08-21 从 Google Maps 抓取了 50 条 Warung (Jakarta)",
        "2026-08-21  Warung Bu Siti 评分更新: 72 → 87 (黄金)",
        "2026-08-20  Warung Pak Made 完成首次拜访",
        "2026-08-20  Warung Bu Dewi 进入推品试销阶段",
    ]
    for act in activities[:5]:
        st.caption(f"• {act}")


elif nav == "📋 Warung列表":
    # ============================================================
    # 6.2 Warung 列表页面
    # ============================================================

    st.markdown('<p class="main-header">📋 Warung 列表</p>', unsafe_allow_html=True)

    # 筛选器
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        grade_filter = st.selectbox("等级", ["全部", "黄金", "白银", "潜力", "普通"])
    with col2:
        step_filter = st.selectbox("步骤", ["全部", "未接触", "破冰", "拜访", "推品", "深度合作", "长期运营"])
    with col3:
        source_filter = st.selectbox("数据来源", ["全部", "Google Maps", "人工录入"])
    with col4:
        st.markdown("")  # 占位

    # 获取数据
    warungs = get_warungs()

    # 构建表格数据
    if warungs:
        df = pd.DataFrame(warungs)

        # 添加等级徽章
        def get_badge(grade):
            badges = {
                "gold": '<span class="score-badge-gold">🔴 黄金</span>',
                "silver": '<span class="score-badge-silver">🟡 白银</span>',
                "potential": '<span class="score-badge-potential">🟢 潜力</span>',
                "normal": '<span class="score-badge-normal">⚪ 普通</span>',
            }
            return badges.get(grade, grade)

        df['等级'] = df['grade'].apply(get_badge)

        # 添加数据来源标识
        def get_source_label(source):
            return "🌐 Google Maps" if source == "google_maps" else "📝 人工录入"

        df['来源'] = df['source'].apply(get_source_label)

        # 显示表格
        display_cols = ['name', 'city', '来源', 'score', '等级', 'step_name']
        st.markdown(df[display_cols].to_html(escape=False, index=False), unsafe_allow_html=True)

        # 分页
        st.caption(f"共 {len(warungs)} 条记录")

    else:
        st.info("暂无数据，请先导入 Warung 数据")


elif nav == "📥 数据抓取":
    # ============================================================
    # 6.3 数据抓取页面
    # ============================================================

    st.markdown('<p class="main-header">📥 数据抓取管理</p>', unsafe_allow_html=True)

    # 触发新抓取
    st.subheader("🔄 触发新抓取")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        query = st.text_input("搜索关键词", placeholder="例如: warung Jakarta")
    with col2:
        max_results = st.number_input("最大数量", min_value=10, max_value=500, value=100)
    with col3:
        source_type = st.selectbox("数据来源", ["SerpApi", "Google Places API"])

    if st.button("▶ 开始抓取", type="primary"):
        with st.spinner("正在抓取数据..."):
            # TODO: 调用 API
            time.sleep(2)
            st.success(f"✅ 抓取完成！已导入 50 条 Warung 数据")

    st.markdown("---")

    # 最近抓取任务
    st.subheader("📋 最近抓取任务")

    tasks_data = [
        {"time": "2026-08-21 14:30", "query": "warung Jakarta", "count": 50, "status": "✅ 完成"},
        {"time": "2026-08-21 10:00", "query": "warung Bali", "count": 35, "status": "✅ 完成"},
        {"time": "2026-08-20 16:00", "query": "warung Medan", "count": 0, "status": "❌ 失败"},
        {"time": "2026-08-20 09:00", "query": "warung Bandung", "count": 28, "status": "✅ 完成"},
    ]

    for task in tasks_data:
        col1, col2, col3, col4 = st.columns([1.5, 2, 1, 1])
        with col1:
            st.caption(task["time"])
        with col2:
            st.caption(task["query"])
        with col3:
            st.caption(f"{task['count']} 条")
        with col4:
            st.caption(task["status"])


elif nav == "⚙️ 设置":
    # ============================================================
    # 6.4 设置页面
    # ============================================================

    st.markdown('<p class="main-header">⚙️ 系统设置</p>', unsafe_allow_html=True)

    st.subheader("📊 评分权重配置")

    weights = {
        "地理位置价值": 0.25,
        "店主活跃度": 0.20,
        "竞争密度": 0.15,
        "配合度": 0.15,
        "数字化接受度": 0.15,
        "店主画像": 0.05,
        "区域潜力": 0.05,
    }

    for name, weight in weights.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.caption(name)
        with col2:
            st.progress(weight, text=f"{int(weight * 100)}%")

    st.caption(f"总权重: {sum(weights.values()) * 100}%")

    st.divider()

    # API 配置（仅显示，不存储）
    st.subheader("🔑 API 配置")
    st.info("""
    - SerpApi API Key: ✅ 已配置
    - Google Places API Key: ⚠️ 未配置
    - 当前数据来源: SerpApi
    """)

# ============================================================
# 7. 页脚
# ============================================================

st.divider()
st.caption("🏪 WarungScout v1.0.0 · 数据每 5 分钟自动更新")
