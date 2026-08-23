# ============================================================
# WarungScout 评分引擎
# 功能: 7 维度综合评分 + 分级
# 版本: v1.0.0
# ============================================================

import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import math

# ============================================================
# 1. 评分权重配置
# ============================================================

SCORE_WEIGHTS = {
    'location': 0.25,      # 地理位置价值
    'activity': 0.20,      # 店主活跃度
    'competition': 0.15,   # 竞争密度
    'cooperation': 0.15,   # 配合度
    'digital': 0.15,       # 数字化接受度
    'owner': 0.05,         # 店主画像匹配
    'region': 0.05,        # 区域潜力
}

# 分级阈值
GRADE_THRESHOLDS = {
    'gold': {'min': 80, 'label': '黄金', 'emoji': '🔴', 'priority': 1},
    'silver': {'min': 60, 'label': '白银', 'emoji': '🟡', 'priority': 2},
    'potential': {'min': 40, 'label': '潜力', 'emoji': '🟢', 'priority': 3},
    'normal': {'min': 0, 'label': '普通', 'emoji': '⚪', 'priority': 4},
}

# 城市分级数据
CITY_TIERS = {
    1: {'label': 'Tier 1', 'score': 100, 'cities': ['Jakarta', 'Surabaya', 'Medan', 'Bandung']},
    2: {'label': 'Tier 2', 'score': 60, 'cities': ['Yogyakarta', 'Semarang', 'Makassar', 'Bali']},
    3: {'label': 'Tier 3', 'score': 40, 'cities': []},
}


# ============================================================
# 2. 各维度评分函数
# ============================================================

def calculate_location_score(warung: Dict[str, Any]) -> int:
    """
    计算地理位置价值得分 (0-100)
    
    基于周边设施加分:
    - 学校 (中小学/大学): +10
    - 工厂/工业区: +10
    - 办公区/写字楼: +8
    - 住宅区 (中高端): +5
    - 交通枢纽 (车站): +7
    
    数据来源: Google Maps Places API
    """
    score = 0
    
    # 从 Google Maps 获取的周边设施类型
    gm_types = warung.get('gm_types', [])
    if isinstance(gm_types, str):
        try:
            gm_types = json.loads(gm_types)
        except:
            gm_types = []
    
    # 周边设施加分
    facility_scores = {
        'school': 10,
        'university': 10,
        'factory': 10,
        'industrial': 10,
        'office': 8,
        'residential': 5,
        'transit_station': 7,
        'bus_station': 7,
        'train_station': 7,
    }
    
    for facility, points in facility_scores.items():
        if any(facility in str(t).lower() for t in gm_types):
            score += points
    
    # 如果地址中包含高价值区域关键词
    address = warung.get('address', '').lower()
    high_value_keywords = ['central', 'downtown', 'business district', 'commercial']
    for kw in high_value_keywords:
        if kw in address:
            score += 5
            break
    
    # 限制满分 100
    return min(100, score)


def calculate_activity_score(warung: Dict[str, Any]) -> int:
    """
    计算店主活跃度得分 (0-100)
    
    指标:
    - Google Maps 评分 + 评论数 (0-50分)
    - WA 群活跃度 (0-30分)
    - 历史活动参与 (0-20分)
    """
    score = 0
    
    # 1. Google Maps 评分 + 评论数 (0-50分)
    rating = warung.get('gm_rating', 0)
    reviews = warung.get('gm_reviews', 0)
    
    if rating >= 4.5 and reviews >= 100:
        score += 50
    elif rating >= 4.0 and reviews >= 50:
        score += 40
    elif rating >= 4.0 and reviews >= 20:
        score += 30
    elif rating >= 3.5 and reviews >= 10:
        score += 20
    elif rating >= 3.0:
        score += 10
    else:
        score += 5
    
    # 2. WA 群活跃度 (0-30分)
    if warung.get('wa_active', False):
        score += 20
    
    # 近7天发言次数
    recent_messages = warung.get('wa_recent_messages', 0)
    if recent_messages >= 5:
        score += 10
    elif recent_messages >= 3:
        score += 5
    
    # 3. 历史活动参与 (0-20分)
    if warung.get('participated_promo', False):
        score += 15
    if warung.get('active_inquiry', False):
        score += 5
    
    return min(100, score)


