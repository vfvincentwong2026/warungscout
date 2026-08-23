# ============================================================
# WarungScout 反馈闭环处理器
# 功能: 处理销售反馈，动态调整评分和步骤
# 版本: v1.0.0
# ============================================================

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import logging

from .scorer import calculate_final_score, SCORE_WEIGHTS
from .advisor import mark_task_completed, get_step_name

logger = logging.getLogger(__name__)


# ============================================================
# 1. 反馈类型定义
# ============================================================

# 反馈类型 → 分数变化映射
FEEDBACK_DELTAS = {
    # 正向反馈
    'wa_replied': {
        'cooperation': +2,
        'digital': +1,
        'total': +3,
        'description': '店主回复了 WA 消息',
        'step_effect': 'advance'  # advance | block | none
    },
    'visit_agreed': {
        'cooperation': +5,
        'digital': 0,
        'total': +5,
        'description': '店主同意地推拜访',
        'step_effect': 'advance'
    },
    'trial_ordered': {
        'cooperation': +5,
        'digital': +3,
        'total': +8,
        'description': '店主试销下单/上架',
        'step_effect': 'advance'
    },
    'cooperation_signed': {
        'cooperation': +10,
        'digital': +5,
        'total': +15,
        'description': '签约深度合作',
        'step_effect': 'advance'
    },
    'referral_given': {
        'cooperation': +5,
        'digital': +3,
        'total': +8,
        'description': '店主转介绍新 Warung',
        'step_effect': 'advance'
    },
    'sales_data_shared': {
        'cooperation': +3,
        'digital': +2,
        'total': +5,
        'description': '店主分享销售数据',
        'step_effect': 'none'
    },

    # 负向反馈
    'visit_refused': {
        'cooperation': -8,
        'digital': 0,
        'total': -8,
        'description': '店主拒绝拜访',
        'step_effect': 'block'
    },
    'trial_rejected': {
        'cooperation': -3,
        'digital': 0,
        'total': -3,
        'description': '店主拒绝试销',
        'step_effect': 'none'
    },
    'display_refused': {
        'cooperation': -10,
        'digital': 0,
        'total': -10,
        'description': '店主拒绝陈列要求',
        'step_effect': 'block'
    },
    'wa_not_replied_3x': {
        'cooperation': -5,
        'digital': 0,
        'total': -5,
        'description': '连续 3 次 WA 无回复',
        'step_effect': 'block'
    },

    # 系统事件（不改变分数）
    'gmaps_imported': {
        'cooperation': 0,
        'digital': 0,
        'total': 0,
        'description': '从 Google Maps 导入',
        'step_effect': 'none'
    },
    'manual_update': {
        'cooperation': 0,
        'digital': 0,
        'total': 0,
        'description': '人工更新',
        'step_effect': 'none'
    },
}


# ============================================================
# 2. 反馈处理核心函数
# ============================================================

