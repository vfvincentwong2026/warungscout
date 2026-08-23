# 🛠️ WarungScout 技术架构与部署方案

**版本**：v1.0.0
**日期**：2026年8月23日
**状态**：设计冻结，可进入开发


## 1. 核心定位

WarungScout 是一个面向印尼 Warung 的**智能评分与销售导航系统**。

| 属性 | 说明 |
| :--- | :--- |
| **用户** | 快消品/支付/供应链金融的销售与商务团队 |
| **目标** | 每周自动输出高价值 Warung 名单 + 下一步动作建议 |
| **数据量** | 支持 500-5000 条 Warung 数据 |
| **部署方式** | Cloudflare Workers 边缘计算 |


## 2. 技术选型

| 层级 | 技术选型 | 理由 |
| :--- | :--- | :--- |
| **后端运行时** | Cloudflare Python Workers | 零运维、全球边缘节点、印尼访问快、免费额度充足 |
| **API 框架** | FastAPI | 高性能、自动生成文档、Pydantic 数据校验 |
| **数据库** | Cloudflare D1 (SQLite) | 与 Workers 原生集成、5GB 免费额度 |
| **前端框架** | React 19 + TypeScript + Vite | 现代化 UI、类型安全 |
| **UI 组件库** | shadcn/ui | 美观、可定制、组件丰富 |
| **状态管理** | Zustand | 轻量、简单、适合中小型应用 |
| **HTTP 客户端** | TanStack Query | 数据缓存、自动重试、状态管理 |
| **图表库** | Recharts | 雷达图展示 7 维评分 |
| **部署工具** | Wrangler / pywrangler | Cloudflare 官方 CLI |
| **包管理** | uv + pyproject.toml | 现代化 Python 包管理 |



┌─────────────────────────────────────────────────────────────────┐
│ 用户访问层 │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ 对外营销视图 │ │ 对内销售作战室│ │
│ │ (公开/脱敏) │ │ (需登录) │ │
│ └──────────────┘ └──────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Cloudflare Workers 边缘网络 │
│ (Python + FastAPI) │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ API 路由层 │ │
│ │ /api/warungs /api/score /api/advice /api/feed │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 核心业务层 │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │ 评分引擎 │ │ 步骤导航 │ │ 反馈闭环 │ │ │
│ │ │ (7维) │ │ (6步) │ │ (动态调分)│ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Cloudflare 数据层 │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ D1 │ │ KV │ │ R2 │ │
│ │ (主数据库)│ │ (会话/缓存)│ │ (静态资源)│ │
│ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ 外部数据源 │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ warung- │ │ Google Maps │ │
│ │ network-mvp │ │ Places API │ │
│ │ (CSV/API) │ │ (位置补全) │ │
│ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘

text


## 4. 数据流转
[warung-network-mvp] → (CSV导出/API) → [数据导入模块] → [D1 数据库]
│
▼
[评分引擎 (7维)]
│
▼
[步骤建议生成器]
│
▼
┌──────────────────────────────────────────────────────────────┐
│ 前端展示 │
│ ┌──────────────────────┐ ┌──────────────────────────┐ │
│ │ 对外视图 (公开) │ │ 对内视图 (需登录) │ │
│ │ - 脱敏榜单 │ │ - 评分列表 + 排序 │ │
│ │ - 区域热力图 │ │ - 7维雷达图 │ │
│ │ - 数据总览 │ │ - 步骤看板 + 建议 │ │
│ └──────────────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
▼
[销售执行动作] → [反馈提交] → [反馈闭环处理器] → [评分动态调整] → [更新D1]

text


## 5. Cloudflare 部署配置

### 5.1 `wrangler.toml` 配置

```toml
name = "warungscout"
main = "src/api/index.py"
compatibility_date = "2026-08-14"

# Python 配置
[python]
python_compat = "3.10"

# D1 数据库绑定
[[d1_databases]]
binding = "DB"
database_name = "warungscout_db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# KV 命名空间绑定
[[kv_namespaces]]
binding = "KV"
id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 静态资源绑定（前端构建产物）
[assets]
binding = "ASSETS"
directory = "./dist"

# 环境变量
[vars]
ENVIRONMENT = "production"
5.2 部署环境划分
环境	Worker 名称	数据库	用途
开发	warungscout-dev	本地 D1	本地开发调试
预览	warungscout-preview	预览 D1	PR 自动部署验证
生产	warungscout-prod	生产 D1	正式使用
6. 成本估算
项目	免费额度	预估用量	月度成本
Workers 请求	10万次/日	5,000次/日	$0
D1 存储	5GB	100MB	$0
D1 读取	500万行/月	10万行/月	$0
D1 写入	10万次/月	5,000次/月	$0
KV 存储	1GB	100MB	$0
前端资源	无限	小型	$0
月度总成本：$0（MVP 阶段完全在免费额度内）

7. 安全与合规
维度	措施
传输安全	全量 HTTPS（Cloudflare 原生支持）
认证授权	JWT Token / API Key（对内视图）
数据隔离	公开视图仅展示脱敏数据
密钥管理	Cloudflare Secrets 存储
数据来源	仅使用公开或已授权数据
8. 后续扩展方向
方向	说明	优先级
WhatsApp Business API 集成	自动发送破冰消息	P1
定时自动评分	每周自动重新计算所有 Warung 分数	P2
数据回写	将评分结果写回 warung-network-mvp	P2
A/B 测试话术	不同话术转化率对比	P3
文档结束

text


# 文档二：`docs/SCORING_MODEL.md`


```markdown
# 📊 WarungScout 评分模型详解

