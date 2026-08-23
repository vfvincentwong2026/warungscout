# ============================================================
# WarungScout 步骤建议生成器
# 功能: 根据 Warung 当前状态自动生成下一步销售建议
# 版本: v1.0.0
# ============================================================

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================
# 1. 销售步骤定义
# ============================================================

SALES_STEPS = {
    0: {'name': '未接触', 'action': '系统初筛，分配优先级'},
    1: {'name': '首次破冰', 'action': 'WA 发送破冰消息'},
    2: {'name': '初次拜访', 'action': '地推上门拜访'},
    3: {'name': '推品试销', 'action': '推荐主推品/小批量铺货'},
    4: {'name': '深度合作', 'action': '签约独家/联合促销'},
    5: {'name': '长期运营', 'action': '定期巡访/新品推荐'},
}

# 步骤超时配置（天数）
STEP_TIMEOUTS = {
    0: 30,
    1: 3,
    2: 5,
    3: 7,
    4: 14,
    5: 14,
}

# 冷却配置
COOLING_NO_RESPONSE_DAYS = 7
COOLING_DAYS = 15


# ============================================================
# 2. 核心建议生成器
# ============================================================

def generate_next_advice(warung: Dict[str, Any], score_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 Warung 当前状态和评分，生成下一步建议

    Args:
        warung: Warung 数据字典
        score_result: 评分结果字典（来自 scorer.py）

    Returns:
        {
            'next_step': int,          # 下一步步骤编号
            'next_step_name': str,     # 下一步步骤名称
            'action': str,             # 具体动作描述
            'description': str,        # 详细说明
            'template': str,           # 话术模板名称
            'priority': str,           # high | medium | low
            'timeout_days': int,       # 截止天数
            'channel': str,            # whatsapp | visit | call | None
            'current_step': int,       # 当前步骤
            'current_step_name': str,  # 当前步骤名称
        }
    """
    current_step = warung.get('sales_step', 0)
    total_score = score_result.get('total_score', 0)
    grade = score_result.get('grade', 'normal')

    # 检查是否是新抓取的 Warung
    is_new_gmaps = (
        warung.get('source') == 'google_maps' and
        warung.get('data_completeness', 'basic') == 'basic'
    )

    # ============================================================
    # Step 0: 未接触
    # ============================================================
    if current_step == 0:
        return _advice_step0(warung, total_score, grade, is_new_gmaps)

    # ============================================================
    # Step 1: 首次破冰 (WA 已发送)
    # ============================================================
    if current_step == 1:
        return _advice_step1(warung)

    # ============================================================
    # Step 2: 初次拜访
    # ============================================================
    if current_step == 2:
        return _advice_step2(warung)

    # ============================================================
    # Step 3: 推品试销
    # ============================================================
    if current_step == 3:
        return _advice_step3(warung)

    # ============================================================
    # Step 4: 深度合作
    # ============================================================
    if current_step == 4:
        return _advice_step4(warung)

    # ============================================================
    # Step 5: 长期运营
    # ============================================================
    if current_step == 5:
        return _advice_step5(warung)

    # 默认返回
    return {
        'next_step': current_step,
        'next_step_name': SALES_STEPS.get(current_step, {}).get('name', '未知'),
        'action': '状态异常，请联系管理员',
        'description': f'无法识别的步骤状态: {current_step}',
        'template': None,
        'priority': 'low',
        'timeout_days': 7,
        'channel': None,
        'current_step': current_step,
        'current_step_name': SALES_STEPS.get(current_step, {}).get('name', '未知'),
    }


# ============================================================
# 3. 各步骤建议逻辑
# ============================================================

def _advice_step0(warung: Dict[str, Any], total_score: int, grade: str, is_new_gmaps: bool) -> Dict[str, Any]:
    """Step 0: 未接触"""
    # 从 Google Maps 新抓取的 Warung，先记录来源
    source_note = '（新抓取，建议尽快联系）' if is_new_gmaps else ''

    if total_score >= 70:
        return {
            'next_step': 1,
            'next_step_name': '首次破冰',
            'action': '立即通过 WhatsApp 发送破冰消息',
            'description': f'高价值 Warung，优先触达 {source_note}',
            'template': 'WARUNG_GOLD_BREAK_ICE',
            'priority': 'high',
            'timeout_days': 1,
            'channel': 'whatsapp',
            'current_step': 0,
            'current_step_name': '未接触',
        }
    elif total_score >= 50:
        return {
            'next_step': 1,
            'next_step_name': '首次破冰',
            'action': '3 天内通过 WhatsApp 发送破冰消息',
            'description': f'中等潜力 Warung，建议跟进 {source_note}',
            'template': 'WARUNG_SILVER_BREAK_ICE',
            'priority': 'medium',
            'timeout_days': 3,
            'channel': 'whatsapp',
            'current_step': 0,
            'current_step_name': '未接触',
        }
    else:
        return {
            'next_step': 0,
            'next_step_name': '未接触',
            'action': '暂不触达，添加到培育池',
            'description': f'低分 Warung，等待后续激活 {source_note}',
            'template': None,
            'priority': 'low',
            'timeout_days': 30,
            'channel': None,
            'current_step': 0,
            'current_step_name': '未接触',
        }


def _advice_step1(warung: Dict[str, Any]) -> Dict[str, Any]:
    """Step 1: 首次破冰"""
    last_action_at = warung.get('last_action_at', 0)
    days_since = _days_since(last_action_at)

    if days_since > 2 and days_since <= 7:
        return {
            'next_step': 1,
            'next_step_name': '首次破冰',
            'action': '发送第二次 WA 消息跟进',
            'description': f'上次 WA 发送已 {days_since} 天，无回复，继续跟进',
            'template': 'WARUNG_FOLLOWUP_1',
            'priority': 'medium',
            'timeout_days': 2,
            'channel': 'whatsapp',
            'current_step': 1,
            'current_step_name': '首次破冰',
        }
    elif days_since > 7:
        return {
            'next_step': 0,
            'next_step_name': '未接触',
            'action': '暂停跟进，标记为冷却状态',
            'description': f'连续 {days_since} 天无回复，{COOLING_DAYS} 天后重新激活',
            'template': None,
            'priority': 'low',
            'timeout_days': COOLING_DAYS,
            'channel': None,
            'current_step': 1,
            'current_step_name': '首次破冰',
        }
    else:
        # 等待中（2天内）
        remaining_days = 2 - days_since
        return {
            'next_step': 1,
            'next_step_name': '首次破冰',
            'action': '等待店主回复',
            'description': f'WA 已发送，等待店主回应（剩余 {remaining_days} 天）',
            'template': None,
            'priority': 'medium',
            'timeout_days': remaining_days if remaining_days > 0 else 1,
            'channel': None,
            'current_step': 1,
            'current_step_name': '首次破冰',
        }


def _advice_step2(warung: Dict[str, Any]) -> Dict[str, Any]:
    """Step 2: 初次拜访"""
    visit_count = warung.get('visit_count', 0)

    if visit_count == 0:
        return {
            'next_step': 2,
            'next_step_name': '初次拜访',
            'action': '安排地推团队上门拜访',
            'description': '店主已回复 WA，建议 3 天内完成首次拜访',
            'template': 'VISIT_SCRIPT_V1',
            'priority': 'high',
            'timeout_days': 3,
            'channel': 'visit',
            'current_step': 2,
            'current_step_name': '初次拜访',
        }
    elif visit_count == 1 and warung.get('visit_result') == 'pending':
        return {
            'next_step': 2,
            'next_step_name': '初次拜访',
            'action': '第二次拜访，加深关系',
            'description': '首次拜访后未达成合作，建议再次拜访并换品推荐',
            'template': 'VISIT_SCRIPT_V2',
            'priority': 'medium',
            'timeout_days': 5,
            'channel': 'visit',
            'current_step': 2,
            'current_step_name': '初次拜访',
        }
    else:
        if warung.get('visit_result') == 'success':
            return {
                'next_step': 3,
                'next_step_name': '推品试销',
                'action': '进入推品试销阶段',
                'description': '拜访沟通顺畅，推荐主推品并安排小批量铺货',
                'template': None,
                'priority': 'high',
                'timeout_days': 3,
                'channel': None,
                'current_step': 2,
                'current_step_name': '初次拜访',
            }
        else:
            return {
                'next_step': 0,
                'next_step_name': '未接触',
                'action': '暂缓跟进，重新评估',
                'description': '多次拜访无果，建议暂时搁置 30 天',
                'template': None,
                'priority': 'low',
                'timeout_days': 30,
                'channel': None,
                'current_step': 2,
                'current_step_name': '初次拜访',
            }


def _advice_step3(warung: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: 推品试销"""
    trial_status = warung.get('trial_status', 'pending')

    if trial_status == 'pending':
        return {
            'next_step': 3,
            'next_step_name': '推品试销',
            'action': '确认试销铺货情况',
            'description': '已推荐主推品，需确认是否已上架/陈列',
            'template': None,
            'priority': 'high',
            'timeout_days': 3,
            'channel': 'visit',
            'current_step': 3,
            'current_step_name': '推品试销',
        }
    elif trial_status == 'success':
        return {
            'next_step': 4,
            'next_step_name': '深度合作',
            'action': '进入深度合作阶段',
            'description': '试销效果良好，建议推进签约独家/联合促销',
            'template': None,
            'priority': 'high',
            'timeout_days': 7,
            'channel': None,
            'current_step': 3,
            'current_step_name': '推品试销',
        }
    else:  # 'failed'
        return {
            'next_step': 2,
            'next_step_name': '初次拜访',
            'action': '返回拜访阶段，换品推荐',
            'description': '试销效果不佳，建议换品推荐并重新拜访',
            'template': 'VISIT_SCRIPT_V2',
            'priority': 'medium',
            'timeout_days': 5,
            'channel': 'visit',
            'current_step': 3,
            'current_step_name': '推品试销',
        }


def _advice_step4(warung: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: 深度合作"""
    return {
        'next_step': 5,
        'next_step_name': '长期运营',
        'action': '完成签约，进入长期运营',
        'description': '准备合作协议，安排签约仪式或正式确认',
        'template': None,
        'priority': 'high',
        'timeout_days': 7,
        'channel': None,
        'current_step': 4,
        'current_step_name': '深度合作',
    }


def _advice_step5(warung: Dict[str, Any]) -> Dict[str, Any]:
    """Step 5: 长期运营"""
    return {
        'next_step': 5,
        'next_step_name': '长期运营',
        'action': '定期巡访 + 新品推荐',
        'description': '合作稳定，建议每 2 周巡访一次，每月推荐 1-2 个新品',
        'template': None,
        'priority': 'medium',
        'timeout_days': 14,
        'channel': 'visit',
        'current_step': 5,
        'current_step_name': '长期运营',
    }


# ============================================================
# 4. 辅助函数
# ============================================================

def _days_since(timestamp: int) -> int:
    """计算距离现在多少天"""
    if not timestamp:
        return 999
    now = datetime.now()
    then = datetime.fromtimestamp(timestamp)
    return (now - then).days


def get_step_name(step: int) -> str:
    """获取步骤名称"""
    return SALES_STEPS.get(step, {}).get('name', '未知')


def get_step_action(step: int) -> str:
    """获取步骤动作描述"""
    return SALES_STEPS.get(step, {}).get('action', '')


def get_timeout_days(step: int) -> int:
    """获取步骤超时天数"""
    return STEP_TIMEOUTS.get(step, 7)


def should_advance_to_next_step(warung: Dict[str, Any]) -> bool:
    """
    检查是否应该推进到下一步
    
    条件:
    - 当前步骤已完成 (step_status == 'done')
    - 或当前步骤已超时
    """
    step_status = warung.get('step_status', 'pending')
    last_action_at = warung.get('last_action_at', 0)
    current_step = warung.get('sales_step', 0)
    
    if step_status == 'done':
        return True
    
    if last_action_at:
        days = _days_since(last_action_at)
        timeout = STEP_TIMEOUTS.get(current_step, 7)
        if days > timeout:
            return True
    
    return False


def mark_task_completed(warung: Dict[str, Any], feedback_type: str) -> Dict[str, Any]:
    """
    标记任务已完成，推进步骤或更新状态
    
    Args:
        warung: Warung 数据
        feedback_type: 反馈类型（决定如何推进）
    
    Returns:
        更新后的 Warung 数据
    """
    current_step = warung.get('sales_step', 0)
    result = warung.copy()
    
    # 根据反馈类型决定步骤推进
    if feedback_type in ['cooperation_signed', 'referral_given']:
        # 重大进展，直接推进到下一步
        result['sales_step'] = min(current_step + 1, 5)
        result['step_status'] = 'pending'
    elif feedback_type in ['visit_agreed', 'trial_ordered']:
        # 进展顺利，推进到下一步
        result['sales_step'] = min(current_step + 1, 5)
        result['step_status'] = 'pending'
    elif feedback_type in ['visit_refused', 'trial_rejected', 'display_refused']:
        # 受阻，可能需要回退或重新评估
        result['step_status'] = 'blocked'
        result['block_reason'] = feedback_type
    elif feedback_type == 'wa_replied':
        # 破冰成功，推进到拜访阶段（如果当前是 Step 1）
        if current_step == 1:
            result['sales_step'] = 2
        result['step_status'] = 'pending'
    elif feedback_type == 'wa_not_replied_3x':
        # 多次无回复，进入冷却
        result['step_status'] = 'blocked'
        result['block_reason'] = 'no_response'
        result['cold_until'] = int((datetime.now() + timedelta(days=COOLING_DAYS)).timestamp())
    else:
        # 默认：保持当前步骤，但更新时间和状态
        result['step_status'] = 'in_progress'
    
    result['last_action_at'] = int(datetime.now().timestamp())
    result['updated_at'] = int(datetime.now().timestamp())
    
    return result
