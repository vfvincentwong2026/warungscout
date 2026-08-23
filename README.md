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


3. SCORING_MODEL.md（评分模型详解）
重点展开：

7 个维度的定义：

位置价值（25%）：学校、工厂、办公区加分细则
店主活跃度（20%）：WA 群发言、历史活动参与度
竞争密度（15%）：500 米内竞品 Warung 数量评分
配合度（15%）：是否配合地推、陈列、促销
数字化接受度（15%）：是否使用 QRIS、智能手机等
店主画像匹配（5%）：年龄、扩张意愿、学历
区域潜力（5%）：城市分级（雅加达 10 分 vs 其他 5 分）
评分公式：Final Score = Σ(各维度得分 × 权重)

分级标准：80-100 黄金，60-79 白银，40-59 潜力，<40 普通

4. SALES_PROCESS.md（销售步骤与建议逻辑）
明确描述 6 个步骤的状态机：

Step 0（未接触）：自动评分 → 分配优先级

Step 1（破冰）：WA 发送话术 → 等待回复 → 无回复则降温

Step 2（拜访）：地推上门 → 记录结果 → 判断是否进入推品

Step 3（推品试销）：推荐主推品 → 记录是否下单/上架

Step 4（深度合作）：签约独家促销 → 进入长期运营

Step 5（长期运营）：定期巡访 + 新品推荐 + 转介绍激励

同时附上：

状态机流程图（用 Mermaid 绘制）

动态调分规则（如 wa_replied 触发配合度 +2，数字化 +1，总分 +3）

5. FRONTEND_PAGES.md（前端页面与组件设计）
对外视图（公开）：脱敏榜单、区域热力图、整体数据看板

对内视图（销售作战室）：

Warung 列表：按分数/等级/步骤筛选

详情页：7 维雷达图 + 当前步骤 + 下一步建议 + 话术模板

待办看板：按优先级（高/中/低）排序的任务清单

页面交互逻辑：比如点击"完成拜访"后，系统自动更新步骤、扣减待办、触发评分重新计算

6. DATABASE_SCHEMA.md（数据表结构）
创建 4 张核心表 的 SQL 定义：

sql
-- 1. warungs（主表）：id, name, phone, lat/lng, 7个评分字段, final_score, sales_step, grade, created_at...
-- 2. score_history（评分历史）：warung_id, score_before, score_after, reason, feedback_type, created_at...
-- 3. outreach_logs（触达记录）：warung_id, channel(wa/call/visit), template, status(sent/replied/read), created_at...
-- 4. warung_history（全量操作日志）：用于审计和回溯