**版本**：v1.0.0
**日期**：2026年8月23日


## 1. 评分公式
Final Score =
Location × 25%

Activity × 20%

Competition × 15%

Cooperation × 15%

Digital × 15%

Owner × 5%

Region × 5%

text

各维度满分均为 100 分，加权后总分 0-100 分。


## 2. 各维度评分细则

### 维度1：地理位置价值（权重 25%）

| 周边设施 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| 学校（中小学/大学） | +10 | Google Maps Places API |
| 工厂/工业区 | +10 | Google Maps Places API |
| 办公区/写字楼 | +8 | Google Maps Places API |
| 住宅区（中高端） | +5 | Google Maps Places API |
| 交通枢纽（车站） | +7 | Google Maps Places API |

**满分：25 分**


### 维度2：店主活跃度（权重 20%）

| 指标 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| 在 WA 群内活跃发言（近7天≥3次） | +10 | WA 群运营记录 |
| 曾配合过地推活动 | +8 | 历史记录 |
| 主动询问过新品/促销 | +7 | 历史记录 |

**满分：20 分**


### 维度3：竞争密度（权重 15%）

| 竞品 Warung 数量（500m 内） | 得分 | 数据来源 |
| :--- | :--- | :--- |
| 0-2 家 | 15（满分） | Google Maps Places API |
| 3-5 家 | 12 | Google Maps Places API |
| 6-10 家 | 8 | Google Maps Places API |
| >10 家 | 5 | Google Maps Places API |

**满分：15 分**


### 维度4：配合度（权重 15%）

| 指标 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| **历史响应率** | | |
| 过往 WA 消息回复率 > 70% | +8 | 历史触达记录 |
| 过往 WA 消息回复率 30%-70% | +4 | 历史触达记录 |
| 过往 WA 消息回复率 < 30% | +1 | 历史触达记录 |
| **地推反馈** | | |
| 曾接受上门拜访，沟通顺畅 | +7 | 地推记录 |
| 曾接受上门拜访，态度一般 | +3 | 地推记录 |
| 拒绝拜访 | -5（扣分） | 地推记录 |
| **合作历史** | | |
| 曾参与过任何试点/促销活动 | +5 | 历史记录 |
| 曾推荐过其他 Warung | +5（额外） | 历史记录 |

**满分：20 分**


### 维度5：数字化接受度（权重 15%）

| 指标 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| **支付方式** | | |
| 使用 QRIS / OVO / GoPay 等数字支付 | +8 | 地推观察/访谈 |
| 仅使用现金 | 0 | 地推观察/访谈 |
| **WA 使用习惯** | | |
| WA 回复通常在 1 小时内 | +7 | 历史记录 |
| WA 回复通常在 24 小时内 | +3 | 历史记录 |
| 基本不回复 WA | 0 | 历史记录 |
| **设备与工具** | | |
| 使用智能手机（非老年机） | +5 | 地推观察 |
| 会使用手机拍照/发图片 | +3 | 地推观察 |
| 会使用手机看视频/刷社媒 | +2 | 地推观察 |
| **主动意愿** | | |
| 对"手机管理库存/下单"感兴趣 | +5（额外） | 访谈记录 |
| 已在使用任何线上订货 App | +5（额外） | 访谈记录 |

**满分：20 分**


### 维度6：店主画像匹配（权重 5%）

| 画像特征 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| 年龄 20-35 岁 | +3 | 访谈记录 |
| 有扩张/开分店计划 | +2 | 访谈记录 |
| 家庭主要收入来源 | +2 | 访谈记录 |
| 女性店主（沟通更顺畅） | +2 | 访谈记录 |
| 高中以上学历 | +2 | 访谈记录 |
| 本地人（非流动人口） | +2 | 访谈记录 |

> 满分 13 分，封顶 10 分

**满分：10 分**


### 维度7：区域潜力（权重 5%）

| 城市层级 | 得分 | 说明 |
| :--- | :--- | :--- |
| **Tier 1**：雅加达 | 10 | 大雅加达都市圈 |
| **Tier 1**：泗水、棉兰、万隆 | 8 | 核心省会 |
| **Tier 2**：日惹、三宝垄、望加锡 | 6 | 重要城市 |
| **Tier 3**：其他城市 | 4 | 非核心区域 |

**满分：10 分**


## 3. 分级标准

| 分数区间 | 等级 | 配合度特征 | 推荐触达方式 |
| :--- | :--- | :--- | :--- |
| 80-100 | 🔴 **黄金** | 高配合度+高数字化 | 立即 WA 推品 + 地推拜访 |
| 60-79 | 🟡 **白银** | 中高配合度+中数字化 | WA 破冰，先培养再推品 |
| 40-59 | 🟢 **潜力** | 中低配合度+低数字化 | 地推拜访，当面建立信任 |
| < 40 | ⚪ **普通** | 低配合度+低数字化 | 暂缓触达，沉淀数据 |


## 4. 评分输出示例

