# warungscout
面向印尼 Warung（小卖店）的智能评分与销售导航系统。
# 🏪 WarungScout

> **面向印尼 Warung（小卖店）的智能评分与销售导航系统。**
> 帮销售团队回答三个问题：**找谁？先做什么？下一步做什么？**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange.svg)](https://developers.cloudflare.com/workers/)
[![Status: v1.0](https://img.shields.io/badge/Status-v1.0-green.svg)]()

---

## 🎯 这个系统解决什么问题？

如果你在做印尼市场——无论是快消品铺货、数字支付推广，还是供应链金融——你都需要回答一个问题：

> **“印尼几百万家 Warung，哪些最值得先接触？联系上之后下一步做什么？”**

WarungScout 的核心价值：

1. **📊 自动评分**：基于 **7 个维度**（位置/活跃度/竞争/配合度/数字化/画像/区域）对 Warung 进行 0-100 分评估
2. **🗺️ 销售导航**：将 Warung 归入 **6 个销售步骤**（未接触→破冰→拜访→推品→深度合作→长期运营）
3. **💡 动态建议**：根据当前状态自动生成**下一步动作**（如“立即发送 WA 破冰消息”）
4. **🔄 反馈闭环**：销售每次动作的反馈都会**动态调整评分**和后续建议
5. **☁️ 云端部署**：基于 **Cloudflare Workers** 全球边缘网络，印尼访问速度极快

---

## 🚀 快速开始

### 前置条件
- Python 3.10+
- Cloudflare 账号（免费）
- Node.js（用于前端构建）

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
# 编辑 .env，配置 API Key 和数据库连接

# 4. 初始化数据库
npx wrangler d1 create warungscout_db
npx wrangler d1 execute warungscout_db --file=./migrations/init.sql

# 5. 本地开发
npx wrangler dev

# 6. 部署到 Cloudflare
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
│   └── web/              # 前端页面
│       ├── public/       # 对外营销视图（脱敏榜单）
│       └── internal/     # 对内销售作战室（需登录）
├── migrations/           # D1 数据库迁移
├── docs/                 # 完整文档
├── config/               # 配置文件
├── tests/                # 单元测试
├── wrangler.toml         # Cloudflare 配置
└── README.md
🔄 与 warung-network-mvp 的关系
项目	定位	数据流向
warung-network-mvp	数据采集 + 地图展示	生产数据（地推录入）
WarungScout	评分 + 步骤导航 + 销售闭环	消费数据（评分、分级、导航、触达）
text
warung-network-mvp（采集数据）→ CSV/API → WarungScout（评分+导航）→ 销售行动 → 反馈 → 评分动态调整
两者通过 CSV 导出 或 API 对接 进行数据流转，各司其职。

📄 许可证
MIT License — 可自由使用、修改、商用。

Made for 印尼 Warung 生态

text

---

## docs 文件夹搭建指南

为了让 Kimi 或你的开发伙伴能按图索骥，建议在 `docs/` 文件夹下放 **5 个核心文档**，我已经帮你梳理好了对应的内容摘要和文件结构：

### 1. `README.md`（你刚刚创建的门面）
- 项目背景
- 系统架构
- 快速开始（部署步骤）
- 项目结构

### 2. `ARCHITECTURE.md`（技术架构与部署）
这个文档需要包含：
- **技术选型**：为什么选 Cloudflare Workers、D1 数据库、Python 运行时等
- **架构图**：数据流从 `warung-network` 到 `WarungScout` 再到销售团队的流程图
- **部署拓扑**：开发环境、预览环境、生产环境的配置区别
- **数据流转**：数据如何从 CSV 导入 D1，再到前端展示

**内容摘要示例：**
```text
系统采用三层架构：
1. 数据层（D1 SQLite）：存储 Warung 信息、评分、步骤、反馈历史。
2. 逻辑层（Python Worker）：包含评分引擎、步骤建议生成器、反馈处理器。
3. 展示层（React + Streamlit）：提供对外营销视图和对内销售作战室两个入口。