def calculate_competition_score(warung: Dict[str, Any]) -> int:
    """
    计算竞争密度得分 (0-100)
    
    基于 500m 内的竞品 Warung 数量
    数据来源: Google Maps Places API
    """
    # 从 Google Maps 或缓存获取竞品数量
    competitors_count = warung.get('competitors_count', 0)
    
    if competitors_count <= 2:
        return 100
    elif competitors_count <= 5:
        return 80
    elif competitors_count <= 10:
        return 60
    elif competitors_count <= 20:
        return 40
    else:
        return 20


def calculate_cooperation_score(warung: Dict[str, Any]) -> int:
    """
    计算配合度得分 (0-100)
    
    指标:
    - 历史响应率 (0-40分)
    - 地推反馈 (0-35分)
    - 合作历史 (0-25分)
    
    注意: 新抓取的 Warung (来自 Google Maps) 默认 50 分
    """
    # 如果是新抓取的 Warung，无历史记录，默认 50 分
    source = warung.get('source', 'manual')
    data_completeness = warung.get('data_completeness', 'basic')
    
    if source == 'google_maps' and data_completeness == 'basic':
        return 50
    
    score = 0
    
    # 1. 历史响应率 (0-40分)
    reply_rate = warung.get('reply_rate', 0)  # 0.0 - 1.0
    total_contacts = warung.get('total_contacts', 0)
    
    if total_contacts > 0:
        if reply_rate >= 0.8:
            score += 40
        elif reply_rate >= 0.5:
            score += 30
        elif reply_rate >= 0.3:
            score += 20
        elif reply_rate > 0:
            score += 10
        else:
            score += 5
    else:
        # 无联系记录，中性分
        score += 20
    
    # 2. 地推反馈 (0-35分)
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


def calculate_digital_score(warung: Dict[str, Any]) -> int:
    """
    计算数字化接受度得分 (0-100)
    
    指标:
    - 支付方式 (0-30分)
    - WA 使用习惯 (0-30分)
    - 设备与工具 (0-20分)
    - 主动意愿 (0-20分)
    """
    # 如果是新抓取的 Warung，默认 50 分
    source = warung.get('source', 'manual')
    data_completeness = warung.get('data_completeness', 'basic')
    
    if source == 'google_maps' and data_completeness == 'basic':
        return 50
    
    score = 0
    
    # 1. 支付方式 (0-30分)
    payment_methods = warung.get('payment_methods', [])
    if isinstance(payment_methods, str):
        try:
            payment_methods = json.loads(payment_methods)
        except:
            payment_methods = []
    
    digital_payments = ['qris', 'ovo', 'gopay', 'dana', 'shopee_pay', 'linkaja']
    for payment in digital_payments:
        if any(payment in p.lower() for p in payment_methods):
            score += 6  # 每种数字支付 +6分，最多30分
    
    if len(payment_methods) == 0:
        score += 5  # 不清楚，给基础分
    
    # 2. WA 使用习惯 (0-30分)
    wa_response_time = warung.get('wa_response_time')  # 'fast' | 'medium' | 'slow'
    if wa_response_time == 'fast':
        score += 30
    elif wa_response_time == 'medium':
        score += 15
    elif wa_response_time == 'slow':
        score += 5
    else:
        score += 10  # 未知，给基础分
    
    # 3. 设备与工具 (0-20分)
    if warung.get('smartphone_owner', False):
        score += 10
    if warung.get('can_use_camera', False):
        score += 5
    if warung.get('can_use_social_media', False):
        score += 5
    
    # 4. 主动意愿 (0-20分)
    if warung.get('interested_digital_tools', False):
        score += 10
    if warung.get('uses_online_order_app', False):
        score += 10
    
    return min(100, score)


