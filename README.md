# 🏪 WarungScout

> **面向印尼 Warung（小卖店）的智能评分与销售导航系统。**
> 自动从 Google Maps 抓取 Warung 数据，AI 评分排序，并告诉销售团队：**找谁？先做什么？下一步做什么？**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange.svg)](https://developers.cloudflare.com/workers/)
[![Status: v1.0](https://img.shields.io/badge/Status-v1.0-green.svg)]()


## 🎯 这个系统解决什么问题？

如果你在做印尼市场——无论是快消品铺货、数字支付推广，还是供应链金融——你都需要回答一个问题：

> **“印尼几百万家 Warung，哪些最值得先接触？联系上之后下一步做什么？”**

WarungScout 的核心价值：

1. **📊 自动采集**：从 Google Maps 自动抓取印尼 Warung 数据，覆盖雅加达、泗水、巴厘岛等核心区域
2. **🤖 智能评分**：基于 **7 个维度**（位置/活跃度/竞争/配合度/数字化/画像/区域）对 Warung 进行 0-100 分评估
3. **🗺️ 销售导航**：将 Warung 归入 **6 个销售步骤**（未接触→破冰→拜访→推品→深度合作→长期运营）
4. **💡 动态建议**：根据当前状态自动生成**下一步动作**（如“立即发送 WA 破冰消息”）
5. **🔄 反馈闭环**：销售每次动作的反馈都会**动态调整评分**和后续建议
6. **☁️ 云端部署**：基于 **Cloudflare Workers** 全球边缘网络，印尼访问速度极快


## 🚀 快速开始

### 前置条件
- Python 3.10+
- Cloudflare 账号（免费）
- SerpApi API Key 或 Google Places API Key（用于抓取 Google Maps 数据）

### 一键部署到 Cloudflare

```bash
# 1. 克隆仓库
git clone https://github.com/vfvincentwong2026/warungscout.git
cd warungscout

# 2. 安装依赖
pip install -r requirements.txt
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，配置以下内容：
#   - SERPAPI_API_KEY 或 GOOGLE_PLACES_API_KEY
#   - CLOUDFLARE_ACCOUNT_ID
#   - CLOUDFLARE_API_TOKEN

# 4. 从 Google Maps 抓取 Warung 数据（首次运行）
python src/importers/google_maps_importer.py --query "warung Jakarta" --max 100

# 5. 批量抓取（使用预置词库）
python src/importers/google_maps_importer.py --batch --config config/search_queries.json

# 6. 执行评分
python src/core/run_scorer.py --source warungs

# 7. 初始化数据库
npx wrangler d1 create warungscout_db
npx wrangler d1 execute warungscout_db --file=./migrations/init.sql

# 8. 导入数据到 D1
python src/importers/import_to_d1.py --file data/warungs_export.csv

# 9. 本地开发
npx wrangler dev

# 10. 部署到 Cloudflare
npx wrangler deploy
📂 项目结构
text
warungscout/
├── src/
│   ├── api/              # Cloudflare Workers API
│   │   ├── routes/       # 路由：评分、步骤、反馈等
│   │   └── models/       # 数据模型（Pydantic）
│   ├── core/             # 核心业务逻辑
│   │   ├── scorer.py     # 7维评分引擎
│   │   ├── advisor.py    # 步骤建议生成器
│   │   └── feedback.py   # 反馈闭环处理
│   ├── importers/        # 数据导入模块
│   │   ├── google_maps_importer.py  # Google Maps 抓取器
│   │   └── import_to_d1.py          # 导入 D1 数据库
│   └── web/              # 前端页面
│       ├── public/       # 对外营销视图（脱敏榜单）
│       └── internal/     # 对内销售作战室（需登录）
├── config/
│   ├── settings.yaml              # 全局配置
│   └── search_queries.json        # 搜索词库（印尼各城市）
├── migrations/           # D1 数据库迁移
├── docs/                 # 完整文档
├── tests/                # 单元测试
├── data/                 # 数据缓存目录
├── wrangler.toml         # Cloudflare 配置
└── README.md
🔄 Google Maps 自动抓取
WarungScout 支持从 Google Maps 自动抓取 Warung 数据，无需手动录入。

支持的抓取方式
方式	说明	适用场景
SerpApi	通过 API 调用，稳定、无需处理反爬	快速集成，推荐 MVP 阶段使用
Google Places API	官方 API，合规性最好	正式生产环境
Playwright 自建爬虫	模拟浏览器行为，免费但需处理反爬	预算有限，技术能力强的团队
预置搜索词库
json
{
  "queries": [
    {"keyword": "warung Jakarta", "location": "-6.2088,106.8456,14z"},
    {"keyword": "warung Surabaya", "location": "-7.2575,112.7521,14z"},
    {"keyword": "warung Bali", "location": "-8.3405,115.0920,14z"},
    {"keyword": "warung Bandung", "location": "-6.9175,107.6191,14z"},
    {"keyword": "warung Medan", "location": "3.5952,98.6722,14z"},
    {"keyword": "warung Yogyakarta", "location": "-7.7956,110.3695,14z"}
  ]
}
抓取字段映射
Google Maps 字段	WarungScout 字段	说明
name	name	Warung 名称
formatted_address	address	地址
geometry.location.lat	latitude	纬度
geometry.location.lng	longitude	经度
formatted_phone_number	phone	电话
rating	activity_score（部分）	评分参考
user_ratings_total	activity_score（部分）	评论数参考
types	region / 标签	分类和区域判断
🔄 与 warung-network-mvp 的关系
项目	定位	数据流向
warung-network-mvp	人工地推数据采集 + 地图展示	生产数据（地推录入）
WarungScout	自动抓取 + 评分 + 步骤导航 + 销售闭环	消费数据（自动抓取、评分、分级、导航、触达）
text
Google Maps → [自动抓取] → WarungScout → 评分 → 分级 → 步骤导航 → 销售行动 → 反馈 → 评分动态调整
                                    ↑
warung-network-mvp → [CSV/API导入] ──┘
两者可通过 CSV 导出 或 API 对接 进行数据流转，各司其职。

📄 许可证
MIT License — 可自由使用、修改、商用。
