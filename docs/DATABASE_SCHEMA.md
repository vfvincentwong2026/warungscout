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

    -- 数据来源追踪（新增）
    source TEXT DEFAULT 'manual' CHECK(source IN ('google_maps', 'manual', 'api')),
    source_import_id TEXT,
    source_imported_at INTEGER,

    -- Google Maps 原始数据（新增）
    gm_place_id TEXT,
    gm_rating REAL,
    gm_reviews INTEGER,
    gm_types TEXT,  -- JSON 数组
    gm_plus_code TEXT,

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
    cold_until INTEGER,

    -- 统计字段
    outreach_count INTEGER DEFAULT 0,
    no_response_count INTEGER DEFAULT 0,
    visit_count INTEGER DEFAULT 0,
    visit_result TEXT CHECK(visit_result IN ('success', 'pending', 'refused', NULL)),
    trial_status TEXT DEFAULT 'pending' CHECK(trial_status IN ('pending', 'success', 'failed')),

    -- 数据完整性标记（新增）
    data_completeness TEXT DEFAULT 'basic' CHECK(data_completeness IN ('basic', 'partial', 'complete')),
    -- basic: 仅来自 Google Maps, partial: 部分销售补充, complete: 全部字段已确认

    -- 时间戳
    last_action_at INTEGER,
    next_action_at INTEGER,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- 索引