def calculate_owner_score(warung: Dict[str, Any]) -> int:
    """
    计算店主画像匹配得分 (0-100)
    
    画像特征:
    - 年龄 20-35 岁 (高)
    - 有扩张/开分店计划
    - 家庭主要收入来源
    - 女性店主
    - 高中以上学历
    - 本地人
    """
    # 如果是新抓取的 Warung，默认 50 分
    source = warung.get('source', 'manual')
    data_completeness = warung.get('data_completeness', 'basic')
    
    if source == 'google_maps' and data_completeness == 'basic':
        return 50
    
    score = 0
    
    # 每个特征 +10-20分
    features = [
        ('age_20_35', 15),
        ('expansion_plan', 15),
        ('is_primary_income', 10),
        ('is_female', 10),
        ('education_above_highschool', 10),
        ('is_local', 10),
        ('business_experience_years', 5),  # 每5年 +5分
    ]
    
    for feature, points in features:
        if warung.get(feature, False):
            score += points
    
    # 经营年限加分
    years = warung.get('business_years', 0)
    if years >= 10:
        score += 15
    elif years >= 5:
        score += 10
    elif years >= 2:
        score += 5
    
    return min(100, score)


def calculate_region_score(warung: Dict[str, Any]) -> int:
    """
    计算区域潜力得分 (0-100)
    
    根据城市 Tier 自动识别:
    - Tier 1: 雅加达, 泗水, 棉兰, 万隆 → 100分
    - Tier 2: 日惹, 三宝垄, 望加锡, 巴厘岛 → 60分
    - Tier 3: 其他城市 → 40分
    """
    city = warung.get('city', '')
    region = warung.get('region', '')
    
    # 关键词匹配
    city_lower = (city + ' ' + region).lower()
    
    # Tier 1 城市
    tier1_cities = ['jakarta', 'surabaya', 'medan', 'bandung']
    for c in tier1_cities:
        if c in city_lower:
            return 100
    
    # Tier 2 城市
    tier2_cities = ['yogyakarta', 'jogja', 'semarang', 'makassar', 'bali']
    for c in tier2_cities:
        if c in city_lower:
            return 60
    
    # 默认 Tier 3
    return 40


# ============================================================
# 3. 综合评分与分级
# ============================================================

