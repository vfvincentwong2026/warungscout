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

### 3.1 核心逻辑

根据 Warung 当前步骤和评分，自动生成下一步销售动作。每个建议包含：下一步步骤编号、具体动作描述、话术模板、优先级、截止天数、触达渠道。

### 3.2 Python 实现

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
4.1 反馈类型与分数变化映射
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

    # 更新配合度和数字化分数（保持 0-100 范围）
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
6. 销售反馈采集表单
6.1 表单字段
字段	类型	选项/示例
Warung 名称	文本	自动填充
反馈类型	下拉选择	WA回复/同意拜访/拒绝拜访/试销下单/试销拒绝/签约合作/转介绍/拒绝陈列/分享销售数据
备注	文本	详细记录沟通情况
下次跟进时间	日期	建议自动生成，可手动调整
6.2 反馈提交后自动触发的动作
记录反馈到 outreach_logs 表

更新 Warung 的配合度和数字化分数

重新计算综合评分

更新分级（如果分数跨级）

推进或回退销售步骤（根据反馈类型）

更新待办任务（完成当前任务，生成下一任务）

文档结束
