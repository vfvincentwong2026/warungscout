# 🏪 WarungScout

> **印尼 Warung（小卖店）智能评分与销售导航系统。**
> 从 Google Maps 自动发现 Warung，AI 评分排序，并告诉销售团队：**找谁？先做什么？下一步做什么？**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange.svg)](https://developers.cloudflare.com/workers/)
[![Status: v1.0](https://img.shields.io/badge/Status-v1.0-green.svg)]()

---

## 这个系统解决什么问题？

印尼有数百万家 Warung（小卖店），是快消品、数字支付、供应链金融的核心渠道。但销售团队面临三个问题：

| 问题 | 传统方式 | WarungScout 的做法 |
| :--- | :--- | :--- |
| **找不到客户** | 盲目扫街、等人介绍 | **Google Maps 自动抓取**，覆盖雅加达、泗水、巴厘岛等核心区域 |
| **不知道谁值得联系** | 凭感觉判断 | **7 维 AI 评分**（0-100 分），自动分级：🔴黄金 / 🟡白银 / 🟢潜力 / ⚪普通 |
| **不知道下一步做什么** | 反复试错 | **6 步销售导航**（破冰→拜访→推品→深度合作→长期运营），自动生成下一步动作 |

**一句话：WarungScout 帮销售团队从 0 到 1 找到客户、判断优先级、执行跟进动作。**

---

## 🎯 核心功能

| 功能模块 | 说明 |
| :--- | :--- |
| **🔍 Google Maps 自动抓取** | 支持 SerpApi / Google Places API / Playwright 三种方案，一键抓取 Warung 数据 |
| **📊 7 维智能评分** | 位置价值、店主活跃度、竞争密度、配合度、数字化接受度、店主画像、区域潜力 → 0-100 分 |
| **🗺️ 6 步销售导航** | 未接触 → 破冰 → 拜访 → 推品 → 深度合作 → 长期运营，自动生成下一步动作 |
| **🔄 反馈闭环** | 销售反馈（WA 回复 / 拜访成功 / 试销下单）自动调整评分和后续建议 |
| **📋 销售作战室** | Web Dashboard：待办任务、Warung 列表、评分雷达图、一键触达 |
| **☁️ 云端部署** | 基于 Cloudflare Workers 边缘网络，印尼访问速度快，免费额度充足 |


## 🧠 评分模型（7 个维度）
最终得分 = 位置×25% + 活跃度×20% + 竞争×15% + 配合度×15% + 数字化×15% + 画像×5% + 区域×5%

text

| 维度 | 权重 | 说明 |
| :--- | :--- | :--- |
| **位置价值** | 25% | 学校、工厂、办公区、交通枢纽周边 |
| **店主活跃度** | 20% | Google Maps 评分、WA 群活跃度、活动参与 |
| **竞争密度** | 15% | 500m 内竞品 Warung 数量 |
| **配合度** | 15% | WA 回复率、地推反馈、合作历史（新 Warung 默认 50 分） |
| **数字化接受度** | 15% | 数字支付使用、WA 响应速度、智能手机（新 Warung 默认 50 分） |
| **店主画像** | 5% | 年龄、扩张意愿、学历、本地人（新 Warung 默认 50 分） |
| **区域潜力** | 5% | 城市 Tier（雅加达 100 分 / 泗水 80 分 / 其他 40-60 分） |

### 分级与行动建议

| 分数 | 等级 | 行动建议 |
| :--- | :--- | :--- |
| 80-100 | 🔴 **黄金** | 立即 WA 联系 + 地推拜访 |
| 60-79 | 🟡 **白银** | WA 破冰，先培养再推品 |
| 40-59 | 🟢 **潜力** | 地推拜访，当面建立信任 |
| < 40 | ⚪ **普通** | 暂缓触达，沉淀数据 |


## 📂 项目结构
warungscout/
├── src/
│ ├── api/ # Cloudflare Workers API
│ │ └── index.py # FastAPI 应用（15+ 端点）
│ ├── core/ # 核心业务逻辑
│ │ ├── scorer.py # 7 维评分引擎
│ │ ├── advisor.py # 步骤建议生成器
│ │ └── feedback.py # 反馈闭环处理器
│ ├── importers/ # 数据导入模块
│ │ ├── google_maps_importer.py # Google Maps 抓取器
│ │ └── import_to_d1.py # D1 数据库导入器
│ └── pages/ # React 前端页面
│ ├── Dashboard.tsx # 销售作战室总览
│ ├── WarungList.tsx # Warung 列表（筛选/排序）
│ ├── Import.tsx # 数据抓取管理
│ └── Settings.tsx # 系统设置
├── config/
│ ├── settings.yaml # 全局配置
│ └── search_queries.json # 印尼 8 个城市搜索词库
├── migrations/
│ ├── init.sql # D1 数据库初始化
│ └── 004_add_gmaps_fields.sql # Google Maps 字段增量迁移
├── web/
│ └── app.py # Streamlit 前端（备用）
├── docs/ # 完整文档
├── wrangler.toml # Cloudflare 部署配置
├── package.json # Node.js 依赖
├── requirements.txt # Python 依赖
└── README.md

text


## 🔄 与 warung-network-mvp 的关系

| 项目 | 定位 | 数据流向 |
| :--- | :--- | :--- |
| **warung-network-mvp** | 地推数据采集 + 地图展示 | **生产数据** |
| **WarungScout** | 自动抓取 + 评分 + 销售导航 | **消费数据**（评分、分级、导航、触达） |
Google Maps → [自动抓取] → WarungScout → 评分 → 分级 → 步骤导航 → 销售行动 → 反馈 → 评分动态调整
↑
warung-network-mvp → [CSV/API 导入] ──┘

text

两者通过 **CSV 导出** 或 **API 对接** 进行数据流转，各司其职。

---

## 🚀 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+
- Cloudflare 账号（免费）
- SerpApi API Key 或 Google Places API Key

### 1. 克隆仓库

```bash
git clone https://github.com/vfvincentwong2026/warungscout.git
cd warungscout
2. 安装后端依赖
bash
pip install -r requirements.txt
3. 安装前端依赖
bash
npm install
4. 配置环境变量
bash
cp .env.example .env
# 编辑 .env，填入 SerpApi API Key 或 Google Places API Key
5. 初始化数据库
bash
npx wrangler d1 create warungscout_db
npx wrangler d1 execute warungscout_db --file=./migrations/init.sql
6. 启动后端（本地开发）
bash
npx wrangler dev
# 后端 API 运行在 http://localhost:8787
7. 启动前端（另一个终端）
bash
npm run dev
# 前端运行在 http://localhost:5173
8. 触发抓取（首次使用）
bash
# 使用预置词库批量抓取
python src/importers/google_maps_importer.py --batch --config config/search_queries.json

# 或单次抓取
python src/importers/google_maps_importer.py --query "warung Jakarta" --max 100
9. 部署到 Cloudflare
bash
npm run deploy
🛠️ 技术栈
层级	技术选型
后端运行时	Cloudflare Workers (Python 3.10+)
API 框架	FastAPI
数据库	Cloudflare D1 (SQLite)
缓存	Cloudflare KV
前端框架	React 19 + TypeScript + Vite
UI 组件	shadcn/ui + Tailwind CSS
图表	Recharts
数据抓取	SerpApi / Google Places API / Playwright
部署	Wrangler / pywrangler
📄 许可证
MIT License — 可自由使用、修改、商用。