```json
{
  "warung_name": "Warung Bu Siti",
  "location": "Jl. Raya Canggu No. 45, Bali",
  "final_score": 87,
  "grade": "gold",
  "breakdown": {
    "location": { "score": 85, "weight": 0.25, "weighted": 21.25 },
    "activity": { "score": 70, "weight": 0.20, "weighted": 14.00 },
    "competition": { "score": 90, "weight": 0.15, "weighted": 13.50 },
    "cooperation": { "score": 80, "weight": 0.15, "weighted": 12.00 },
    "digital": { "score": 75, "weight": 0.15, "weighted": 11.25 },
    "owner": { "score": 65, "weight": 0.05, "weighted": 3.25 },
    "region": { "score": 85, "weight": 0.05, "weighted": 4.25 }
  },
  "top_actions": [
    "优先联系，配合度高+数字化接受度好",
    "可直接通过 WA 推送新品信息，预期回复率高"
  ]
}
5. Python 实现
python
from typing import Dict, Any

def calculate_final_score(warung: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算 Warung 的 7 维综合评分
    """
    # 各维度得分（0-100）
    location_score = calculate_location_score(warung)
    activity_score = calculate_activity_score(warung)
    competition_score = calculate_competition_score(warung)
    cooperation_score = calculate_cooperation_score(warung)
    digital_score = calculate_digital_score(warung)
    owner_score = calculate_owner_score(warung)
    region_score = calculate_region_score(warung)

    # 权重
    weights = {
        'location': 0.25,
        'activity': 0.20,
        'competition': 0.15,
        'cooperation': 0.15,
        'digital': 0.15,
        'owner': 0.05,
        'region': 0.05,
    }

    # 加权总分
    total = (
        location_score * weights['location'] +
        activity_score * weights['activity'] +
        competition_score * weights['competition'] +
        cooperation_score * weights['cooperation'] +
        digital_score * weights['digital'] +
        owner_score * weights['owner'] +
        region_score * weights['region']
    )

    # 四舍五入取整
    final_score = round(total)

    # 分级
    if final_score >= 80:
        grade = 'gold'
        grade_label = '黄金'
    elif final_score >= 60:
        grade = 'silver'
        grade_label = '白银'
    elif final_score >= 40:
        grade = 'potential'
        grade_label = '潜力'
    else:
        grade = 'normal'
        grade_label = '普通'

    return {
        'total_score': final_score,
        'grade': grade,
        'grade_label': grade_label,
        'breakdown': {
            'location': {'score': location_score, 'weighted': round(location_score * weights['location'], 2)},
            'activity': {'score': activity_score, 'weighted': round(activity_score * weights['activity'], 2)},
            'competition': {'score': competition_score, 'weighted': round(competition_score * weights['competition'], 2)},
            'cooperation': {'score': cooperation_score, 'weighted': round(cooperation_score * weights['cooperation'], 2)},
            'digital': {'score': digital_score, 'weighted': round(digital_score * weights['digital'], 2)},
            'owner': {'score': owner_score, 'weighted': round(owner_score * weights['owner'], 2)},
            'region': {'score': region_score, 'weighted': round(region_score * weights['region'], 2)}
        }
    }


def calculate_cooperation_score(warung: Dict[str, Any]) -> int:
    """
    计算配合度得分 (0-100)
    """
    score = 0

    # 1. 历史响应率 (0-40分)
    reply_rate = warung.get('reply_rate', 0)  # 0.0 - 1.0
    if reply_rate > 0.7:
        score += 40
    elif reply_rate > 0.3:
        score += 20
    elif reply_rate > 0:
        score += 5

    # 2. 地推反馈 (0-35分)
    visit_feedback = warung.get('visit_feedback')  # 'positive' | 'neutral' | 'negative' | None
    if visit_feedback == 'positive':
        score += 35
    elif visit_feedback == 'neutral':
        score += 15
    elif visit_feedback == 'negative':
        score -= 25

    # 3. 合作历史 (0-25分)
    if warung.get('participated_promo', False):
        score += 15
    if warung.get('referral_given', False):
        score += 10

    return max(0, min(100, score))
文档结束

text


# 文档三：`docs/SALES_PROCESS.md`


```markdown
# 🗺️ WarungScout 销售步骤与建议逻辑

**版本**：v1.0.0
**日期**：2026年8月23日


## 1. 销售步骤总览

| 步骤 | 状态 | 销售动作 | 触发条件 | 成功标志 |
| :--- | :--- | :--- | :--- | :--- |
| **0** | 未接触 | 系统初筛，分配优先级 | 数据录入系统 | 产生评分 |
| **1** | 首次破冰 | WA 发送破冰消息 | 分数 ≥ 60 分 | 店主回复 |
| **2** | 初次拜访 | 地推上门拜访 | 回复且有基础兴趣 | 当面沟通 10min+ |
| **3** | 推品试销 | 推荐主推品/小批量铺货 | 拜访沟通顺畅 | 店主下单/上架 |
| **4** | 深度合作 | 签约独家/联合促销 | 试销效果良好 | 签订合作协议 |
| **5** | 长期运营 | 定期巡访/新品推荐 | 合作稳定 | 持续进货 + 转介绍 |


