-- ============================================================
-- WarungScout 数据库初始化脚本
-- 数据库: Cloudflare D1 (SQLite)
-- 版本: v1.0.0
-- 执行: npx wrangler d1 execute warungscout_db --file=./migrations/init.sql
-- ============================================================

-- ============================================================
-- 1. warungs（Warung 主表）
-- ============================================================
CREATE TABLE IF NOT EXISTS warungs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    region TEXT,
    city TEXT,

    -- 数据来源追踪
    source TEXT DEFAULT 'manual' CHECK(source IN ('google_maps', 'manual', 'api')),
    source_import_id TEXT,
    source_imported_at INTEGER,

    -- Google Maps 原始数据
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

    -- 数据完整性标记
    data_completeness TEXT DEFAULT 'basic' CHECK(data_completeness IN ('basic', 'partial', 'complete')),

    -- 时间戳
    last_action_at INTEGER,
    next_action_at INTEGER,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- warungs 表索引
CREATE INDEX IF NOT EXISTS idx_warungs_grade ON warungs(grade);
CREATE INDEX IF NOT EXISTS idx_warungs_sales_step ON warungs(sales_step);
CREATE INDEX IF NOT EXISTS idx_warungs_final_score ON warungs(final_score);
CREATE INDEX IF NOT EXISTS idx_warungs_region ON warungs(region);
CREATE INDEX IF NOT EXISTS idx_warungs_source ON warungs(source);
CREATE INDEX IF NOT EXISTS idx_warungs_gm_place_id ON warungs(gm_place_id);
CREATE INDEX IF NOT EXISTS idx_warungs_next_action_at ON warungs(next_action_at);
CREATE INDEX IF NOT EXISTS idx_warungs_created_at ON warungs(created_at);


-- ============================================================
-- 2. google_maps_import_tasks（Google Maps 抓取任务表）
-- ============================================================
CREATE TABLE IF NOT EXISTS google_maps_import_tasks (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
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

CREATE INDEX IF NOT EXISTS idx_gmaps_import_tasks_status ON google_maps_import_tasks(status);
CREATE INDEX IF NOT EXISTS idx_gmaps_import_tasks_created_at ON google_maps_import_tasks(created_at);


-- ============================================================
-- 3. score_history（评分历史）
-- ============================================================
CREATE TABLE IF NOT EXISTS score_history (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    score_before INTEGER NOT NULL,
    score_after INTEGER NOT NULL,
    delta_cooperation INTEGER,
    delta_digital INTEGER,
    delta_total INTEGER,

    feedback_type TEXT CHECK(feedback_type IN (
        'gmaps_imported',
        'wa_replied', 'wa_not_replied_3x',
        'visit_agreed', 'visit_refused',
        'trial_ordered', 'trial_rejected',
        'cooperation_signed',
        'referral_given', 'display_refused',
        'sales_data_shared',
        'manual_update'
    )),

    reason TEXT,
    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_score_history_warung_id ON score_history(warung_id);
CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON score_history(created_at);


-- ============================================================
-- 4. outreach_logs（触达记录）
-- ============================================================
CREATE TABLE IF NOT EXISTS outreach_logs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    channel TEXT CHECK(channel IN ('whatsapp', 'call', 'visit')),
    template TEXT,
    message TEXT,

    status TEXT CHECK(status IN ('sent', 'delivered', 'read', 'replied', 'no_response')),
    response TEXT,

    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_outreach_logs_warung_id ON outreach_logs(warung_id);
CREATE INDEX IF NOT EXISTS idx_outreach_logs_created_at ON outreach_logs(created_at);


-- ============================================================
-- 5. warung_history（全量操作日志）
-- ============================================================
CREATE TABLE IF NOT EXISTS warung_history (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    warung_id TEXT NOT NULL REFERENCES warungs(id) ON DELETE CASCADE,

    action_type TEXT CHECK(action_type IN ('score_update', 'step_change', 'feedback', 'status_change', 'import')),
    old_value TEXT,
    new_value TEXT,
    note TEXT,

    created_at INTEGER DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_warung_history_warung_id ON warung_history(warung_id);
CREATE INDEX IF NOT EXISTS idx_warung_history_created_at ON warung_history(created_at);


-- ============================================================
-- 6. city_tiers（城市分级数据）
-- ============================================================
CREATE TABLE IF NOT EXISTS city_tiers (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    city_name TEXT NOT NULL,
    tier INTEGER CHECK(tier IN (1, 2, 3)),
    region_score INTEGER CHECK(region_score BETWEEN 0 AND 100),
    created_at INTEGER DEFAULT (unixepoch())
);

INSERT OR IGNORE INTO city_tiers (city_name, tier, region_score) VALUES
('Jakarta', 1, 100),
('Surabaya', 1, 80),
('Medan', 1, 80),
('Bandung', 1, 80),
('Yogyakarta', 2, 60),
('Semarang', 2, 60),
('Makassar', 2, 60),
('Bali', 2, 60),
('Other', 3, 40);


-- ============================================================
-- 7. search_queries（预置搜索词库）
-- ============================================================
CREATE TABLE IF NOT EXISTS search_queries (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    keyword TEXT NOT NULL,
    location TEXT,
    city TEXT,
    tier INTEGER DEFAULT 2,
    is_active BOOLEAN DEFAULT 1,
    last_imported_at INTEGER,
    created_at INTEGER DEFAULT (unixepoch())
);

INSERT OR IGNORE INTO search_queries (keyword, location, city, tier) VALUES
('warung Jakarta', '-6.2088,106.8456,14z', 'Jakarta', 1),
('warung makan Jakarta', '-6.2088,106.8456,14z', 'Jakarta', 1),
('toko kelontong Jakarta', '-6.2088,106.8456,14z', 'Jakarta', 1),
('warung Surabaya', '-7.2575,112.7521,14z', 'Surabaya', 1),
('toko kelontong Surabaya', '-7.2575,112.7521,14z', 'Surabaya', 1),
('warung Bali', '-8.3405,115.0920,14z', 'Bali', 2),
('warung makan Bali', '-8.3405,115.0920,14z', 'Bali', 2),
('warung Bandung', '-6.9175,107.6191,14z', 'Bandung', 1),
('toko kelontong Bandung', '-6.9175,107.6191,14z', 'Bandung', 1),
('warung Medan', '3.5952,98.6722,14z', 'Medan', 1),
('toko kelontong Medan', '3.5952,98.6722,14z', 'Medan', 1),
('warung Yogyakarta', '-7.7956,110.3695,14z', 'Yogyakarta', 2),
('toko kelontong Yogyakarta', '-7.7956,110.3695,14z', 'Yogyakarta', 2),
('warung Makassar', '-5.1477,119.4327,14z', 'Makassar', 2),
('warung Semarang', '-6.9667,110.4167,14z', 'Semarang', 2);


-- ============================================================
-- 8. 初始化完成
-- ============================================================
-- 查询验证
SELECT '✅ 数据库初始化完成！' as status;
SELECT COUNT(*) as total_tables FROM sqlite_master WHERE type='table';
SELECT name as table_name FROM sqlite_master WHERE type='table' ORDER BY name;