CREATE INDEX idx_warungs_grade ON warungs(grade);
CREATE INDEX idx_warungs_sales_step ON warungs(sales_step);
CREATE INDEX idx_warungs_final_score ON warungs(final_score);
CREATE INDEX idx_warungs_region ON warungs(region);
CREATE INDEX idx_warungs_source ON warungs(source);  -- 新增
CREATE INDEX idx_warungs_gm_place_id ON warungs(gm_place_id);  -- 新增
CREATE INDEX idx_warungs_next_action_at ON warungs(next_action_at);
CREATE INDEX idx_warungs_created_at ON warungs(created_at);
1.2 google_maps_import_tasks（Google Maps 抓取任务表，新增）
sql
CREATE TABLE google_maps_import_tasks (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    query TEXT NOT NULL,
    location TEXT,
    max_results INTEGER DEFAULT 100,
    source_type TEXT CHECK(source_type IN ('serpapi', 'places_api', 'playwright')),

    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed')),
    total_found INTEGER DEFAULT 0,
    total_imported INTEGER DEFAULT 0,

    error_message TEXT,
    started_at INTEGER,
    completed_at INTEGER,

    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_gmaps_import_tasks_status ON google_maps_import_tasks(status);
CREATE INDEX idx_gmaps_import_tasks_created_at ON google_maps_import_tasks(created_at);
1.3 score_history（评分历史）
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
        'gmaps_imported',  -- 新增
        'wa_replied', 'wa_not_replied_3x',
        'visit_agreed', 'visit_refused',
        'trial_ordered', 'trial_rejected',
        'cooperation_signed',
        'referral_given', 'display_refused',
        'sales_data_shared',
        'manual_update'  -- 新增
    )),

    reason TEXT,
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX idx_score_history_warung_id ON score_history(warung_id);
CREATE INDEX idx_score_history_created_at ON score_history(created_at);
1.4 outreach_logs（触达记录）
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
1.5 warung_history（全量操作日志）
sql
CREATE TABLE warung_history (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    action_type TEXT CHECK(action_type IN ('score_update', 'step_change', 'feedback', 'status_change', 'import')),
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
2.2 预置搜索词库表（新增）
sql
CREATE TABLE search_queries (
    id TEXT PRIMARY KEY DEFAULT (uuid4()),
    keyword TEXT NOT NULL,
    location TEXT,
    is_active BOOLEAN DEFAULT 1,
    last_imported_at INTEGER,
    created_at INTEGER DEFAULT (unixepoch())
);

INSERT INTO search_queries (keyword, location) VALUES
('warung Jakarta', '-6.2088,106.8456,14z'),
('warung Surabaya', '-7.2575,112.7521,14z'),
('warung Bali', '-8.3405,115.0920,14z'),
('warung Bandung', '-6.9175,107.6191,14z'),
('warung Medan', '3.5952,98.6722,14z'),
('warung Yogyakarta', '-7.7956,110.3695,14z');
3. 字段枚举说明
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
3.4 source（数据来源）
值	含义
google_maps	从 Google Maps 自动抓取
manual	人工录入（地推/CSV导入）
api	通过 API 导入
3.5 data_completeness（数据完整性）
值	含义	说明
basic	基础	仅来自 Google Maps，等待销售补充
partial	部分	已有部分销售反馈
complete	完整	所有维度已确认
3.6 feedback_type（反馈类型）
值	含义	配合度变化	数字化变化	总分变化
gmaps_imported	从 Google Maps 导入	0	0	0
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
manual_update	人工更新分数	自定义	自定义	自定义
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
    next_action_at,
    source
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
    SUM(CASE WHEN source = 'google_maps' THEN 1 ELSE 0 END) as from_google_maps,
    SUM(CASE WHEN source = 'manual' THEN 1 ELSE 0 END) as from_manual,
    AVG(final_score) as avg_score
FROM warungs;
4.3 按数据来源统计
sql
SELECT
    source,
    COUNT(*) as count,
    AVG(final_score) as avg_score,
    SUM(CASE WHEN grade = 'gold' THEN 1 ELSE 0 END) as gold_count
FROM warungs
GROUP BY source;
4.4 查询 Google Maps 抓取任务状态
sql
SELECT
    id,
    query,
    status,
    total_found,
    total_imported,
    started_at,
    completed_at
FROM google_maps_import_tasks
ORDER BY created_at DESC
LIMIT 20;
4.5 查询某个 Warung 的完整信息（含评分明细）
sql
SELECT
    w.*,
    (
        SELECT json_group_array(
            json_object(
                'score_before', score_before,
                'score_after', score_after,
                'feedback_type', feedback_type,
                'created_at', created_at
            )
        )
        FROM score_history sh
        WHERE sh.warung_id = w.id
        ORDER BY sh.created_at DESC
        LIMIT 10
    ) as recent_score_history,
    (
        SELECT json_group_array(
            json_object(
                'channel', channel,
                'status', status,
                'created_at', created_at
            )
        )
        FROM outreach_logs ol
        WHERE ol.warung_id = w.id
        ORDER BY ol.created_at DESC
        LIMIT 10
    ) as recent_outreach
FROM warungs w
WHERE w.id = ?;
5. 数据迁移
5.1 从 Google Maps 抓取数据入库流程
sql
-- 1. 创建新 Warung 记录（含 Google Maps 数据）
INSERT INTO warungs (
    id, name, phone, address, latitude, longitude,
    region, city,
    source, source_import_id,
    gm_place_id, gm_rating, gm_reviews, gm_types,
    location_score, activity_score, competition_score,
    cooperation_score, digital_score, owner_score, region_score,
    final_score, grade,
    sales_step, step_status,
    data_completeness,
    created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'google_maps', ?, ?, ?, ?, ?, ?, ?, 50, 50, 50, 50, ?, ?, 0, 'pending', 'basic', unixepoch(), unixepoch());

-- 2. 记录评分历史
INSERT INTO score_history (
    warung_id, score_before, score_after, feedback_type, reason, created_at
) VALUES (?, 0, ?, 'gmaps_imported', '从 Google Maps 抓取导入', unixepoch());

-- 3. 更新抓取任务统计
UPDATE google_maps_import_tasks
SET total_imported = total_imported + 1
WHERE id = ?;
5.2 迁移脚本模板
sql
-- migrations/001_init.sql
-- 包含所有 CREATE TABLE 语句

-- migrations/002_seed_cities.sql
-- 包含城市数据

-- migrations/003_seed_search_queries.sql
-- 包含预置搜索词库

-- migrations/004_add_gmaps_fields.sql
-- 为 warungs 表添加 Google Maps 相关字段（如需增量更新）
6. 数据库关系图
text
┌─────────────────────────────┐
│    google_maps_import_tasks  │
├─────────────────────────────┤
│ id (PK)                     │
│ query                       │
│ location                    │
│ status                      │
│ total_imported              │
└─────────────────────────────┘
              │
              │ 触发导入
              ▼
┌─────────────────────────────┐          ┌─────────────────────────────┐
│          warungs             │          │       search_queries        │
├─────────────────────────────┤          ├─────────────────────────────┤
│ id (PK)                     │          │ id (PK)                     │
│ name                        │          │ keyword                     │
│ phone                       │          │ location                    │
│ address                     │          │ is_active                   │
│ latitude / longitude        │          └─────────────────────────────┘
│ source  ←─────── 新增       │
│ gm_place_id  ←── 新增       │
│ gm_rating  ←─── 新增        │
│ gm_reviews  ←── 新增        │
│ gm_types  ←──── 新增        │
│ data_completeness ←─ 新增   │
│ 7个维度评分                  │
│ final_score, grade          │
│ sales_step, step_status     │
└──────────────┬──────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌──────────────┐  ┌──────────────┐
│ score_history │  │outreach_logs │
├──────────────┤  ├──────────────┤
│ warung_id(FK)│  │ warung_id(FK)│
│ feedback_type│  │ channel      │
│ (含gmaps_    │  │ status       │
│  imported)   │  └──────────────┘
└──────────────┘
     │
     ▼
┌──────────────┐
│warung_history│
├──────────────┤
│ warung_id(FK)│
│ action_type  │
│ (含 import)  │
└──────────────┘
