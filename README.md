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