def process_feedback(
    warung: Dict[str, Any],
    feedback_type: str,
    note: Optional[str] = None,
    custom_delta: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    处理销售反馈，更新评分和步骤

    Args:
        warung: Warung 数据字典
        feedback_type: 反馈类型（见 FEEDBACK_DELTAS）
        note: 备注信息
        custom_delta: 自定义分数变化（用于 manual_update 类型）

    Returns:
        {
            'warung': dict,              # 更新后的 Warung 数据
            'score_before': int,         # 更新前总分
            'score_after': int,          # 更新后总分
            'score_delta': dict,         # 各维度变化
            'step_before': int,          # 更新前步骤
            'step_after': int,           # 更新后步骤
            'grade_before': str,         # 更新前等级
            'grade_after': str,          # 更新后等级
            'feedback_type': str,        # 反馈类型
            'applied': bool,             # 是否成功应用
            'message': str,              # 处理结果消息
        }
    """
    # 1. 验证反馈类型
    delta_config = FEEDBACK_DELTAS.get(feedback_type)
    if not delta_config and feedback_type != 'manual_update':
        return {
            'warung': warung,
            'error': True,
            'message': f'未知的反馈类型: {feedback_type}'
        }

    # 2. 复制 warung 数据
    updated_warung = warung.copy()

    # 3. 计算评分变化
    if feedback_type == 'manual_update' and custom_delta:
        # 手动更新，使用自定义变化
        coop_delta = custom_delta.get('cooperation', 0)
        digi_delta = custom_delta.get('digital', 0)
        total_delta = custom_delta.get('total', coop_delta + digi_delta)
        description = note or '人工更新评分'
    else:
        coop_delta = delta_config.get('cooperation', 0)
        digi_delta = delta_config.get('digital', 0)
        total_delta = delta_config.get('total', 0)
        description = delta_config.get('description', '')

    # 4. 保存旧值
    old_score = updated_warung.get('final_score', 0)
    old_grade = updated_warung.get('grade', 'normal')
    old_step = updated_warung.get('sales_step', 0)

    # 5. 更新配合度和数字化分数
    old_coop = updated_warung.get('cooperation_score', 50)
    old_digi = updated_warung.get('digital_score', 50)

    new_coop = max(0, min(100, old_coop + coop_delta))
    new_digi = max(0, min(100, old_digi + digi_delta))

    updated_warung['cooperation_score'] = new_coop
    updated_warung['digital_score'] = new_digi

    # 6. 重新计算总分
    score_result = calculate_final_score(updated_warung)
    new_score = score_result['total_score']
    new_grade = score_result['grade']

    updated_warung['final_score'] = new_score
    updated_warung['grade'] = new_grade

    # 7. 更新步骤
    step_result = mark_task_completed(updated_warung, feedback_type)
    new_step = step_result.get('sales_step', old_step)

    updated_warung['sales_step'] = new_step
    updated_warung['step_status'] = step_result.get('step_status', 'in_progress')
    updated_warung['last_action_at'] = int(datetime.now().timestamp())
    updated_warung['updated_at'] = int(datetime.now().timestamp())

    # 8. 更新数据完整性状态
    if updated_warung.get('data_completeness') == 'basic':
        # 第一次反馈后，标记为 partial
        updated_warung['data_completeness'] = 'partial'

    # 检查是否所有维度都已填充
    if _is_data_complete(updated_warung):
        updated_warung['data_completeness'] = 'complete'

    # 9. 更新统计字段
    if feedback_type in ['wa_replied', 'wa_not_replied_3x']:
        updated_warung['outreach_count'] = updated_warung.get('outreach_count', 0) + 1
        if feedback_type == 'wa_not_replied_3x':
            updated_warung['no_response_count'] = updated_warung.get('no_response_count', 0) + 1

    if feedback_type in ['visit_agreed', 'visit_refused']:
        updated_warung['visit_count'] = updated_warung.get('visit_count', 0) + 1
        updated_warung['visit_result'] = 'success' if feedback_type == 'visit_agreed' else 'refused'

    if feedback_type == 'trial_ordered':
        updated_warung['trial_status'] = 'success'

    if feedback_type == 'trial_rejected':
        updated_warung['trial_status'] = 'failed'

    # 10. 记录反馈历史
    history_entry = {
        'feedback_type': feedback_type,
        'score_before': old_score,
        'score_after': new_score,
        'delta_cooperation': coop_delta,
        'delta_digital': digi_delta,
        'delta_total': total_delta,
        'step_before': old_step,
        'step_after': new_step,
        'grade_before': old_grade,
        'grade_after': new_grade,
        'note': note or description,
        'timestamp': datetime.now().isoformat()
    }

    updated_warung['feedback_history'] = updated_warung.get('feedback_history', []) + [history_entry]

    # 11. 构建返回结果
    return {
        'warung': updated_warung,
        'score_before': old_score,
        'score_after': new_score,
        'score_delta': {
            'cooperation': coop_delta,
            'digital': digi_delta,
            'total': total_delta
        },
        'step_before': old_step,
        'step_after': new_step,
        'grade_before': old_grade,
        'grade_after': new_grade,
        'feedback_type': feedback_type,
        'applied': True,
        'message': f'反馈已处理: {description}（总分: {old_score} → {new_score}, 步骤: {get_step_name(old_step)} → {get_step_name(new_step)}）',
        'history': history_entry,
    }


# ============================================================
# 3. 批量反馈处理
# ============================================================

def batch_process_feedback(
    warungs: List[Dict[str, Any]],
    feedback_entries: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    批量处理反馈

    Args:
        warungs: Warung 数据列表
        feedback_entries: 反馈条目列表，每个包含 warung_id 和 feedback_type

    Returns:
        处理结果列表
    """
    results = []
    for entry in feedback_entries:
        warung_id = entry.get('warung_id')
        feedback_type = entry.get('feedback_type')
        note = entry.get('note')

        # 查找对应的 Warung
        warung = next((w for w in warungs if w.get('id') == warung_id), None)
        if not warung:
            results.append({
                'warung_id': warung_id,
                'error': True,
                'message': f'未找到 Warung: {warung_id}'
            })
            continue

        result = process_feedback(warung, feedback_type, note)
        results.append(result)

    return results


# ============================================================
# 4. 辅助函数
# ============================================================

def _is_data_complete(warung: Dict[str, Any]) -> bool:
    """检查是否所有数据都已填充完成"""
    required_fields = [
        'cooperation_score', 'digital_score', 'owner_score',
        'visit_feedback', 'payment_methods'
    ]

    for field in required_fields:
        value = warung.get(field)
        if value is None or value == '':
            return False

    return True


def get_feedback_summary(warung: Dict[str, Any]) -> Dict[str, Any]:
    """获取反馈历史摘要"""
    history = warung.get('feedback_history', [])

    if not history:
        return {
            'total_feedback': 0,
            'positive_count': 0,
            'negative_count': 0,
            'last_feedback_at': None,
            'most_common_type': None,
        }

    total = len(history)
    positive_types = ['wa_replied', 'visit_agreed', 'trial_ordered', 'cooperation_signed', 'referral_given']
    negative_types = ['visit_refused', 'trial_rejected', 'display_refused', 'wa_not_replied_3x']

    positive_count = sum(1 for h in history if h.get('feedback_type') in positive_types)
    negative_count = sum(1 for h in history if h.get('feedback_type') in negative_types)

    # 统计最常见的反馈类型
    type_counts = {}
    for h in history:
        ft = h.get('feedback_type', 'unknown')
        type_counts[ft] = type_counts.get(ft, 0) + 1
    most_common = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None

    return {
        'total_feedback': total,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'net_score': positive_count - negative_count,
        'last_feedback_at': history[-1].get('timestamp') if history else None,
        'most_common_type': most_common,
    }


def get_available_feedback_types() -> List[Dict[str, Any]]:
    """获取所有可用的反馈类型（用于前端下拉菜单）"""
    return [
        {
            'type': key,
            'description': value['description'],
            'cooperation_delta': value['cooperation'],
            'digital_delta': value['digital'],
            'total_delta': value['total'],
            'category': 'positive' if value['total'] > 0 else 'negative' if value['total'] < 0 else 'neutral'
        }
        for key, value in FEEDBACK_DELTAS.items()
    ]