## 2. 状态机流程图
[数据录入]
│
▼
┌─────────────────────────────────────────────┐
│ Step 0: 未接触 │
│ 动作: 系统自动评分，确定初始等级 │
│ 判断: 分数 ≥ 60 ? │
└─────────────────┬───────────────────────────┘
│ 是
▼
┌─────────────────────────────────────────────┐
│ Step 1: 首次破冰 (WA 联系) │
│ 动作: 发送 WA 破冰消息，等待回复 │
│ 判断: 店主是否回复？ │
└─────────────┬─────────────────┬─────────────┘
│ 是 │ 否 (3次无回复)
▼ ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ Step 2: 初次拜访 │ │ 降温/暂停 │
│ 动作: 地推上门拜访 │ │ 15天后重新激活 │
└─────────────┬───────────┘ └─────────────────────────┘
│ 拜访成功
▼
┌─────────────────────────────────────────────┐
│ Step 3: 推品试销 │
│ 动作: 推荐主推品，小批量铺货 │
│ 判断: 店主是否下单/上架？ │
└─────────────┬─────────────────┬─────────────┘
│ 是 │ 否
▼ ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ Step 4: 深度合作 │ │ 返回 Step 2，换品推荐 │
│ 动作: 签约独家/促销 │ └─────────────────────────┘
└─────────────┬───────────┘
│ 签约成功
▼
┌─────────────────────────────────────────────┐
│ Step 5: 长期运营 │
│ 动作: 定期巡访 + 新品推荐 + 转介绍激励 │
│ 目标: 持续进货 + 推荐新 Warung │
└─────────────────────────────────────────────┘

text


## 3. 步骤建议生成器

### 3.1 Python 实现

