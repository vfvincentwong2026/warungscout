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

**计算方式**：累加所有匹配设施的加分，满分 25 分，超过 25 分按 25 分计。


### 维度2：店主活跃度（权重 20%）

| 指标 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| Google Maps 评分 ≥ 4.0 且评论数 ≥ 50 | +10 | Google Maps API |
| Google Maps 评分 ≥ 3.5 且评论数 ≥ 20 | +5 | Google Maps API |
| 在 WA 群内活跃发言（近7天≥3次） | +10 | WA 群运营记录 |
| 曾配合过地推活动 | +8 | 历史记录 |
| 主动询问过新品/促销 | +7 | 历史记录 |

**计算方式**：累加所有匹配指标的加分，满分 20 分，超过 20 分按 20 分计。


### 维度3：竞争密度（权重 15%）

| 竞品 Warung 数量（500m 内） | 得分 | 数据来源 |
| :--- | :--- | :--- |
| 0-2 家 | 15（满分） | Google Maps Places API |
| 3-5 家 | 12 | Google Maps Places API |
| 6-10 家 | 8 | Google Maps Places API |
| >10 家 | 5 | Google Maps Places API |

**计算方式**：直接查表得分，满分 15 分。


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

**计算方式**：累加所有匹配指标的加分，再扣除扣分项，满分 20 分，额外加分（推荐）不占用满分额度，作为 bonus。

**注意**：新抓取的 Warung 无历史记录时，配合度默认 50 分（中性），等待销售首次反馈后更新。


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

**计算方式**：累加所有匹配指标的加分，满分 20 分，额外加分（主动意愿）不占用满分额度，作为 bonus。

**注意**：新抓取的 Warung 无历史记录时，数字化接受度默认 50 分（中性），等待销售首次接触后更新。


### 维度6：店主画像匹配（权重 5%）

| 画像特征 | 加分 | 数据来源 |
| :--- | :--- | :--- |
| 年龄 20-35 岁 | +3 | 访谈记录 |
| 有扩张/开分店计划 | +2 | 访谈记录 |
| 家庭主要收入来源 | +2 | 访谈记录 |
| 女性店主（沟通更顺畅） | +2 | 访谈记录 |
| 高中以上学历 | +2 | 访谈记录 |
| 本地人（非流动人口） | +2 | 访谈记录 |

**计算方式**：累加所有匹配指标的加分，满分 13 分，封顶 10 分。

**注意**：新抓取的 Warung 无访谈记录时，店主画像默认 50 分（中性），等待销售首次拜访后更新。


### 维度7：区域潜力（权重 5%）

| 城市层级 | 得分 | 说明 |
| :--- | :--- | :--- |
| **Tier 1**：雅加达 | 10 | 大雅加达都市圈 |
| **Tier 1**：泗水、棉兰、万隆 | 8 | 核心省会 |
| **Tier 2**：日惹、三宝垄、望加锡 | 6 | 重要城市 |
| **Tier 3**：其他城市 | 4 | 非核心区域 |

**计算方式**：直接查表得分，满分 10 分。

**注意**：从 Google Maps 抓取时，根据地址自动识别城市并匹配层级。


## 3. 新抓取 Warung 的初始评分策略

当 Warung 从 Google Maps 首次抓取导入时，并非所有维度都有数据。采用以下策略：

| 维度 | 初始值来源 | 说明 |
| :--- | :--- | :--- |
| 位置价值 | Google Maps 周边设施分析 | 自动计算 |
| 活跃度 | Google Maps 评分 + 评论数 | 自动计算 |
| 竞争密度 | Google Maps Places API | 自动计算 |
| 配合度 | 默认 50 分 | 等待销售首次反馈 |
| 数字化接受度 | 默认 50 分 | 等待销售首次接触 |
| 店主画像 | 默认 50 分 | 等待销售首次拜访 |
| 区域潜力 | 地址自动识别 | 自动计算 |

**初次评分后**：部分维度（配合度/数字化/画像）采用中性分，确保新 Warung 不会被误判为极低分而被忽略。随着销售团队的实际接触和反馈，这些维度会逐步调整为真实分数。


## 4. 分级标准

| 分数区间 | 等级 | 配合度特征 | 推荐触达方式 |
| :--- | :--- | :--- | :--- |
| 80-100 | 🔴 **黄金** | 高配合度+高数字化 | 立即 WA 推品 + 地推拜访 |
| 60-79 | 🟡 **白银** | 中高配合度+中数字化 | WA 破冰，先培养再推品 |
| 40-59 | 🟢 **潜力** | 中低配合度+低数字化 | 地推拜访，当面建立信任 |
| < 40 | ⚪ **普通** | 低配合度+低数字化 | 暂缓触达，沉淀数据 |


## 5. 评分输出示例

```json
{
  "warung_name": "Warung Bu Siti",
  "location": "Jl. Raya Canggu No. 45, Bali",
  "source": "google_maps",
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
  "data_completeness": {
    "from_google_maps": ["location", "activity", "competition", "region"],
    "pending_sales_input": ["cooperation", "digital", "owner"]
  },
  "top_actions": [
    "优先联系，配合度高+数字化接受度好",
    "可直接通过 WA 推送新品信息，预期回复率高"
  ]
}
6. Python 实现
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
    返回 0-100 的分数，在加权时乘以权重 0.15
    """
    # 如果是新抓取的 Warung，无历史记录，默认 50 分
    if warung.get('source') == 'google_maps' and warung.get('no_history', True):
        return 50

    score = 0

    # 1. 历史响应率 (0-40分)
    reply_rate = warung.get('reply_rate', 0)
    if reply_rate > 0.7:
        score += 40
    elif reply_rate > 0.3:
        score += 20
    elif reply_rate > 0:
        score += 5

    # 2. 地推反馈 (0-35分，可扣分)
    visit_feedback = warung.get('visit_feedback')
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


def calculate_activity_score(warung: Dict[str, Any]) -> int:
    """
    计算活跃度得分 (0-100)
    结合 Google Maps 数据和历史记录
    """
    score = 0

    # 从 Google Maps 获取的评分和评论数
    gm_rating = warung.get('gm_rating', 0)
    gm_reviews = warung.get('gm_reviews', 0)

    if gm_rating >= 4.0 and gm_reviews >= 50:
        score += 10
    elif gm_rating >= 3.5 and gm_reviews >= 20:
        score += 5

    # WA 群活跃度
    if warung.get('wa_active', False):
        score += 10

    # 历史活动参与
    if warung.get('participated_promo', False):
        score += 8

    return min(score, 20) * 5  # 映射到 0-100
