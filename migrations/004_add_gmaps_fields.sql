-- ============================================================
-- WarungScout 增量迁移脚本
-- 版本: 004
-- 说明: 为 warungs 表添加 Google Maps 相关字段
-- 适用场景: 已有数据库，需要升级到支持 Google Maps 抓取
-- 执行: npx wrangler d1 execute warungscout_db --file=./migrations/004_add_gmaps_fields.sql
-- ============================================================

-- ============================================================
-- 1. 添加 Google Maps 字段
-- ============================================================

-- 数据来源追踪字段
ALTER TABLE warungs ADD COLUMN source TEXT DEFAULT 'manual' CHECK(source IN ('google_maps', 'manual', 'api'));
ALTER TABLE warungs ADD COLUMN source_import_id TEXT;
ALTER TABLE warungs ADD COLUMN source_imported_at INTEGER;

-- Google Maps 原始数据字段
ALTER TABLE warungs ADD COLUMN gm_place_id TEXT;
ALTER TABLE warungs ADD COLUMN gm_rating REAL;
ALTER TABLE warungs ADD COLUMN gm_reviews INTEGER;
ALTER TABLE warungs ADD COLUMN gm_types TEXT;
ALTER TABLE warungs ADD COLUMN gm_plus_code TEXT;

-- 数据完整性标记
ALTER TABLE warungs ADD COLUMN data_completeness TEXT DEFAULT 'basic' CHECK(data_completeness IN ('basic', 'partial', 'complete'));


-- ============================================================
-- 2. 添加索引（如果不存在）
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_warungs_source ON warungs(source);
CREATE INDEX IF NOT EXISTS idx_warungs_gm_place_id ON warungs(gm_place_id);


-- ============================================================
-- 3. 创建 Google Maps 抓取任务表（如果不存在）
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
-- 4. 创建预置搜索词表（如果不存在）
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
-- 5. 验证迁移
-- ============================================================

-- 检查 warungs 表新增字段
SELECT '✅ 迁移完成！已添加以下 Google Maps 字段:' as status;

SELECT column_name AS 新增字段
FROM pragma_table_info('warungs')
WHERE column_name IN (
    'source', 'source_import_id', 'source_imported_at',
    'gm_place_id', 'gm_rating', 'gm_reviews', 'gm_types', 'gm_plus_code',
    'data_completeness'
)
ORDER BY column_name;