```python
from typing import Dict, Any
from datetime import datetime, timedelta

def generate_next_advice(warung: Dict[str, Any], score_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 Warung 当前状态和评分，生成下一步建议
    """
    current_step = warung.get('sales_step', 0)
    score = score_result['total_score']
    now = datetime.now()

    # ============================================
    # Step 0: 未接触
    # ============================================
    if current_step == 0:
        if score >= 70:
            return {
                'next_step': 1,
                'action': '立即通过 WhatsApp 发送破冰消息',
                'description': '高分 Warung，优先触达',
                'template': 'WARUNG_GOLD_BREAK_ICE',
                'priority': 'high',
                'timeout_days': 1,
                'channel': 'whatsapp'
            }
        elif score >= 50:
            return {
                'next_step': 1,
                'action': '3 天内通过 WhatsApp 发送破冰消息',
                'description': '中等潜力 Warung，建议跟进',
                'template': 'WARUNG_SILVER_BREAK_ICE',
                'priority': 'medium',
                'timeout_days': 3,
                'channel': 'whatsapp'
            }
        else:
            return {
                'next_step': 0,
                'action': '暂不触达，添加到培育池',
                'description': '低分 Warung，等待后续激活',
                'priority': 'low',
                'timeout_days': 30,
                'channel': None
            }

    # ============================================
    # Step 1: 首次破冰 (WA 已发送)
    # ============================================
    if current_step == 1:
        last_action = warung.get('last_action_at')
        if last_action:
            days_since = (now - datetime.fromtimestamp(last_action)).days
        else:
            days_since = 0

        if days_since > 2:
            return {
                'next_step': 1,
                'action': '发送第二次 WA 消息跟进',
                'description': f'上次 WA 发送已 {days_since} 天，无回复，继续跟进',
                'template': 'WARUNG_FOLLOWUP_1',
                'priority': 'medium',
                'timeout_days': 2,
                'channel': 'whatsapp'
            }
        elif days_since > 7:
            return {
                'next_step': 0,
                'action': '暂停跟进，标记为冷却状态',
                'description': '连续 7 天无回复，15 天后重新激活',
                'priority': 'low',
                'timeout_days': 15,
                'channel': None
            }
        else:
            return {
                'next_step': 1,
                'action': '等待店主回复',
                'description': 'WA 已发送，等待店主回应',
                'priority': 'medium',
                'timeout_days': 2,
                'channel': None
            }

    # ============================================
    # Step 2: 初次拜访
    # ============================================
    if current_step == 2:
        visit_count = warung.get('visit_count', 0)

        if visit_count == 0:
            return {
                'next_step': 2,
                'action': '安排地推团队上门拜访',
                'description': '店主已回复 WA，建议 3 天内完成首次拜访',
                'template': 'VISIT_SCRIPT_V1',
                'priority': 'high',
                'timeout_days': 3,
                'channel': 'visit'
            }
        elif visit_count == 1 and warung.get('visit_result') == 'pending':
            return {
                'next_step': 2,
                'action': '第二次拜访，加深关系',
                'description': '首次拜访后未达成合作，建议再次拜访并换品推荐',
                'template': 'VISIT_SCRIPT_V2',
                'priority': 'medium',
                'timeout_days': 5,
                'channel': 'visit'
            }
        else:
            if warung.get('visit_result') == 'success':
                return {
                    'next_step': 3,
                    'action': '进入推品试销阶段',
                    'description': '拜访沟通顺畅，推荐主推品并安排小批量铺货',
                    'priority': 'high',
                    'timeout_days': 3,
                    'channel': None
                }
            else:
                return {
                    'next_step': 0,
                    'action': '暂缓跟进，重新评估',
                    'description': '多次拜访无果，建议暂时搁置 30 天',
                    'priority': 'low',
                    'timeout_days': 30,
                    'channel': None
                }

    # ============================================
    # Step 3: 推品试销
    # ============================================
    if current_step == 3:
        trial_status = warung.get('trial_status', 'pending')

        if trial_status == 'pending':
            return {
                'next_step': 3,
                'action': '确认试销铺货情况',
                'description': '已推荐主推品，需确认是否已上架/陈列',
                'priority': 'high',
                'timeout_days': 3,
                'channel': 'visit'
            }
        elif trial_status == 'success':
            return {
                'next_step': 4,
                'action': '进入深度合作阶段',
                'description': '试销效果良好，建议推进签约独家/联合促销',
                'priority': 'high',
                'timeout_days': 7,
                'channel': None
            }
        else:
            return {
                'next_step': 2,
                'action': '返回拜访阶段，换品推荐',
                'description': '试销效果不佳，建议换品推荐并重新拜访',
                'priority': 'medium',
                'timeout_days': 5,
                'channel': 'visit'
            }

    # ============================================
    # Step 4: 深度合作
    # ============================================
    if current_step == 4:
        return {
            'next_step': 5,
            'action': '完成签约，进入长期运营',
            'description': '准备合作协议，安排签约仪式或正式确认',
            'priority': 'high',
            'timeout_days': 7,
            'channel': None
        }

    # ============================================
    # Step 5: 长期运营
    # ============================================
    if current_step == 5:
        return {
            'next_step': 5,
            'action': '定期巡访 + 新品推荐',
            'description': '合作稳定，建议每 2 周巡访一次，每月推荐 1-2 个新品',
            'priority': 'medium',
            'timeout_days': 14,
            'channel': 'visit'
        }

    # 默认返回
    return {
        'next_step': current_step,
        'action': '状态异常，请联系管理员',
        'description': f'无法识别的步骤状态: {current_step}',
        'priority': 'low',
        'timeout_days': 7,
        'channel': None
    }
4. 反馈驱动的动态调分
4.1 反馈类型映射
反馈类型	配合度变化	数字化变化	总分变化
wa_replied	+2	+1	+3
wa_not_replied_3x	-5	0	-5
visit_agreed	+5	0	+5
visit_refused	-8	0	-8
trial_ordered	+5	+3	+8
trial_rejected	-3	0	-3
cooperation_signed	+10	+5	+15
referral_given	+5	+3	+8
display_refused	-10	0	-10
sales_data_shared	+3	+2	+5
4.2 Python 实现
python
def update_score_from_feedback(warung_id: str, feedback_type: str) -> Dict[str, Any]:
    """
    根据销售反馈更新 Warung 评分
    """
    FEEDBACK_DELTAS = {
        'wa_replied': {'cooperation': +2, 'digital': +1, 'total': +3},
        'wa_not_replied_3x': {'cooperation': -5, 'digital': 0, 'total': -5},
        'visit_agreed': {'cooperation': +5, 'digital': 0, 'total': +5},
        'visit_refused': {'cooperation': -8, 'digital': 0, 'total': -8},
        'trial_ordered': {'cooperation': +5, 'digital': +3, 'total': +8},
        'trial_rejected': {'cooperation': -3, 'digital': 0, 'total': -3},
        'cooperation_signed': {'cooperation': +10, 'digital': +5, 'total': +15},
        'referral_given': {'cooperation': +5, 'digital': +3, 'total': +8},
        'display_refused': {'cooperation': -10, 'digital': 0, 'total': -10},
        'sales_data_shared': {'cooperation': +3, 'digital': +2, 'total': +5},
    }

    delta = FEEDBACK_DELTAS.get(feedback_type, {'cooperation': 0, 'digital': 0, 'total': 0})

    # 获取 Warung 数据
    warung = get_warung(warung_id)

    # 更新配合度和数字化分数
    warung['cooperation_score'] = max(0, min(100, warung.get('cooperation_score', 50) + delta['cooperation']))
    warung['digital_score'] = max(0, min(100, warung.get('digital_score', 50) + delta['digital']))

    # 重新计算总分
    new_score_result = calculate_final_score(warung)
    warung['final_score'] = new_score_result['total_score']

    # 保存并记录历史
    save_warung(warung)
    log_score_change(warung_id, feedback_type, delta, new_score_result)

    return {
        'warung_id': warung_id,
        'old_score': new_score_result['total_score'] - delta['total'],
        'new_score': new_score_result['total_score'],
        'delta': delta,
        'feedback_applied': feedback_type
    }
5. WhatsApp 话术模板
黄金 Warung（80-100分）
text
Halo Kak [Nama],

Kami dari [Nama Perusahaan] — tim kami lagi cari mitra warung premium di area [lokasi] untuk program [nama program].

Kami lihat warung kakak posisinya strategis dan cocok jadi mitra.

✅ Keuntungan:
- Produk [nama produk] eksklusif untuk 3 warung terdekat
- Margin 20-30% lebih tinggi dari produk biasa
- Dukungan display & promo gratis

Boleh kami datang besok untuk diskusi lebih lanjut?

Terima kasih 🙏
白银 Warung（60-79分）
text
Halo Kak [Nama],

Kami dari [Nama Perusahaan], supplier [kategori produk] di area [kota].

Saat ini kami sedang buka program percobaan untuk warung-warung terpilih — produk [nama produk] dengan harga grosir khusus + sampel gratis.

Boleh kami kirim info selengkapnya via WA?

Terima kasih 🙏
潜力 Warung（40-59分）
text
Halo Kak [Nama],

Kami dari [Nama Perusahaan] — komunitas supplier & warung di [kota].

Kami rutin bagi-bagi info produk baru, promo grosir, dan pelatihan usaha.

Kak boleh join grup WA kami? Gratis dan tidak ada kewajiban.

Kalau berminat, reply "MAU" ya 🙏
文档结束

text


# 文档四：`docs/FRONTEND_PAGES.md`


```markdown
# 🖥️ WarungScout 前端页面设计