def calculate_final_score(warung: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算 Warung 的 7 维综合评分
    
    Args:
        warung: Warung 数据字典
        
    Returns:
        {
            'total_score': int,          # 0-100
            'grade': str,                # gold | silver | potential | normal
            'grade_label': str,          # 黄金 | 白银 | 潜力 | 普通
            'grade_emoji': str,          # 🔴 | 🟡 | 🟢 | ⚪
            'breakdown': dict            # 各维度得分详情
        }
    """
    # 1. 计算各维度得分
    location_score = calculate_location_score(warung)
    activity_score = calculate_activity_score(warung)
    competition_score = calculate_competition_score(warung)
    cooperation_score = calculate_cooperation_score(warung)
    digital_score = calculate_digital_score(warung)
    owner_score = calculate_owner_score(warung)
    region_score = calculate_region_score(warung)
    
    # 2. 加权计算总分
    total = (
        location_score * SCORE_WEIGHTS['location'] +
        activity_score * SCORE_WEIGHTS['activity'] +
        competition_score * SCORE_WEIGHTS['competition'] +
        cooperation_score * SCORE_WEIGHTS['cooperation'] +
        digital_score * SCORE_WEIGHTS['digital'] +
        owner_score * SCORE_WEIGHTS['owner'] +
        region_score * SCORE_WEIGHTS['region']
    )
    
    final_score = round(total)
    
    # 3. 分级
    if final_score >= 80:
        grade = 'gold'
    elif final_score >= 60:
        grade = 'silver'
    elif final_score >= 40:
        grade = 'potential'
    else:
        grade = 'normal'
    
    grade_info = GRADE_THRESHOLDS[grade]
    
    # 4. 构建返回结果
    return {
        'total_score': final_score,
        'grade': grade,
        'grade_label': grade_info['label'],
        'grade_emoji': grade_info['emoji'],
        'breakdown': {
            'location': {
                'score': location_score,
                'weight': SCORE_WEIGHTS['location'],
                'weighted': round(location_score * SCORE_WEIGHTS['location'], 2)
            },
            'activity': {
                'score': activity_score,
                'weight': SCORE_WEIGHTS['activity'],
                'weighted': round(activity_score * SCORE_WEIGHTS['activity'], 2)
            },
            'competition': {
                'score': competition_score,
                'weight': SCORE_WEIGHTS['competition'],
                'weighted': round(competition_score * SCORE_WEIGHTS['competition'], 2)
            },
            'cooperation': {
                'score': cooperation_score,
                'weight': SCORE_WEIGHTS['cooperation'],
                'weighted': round(cooperation_score * SCORE_WEIGHTS['cooperation'], 2)
            },
            'digital': {
                'score': digital_score,
                'weight': SCORE_WEIGHTS['digital'],
                'weighted': round(digital_score * SCORE_WEIGHTS['digital'], 2)
            },
            'owner': {
                'score': owner_score,
                'weight': SCORE_WEIGHTS['owner'],
                'weighted': round(owner_score * SCORE_WEIGHTS['owner'], 2)
            },
            'region': {
                'score': region_score,
                'weight': SCORE_WEIGHTS['region'],
                'weighted': round(region_score * SCORE_WEIGHTS['region'], 2)
            }
        },
        'priority': grade_info['priority'],
        'data_completeness': warung.get('data_completeness', 'basic')
    }


def batch_calculate_scores(warungs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量计算评分
    
    Args:
        warungs: Warung 数据列表
        
    Returns:
        带评分的 Warung 列表（按分数降序排列）
    """
    result = []
    for warung in warungs:
        score_result = calculate_final_score(warung)
        # 将评分合并到 warung 数据中
        warung_copy = warung.copy()
        warung_copy.update(score_result)
        result.append(warung_copy)
    
    # 按总分降序排列
    result.sort(key=lambda x: x.get('total_score', 0), reverse=True)
    return result


# ============================================================
# 4. 辅助函数
# ============================================================

def get_score_summary(score_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成评分摘要（用于对外展示）
    """
    breakdown = score_result.get('breakdown', {})
    
    return {
        'total_score': score_result.get('total_score', 0),
        'grade': score_result.get('grade', 'normal'),
        'grade_label': score_result.get('grade_label', '普通'),
        'grade_emoji': score_result.get('grade_emoji', '⚪'),
        'strength_dimensions': _get_top_dimensions(breakdown, 3, 'desc'),
        'improvement_dimensions': _get_top_dimensions(breakdown, 3, 'asc'),
    }


def _get_top_dimensions(breakdown: Dict[str, Any], n: int, order: str = 'desc') -> List[str]:
    """
    获取得分最高/最低的维度
    """
    dims = [(name, data['score']) for name, data in breakdown.items()]
    reverse = (order == 'desc')
    dims.sort(key=lambda x: x[1], reverse=reverse)
    
    dim_names = {
        'location': '位置',
        'activity': '活跃度',
        'competition': '竞争密度',
        'cooperation': '配合度',
        'digital': '数字化接受度',
        'owner': '店主画像',
        'region': '区域潜力'
    }
    
    result = []
    for name, score in dims[:n]:
        result.append(f"{dim_names.get(name, name)} ({score}分)")
    
    return result


def get_action_priority(score_result: Dict[str, Any]) -> str:
    """
    根据评分获取行动优先级
    """
    total_score = score_result.get('total_score', 0)
    
    if total_score >= 80:
        return 'high'
    elif total_score >= 60:
        return 'medium'
    else:
        return 'low'