**版本**：v1.0.0
**日期**：2026年8月23日


## 1. 页面架构
┌─────────────────────────────────────────────────────────────────┐
│ WarungScout 网站 │
├──────────────────────────────┬──────────────────────────────────┤
│ 对外营销视图 (公开) │ 对内销售作战室 (需登录) │
│ │ │
│ • 脱敏榜单 │ • Warung 列表 (评分/排序/筛选) │
│ • 区域热力图 │ • Warung 详情 (雷达图+步骤看板) │
│ • 数据总览 │ • 待办看板 (高/中/低优先级) │
│ • "申请演示" 入口 │ • 反馈提交 (完成动作) │
└──────────────────────────────┴──────────────────────────────────┘

text


## 2. 对外营销视图（公开）

### 2.1 页面组成

| 模块 | 内容 | 目的 |
| :--- | :--- | :--- |
| **Hero 区域** | 一句话介绍 + CTA 按钮 | 吸引访客继续浏览 |
| **数据总览** | 已覆盖 Warung 数量、黄金/白银占比 | 展示数据能力 |
| **区域热力图** | 印尼地图展示 Warung 分布密度 | 展示覆盖广度 |
| **脱敏榜单** | Top 10 黄金 Warung（脱敏） | 展示数据质量 |
| **CTA** | "申请演示" / "获取数据报告" | 转化线索 |

### 2.2 脱敏规则

| 字段 | 公开显示 | 示例 |
| :--- | :--- | :--- |
| Warung 名称 | 首字母 + *** | "Warung B***" |
| 等级 | 完整显示 | 🔴 黄金 |
| 区域 | 完整显示 | Bali, Canggu |
| 评分 | 不显示 | — |
| 联系方式 | 不显示 | — |

### 2.3 页面截图参考
┌─────────────────────────────────────────────────────────────────┐
│ 🏪 WarungScout — 印尼 Warung 渠道质量指数 │
│ ──────────────────────────────────────────────────────────── │
│ 覆盖 500+ 高潜力 Warung · 黄金 Warung 占比 15% │
│ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 区域热力图（印尼地图） │ │
│ │ 雅加达 ████████ 泗水 ██████ 巴厘岛 ██████ │ │
│ │ 万隆 █████ 棉兰 ████ │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ 🔴 黄金 Warung Top 10（脱敏） │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ #1 Warung B*** Bali, Canggu 等级: 🔴 黄金 │ │
│ │ #2 Warung M*** Jakarta Selatan 等级: 🔴 黄金 │ │
│ │ #3 Warung S*** Surabaya 等级: 🔴 黄金 │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ [📊 获取完整数据报告] [📞 联系销售团队] │
└─────────────────────────────────────────────────────────────────┘

text


## 3. 对内销售作战室（需登录）

### 3.1 页面组成

| 页面 | 内容 | 核心功能 |
| :--- | :--- | :--- |
| **Dashboard** | 今日待办、关键指标、最近动态 | 一目了然掌握全局 |
| **Warung 列表** | 评分/等级/步骤列表 + 筛选 + 排序 | 找到需要跟进的 Warung |
| **Warung 详情** | 7维雷达图 + 步骤看板 + 下一步建议 | 指导具体销售动作 |
| **反馈提交** | 完成动作 + 记录结果 | 触发评分更新 |

### 3.2 Dashboard 页面
┌─────────────────────────────────────────────────────────────────┐
│ 🏪 WarungScout 销售作战室 👤 销售团队 │
│ ──────────────────────────────────────────────────────────── │
│ 📊 今日待办 (5) │
│ 🔴 高优先级 (2) ── 🟡 中优先级 (3) ── 🟢 低优先级 (0) │
│ │
│ 关键指标 │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ 总 Warung │ │ 黄金 │ │ 白银 │ │ 本周新增 │ │
│ │ 520 │ │ 78 │ │ 156 │ │ 23 │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│ │
│ 待办任务 │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🔴 Warung Bu Siti → WA破冰 (截止: 今日) [立即联系] │ │
│ │ 🔴 Warung Pak Made → 拜访 (截止: 明日) [安排拜访] │ │
│ │ 🟡 Warung Bu Dewi → WA跟进 (截止: 3天后) [发送消息] │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

text

### 3.3 Warung 列表页面
┌─────────────────────────────────────────────────────────────────┐
│ 📋 Warung 列表 🔍 [搜索] [+ 导入数据] │
│ ──────────────────────────────────────────────────────────── │
│ 筛选: [全部等级 ▼] [全部步骤 ▼] [区域 ▼] [按分数排序 ▼] │
│ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 等级 │ 名称 │ 区域 │ 分数 │ 当前步骤 │ 操作 │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ 🔴 │ Bu Siti │ Bali │ 87 │ 拜访 │ [详情] │ │
│ │ 🔴 │ Pak Made │ Jakarta │ 82 │ 破冰 │ [详情] │ │
│ │ 🟡 │ Bu Dewi │ Surabaya │ 75 │ 未接触 │ [详情] │ │
│ │ 🟢 │ Pak Agus │ Bandung │ 55 │ 推品 │ [详情] │ │
│ │ ⚪ │ Bu Rini │ Medan │ 38 │ 未接触 │ [详情] │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ 共 520 条 [< 1 2 3 ... 26 >] │
└─────────────────────────────────────────────────────────────────┘

text

### 3.4 Warung 详情页面
┌─────────────────────────────────────────────────────────────────┐
│ ← 返回列表 │
│ │
│ 🏪 Warung Bu Siti │
│ 📍 Jl. Raya Canggu No. 45, Bali │
│ 📞 +62 812-3456-7890 │
│ │
│ 📊 综合评分: 87 🔴 黄金 │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 位置 ████████████████████░ 85 │ │
│ │ 活跃度 ██████████████░░░░░░ 70 │ │
│ │ 竞争 ███████████████████░ 90 │ │
│ │ 配合度 ████████████████░░░░ 80 │ │
│ │ 数字化 ███████████████░░░░░ 75 │ │
│ │ 画像 █████████████░░░░░░░ 65 │ │
│ │ 区域 ██████████████████░░ 85 │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ ⚡ 当前阶段: Step 2 - 拜访 │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ✅ Step 1: 首次破冰 已完成 (2026-08-15) │ │
│ │ → 店主回复: "好的，可以来聊聊" │ │
│ │ │ │
│ │ 🔵 Step 2: 初次拜访 进行中 │ │
│ │ → 建议: 安排地推团队上门拜访 │ │
│ │ → 截止: 2026-08-22 (还有 3 天) │ │
│ │ → [📋 拜访话术] [📞 电话联系] [✅ 完成拜访] │ │
│ │ │ │
│ │ ⚪ Step 3: 推品试销 待开始 │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ 📝 历史记录 [查看全部 →] │
│ ├─ 2026-08-15 WA 破冰消息已发送, 店主回复 │
│ ├─ 2026-08-12 系统初筛, 评分 72, 建议联系 │
│ └─ 2026-08-10 数据导入完成 │
└─────────────────────────────────────────────────────────────────┘

text


## 4. 技术实现

### 4.1 前端技术栈

| 组件 | 选型 | 说明 |
| :--- | :--- | :--- |
| 框架 | React 19 + TypeScript | 现代 UI 框架 |
| 构建 | Vite | 极速构建 |
| UI 组件 | shadcn/ui | 美观、可定制 |
| 图表 | Recharts | 雷达图、柱状图 |
| 地图 | Leaflet / MapLibre | 印尼区域热力图 |
| 状态 | Zustand | 轻量状态管理 |
| 数据 | TanStack Query | 缓存 + 自动重试 |
| 认证 | JWT | 登录验证 |

### 4.2 页面路由

| 路由 | 页面 | 权限 |
| :--- | :--- | :--- |
| `/` | 对外营销视图 | 公开 |
| `/dashboard` | 销售作战室 | 需登录 |
| `/warungs` | Warung 列表 | 需登录 |
| `/warungs/:id` | Warung 详情 | 需登录 |
| `/tasks` | 待办看板 | 需登录 |
| `/login` | 登录页 | 公开 |


**文档结束**
文档五：docs/DATABASE_SCHEMA.md
markdown
# 🗄️ WarungScout 数据库设计

**版本**：v1.0.0
**日期**：2026年8月23日
**数据库**：Cloudflare D1 (SQLite)


## 1. 核心表结构

### 1.1 warungs（Warung 主表）

```sql
CREATE TABLE warungs (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    region TEXT,
    city TEXT,

    -- 7个维度的原始评分（0-100）
    location_score INTEGER DEFAULT 50,
    activity_score INTEGER DEFAULT 50,
    competition_score INTEGER DEFAULT 50,
    cooperation_score INTEGER DEFAULT 50,
    digital_score INTEGER DEFAULT 50,
    owner_score INTEGER DEFAULT 50,
    region_score INTEGER DEFAULT 50,

    -- 综合评分
    final_score INTEGER DEFAULT 50,
    grade TEXT CHECK(grade IN ('gold', 'silver', 'potential', 'normal')),

    -- 销售步骤（0-5）
    sales_step INTEGER DEFAULT 0 CHECK(sales_step BETWEEN 0 AND 5),
    step_status TEXT DEFAULT 'pending' CHECK(step_status IN ('pending', 'in_progress', 'done', 'blocked')),

    -- 冷却状态
    block_reason TEXT,
    cold_until INTEGER,  -- Unix timestamp

    -- 统计字段
    outreach_count INTEGER DEFAULT 0,
    no_response_count INTEGER DEFAULT 0,
    visit_count INTEGER DEFAULT 0,
    visit_result TEXT CHECK(visit_result IN ('success', 'pending', 'refused', NULL)),
    trial_status TEXT DEFAULT 'pending' CHECK(trial_status IN ('pending', 'success', 'failed')),

    -- 时间戳
    last_action_at INTEGER,  -- Unix timestamp
    next_action_at INTEGER,  -- Unix timestamp
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- 索引
CREATE INDEX idx_warungs_grade ON warungs(grade);
CREATE INDEX idx_warungs_sales_step ON warungs(sales_step);
CREATE INDEX idx_warungs_final_score ON warungs(final_score);
CREATE INDEX idx_warungs_region ON warungs(region);
CREATE INDEX idx_warungs_next_action_at ON warungs(next_action_at);
CREATE INDEX idx_warungs_created_at ON warungs(created_at);
1.2 score_history（评分历史）
sql
CREATE TABLE score_history (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    score_before INTEGER NOT NULL,
    score_after INTEGER NOT NULL,
    delta_cooperation INTEGER,
    delta_digital INTEGER,
    delta_total INTEGER,

    feedback_type TEXT CHECK(feedback_type IN (
        'wa_replied', 'wa_not_replied_3x',
        'visit_agreed', 'visit_refused',
        'trial_ordered', 'trial_rejected',
        'cooperation_signed',
        'referral_given', 'display_refused',
        'sales_data_shared'
    )),

    reason TEXT,
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_score_history_warung_id ON score_history(warung_id);
CREATE INDEX idx_score_history_created_at ON score_history(created_at);
1.3 outreach_logs（触达记录）
sql
CREATE TABLE outreach_logs (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    channel TEXT CHECK(channel IN ('whatsapp', 'call', 'visit')),
    template TEXT,
    message TEXT,

    status TEXT CHECK(status IN ('sent', 'delivered', 'read', 'replied', 'no_response')),
    response TEXT,

    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_outreach_logs_warung_id ON outreach_logs(warung_id);
CREATE INDEX idx_outreach_logs_created_at ON outreach_logs(created_at);
1.4 warung_history（全量操作日志）
sql
CREATE TABLE warung_history (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    action_type TEXT CHECK(action_type IN ('score_update', 'step_change', 'feedback', 'status_change')),
    old_value TEXT,
    new_value TEXT,
    note TEXT,

    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_warung_history_warung_id ON warung_history(warung_id);
CREATE INDEX idx_warung_history_created_at ON warung_history(created_at);
2. 初始数据
2.1 城市分级数据
sql
-- 印尼城市分级表
CREATE TABLE city_tiers (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    city_name TEXT NOT NULL,
    tier INTEGER CHECK(tier IN (1, 2, 3)),
    region_score INTEGER CHECK(region_score BETWEEN 0 AND 100),
    created_at INTEGER DEFAULT (unixepoch())
);

INSERT INTO city_tiers (city_name, tier, region_score) VALUES
('Jakarta', 1, 100),
('Surabaya', 1, 80),
('Medan', 1, 80),
('Bandung', 1, 80),
('Yogyakarta', 2, 60),
('Semarang', 2, 60),
('Makassar', 2, 60),
('Bali', 2, 60),
('Other', 3, 40);
3. 字段说明
3.1 grade（等级）
值	含义	分数范围
gold	黄金	80-100
silver	白银	60-79
potential	潜力	40-59
normal	普通	< 40
3.2 sales_step（销售步骤）
值	含义
0	未接触
1	首次破冰
2	初次拜访
3	推品试销
4	深度合作
5	长期运营
3.3 step_status（步骤状态）
值	含义
pending	待开始
in_progress	进行中
done	已完成
blocked	受阻/暂停
3.4 feedback_type（反馈类型）
值	含义	配合度变化	数字化变化	总分变化
wa_replied	WA 回复	+2	+1	+3
wa_not_replied_3x	3次无回复	-5	0	-5
visit_agreed	同意拜访	+5	0	+5
visit_refused	拒绝拜访	-8	0	-8
trial_ordered	试销下单	+5	+3	+8
trial_rejected	拒绝试销	-3	0	-3
cooperation_signed	签约合作	+10	+5	+15
referral_given	转介绍	+5	+3	+8
display_refused	拒绝陈列	-10	0	-10
sales_data_shared	分享销售数据	+3	+2	+5
4. 核心 SQL 查询
4.1 查询今日待办（高优先级）
sql
SELECT
    id,
    name,
    phone,
    final_score,
    grade,
    sales_step,
    next_action_at
FROM warungs
WHERE
    step_status = 'in_progress'
    AND next_action_at <= unixepoch()
    AND grade IN ('gold', 'silver')
    AND cold_until IS NULL
ORDER BY final_score DESC
LIMIT 25;
4.2 查询统计概览
sql
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN grade = 'gold' THEN 1 ELSE 0 END) as gold_count,
    SUM(CASE WHEN grade = 'silver' THEN 1 ELSE 0 END) as silver_count,
    SUM(CASE WHEN grade = 'potential' THEN 1 ELSE 0 END) as potential_count,
    SUM(CASE WHEN grade = 'normal' THEN 1 ELSE 0 END) as normal_count,
    AVG(final_score) as avg_score
FROM warungs;
4.3 按步骤分布
sql
SELECT
    sales_step,
    COUNT(*) as count
FROM warungs
WHERE cold_until IS NULL
GROUP BY sales_step
ORDER BY sales_step;
5. 数据迁移脚本
5.1 从 warung-network-mvp 导入
sql
-- 假设从 CSV 导入
-- 示例：使用 Cloudflare D1 的 import 功能

-- 或使用 Python 脚本批量插入
5.2 迁移模板
sql
-- migrations/001_init.sql
-- 包含所有 CREATE TABLE 语句

-- migrations/002_seed_cities.sql
-- 包含城市数据

-- migrations/003_seed_sample_warungs.sql
-- 包含示例 Warung 数据（用于测试）
文档结束

text

---

以上是 `docs/` 文件夹的全部内容。五个文档已完整就绪，可以直接复制到你的 GitHub 仓库中。需要我再调整哪份文档的内容或格式吗？


## 3. 系统架构图
