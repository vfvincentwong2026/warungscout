#!/usr/bin/env bash
# WarungScout D1 → Nusantara Brand OS 渠道地图 一键同步
# 用法：bash scripts/sync-to-brandos.sh           # 导本地 D1（wrangler dev 数据）
#       WS_REMOTE=1 bash scripts/sync-to-brandos.sh   # 导远端生产 D1
# 环境变量：BRAND_OS_DIR（Brand OS 仓库路径，默认 ../nusantara-brand-os）
set -euo pipefail

cd "$(dirname "$0")/.."
DB_NAME="${WS_DB:-warungscout_db}"
BRAND_OS_DIR="${BRAND_OS_DIR:-../nusantara-brand-os}"
OUT=".tmp/warungs_export.sql"
mkdir -p .tmp

REMOTE_FLAG=""
if [[ "${WS_REMOTE:-0}" == "1" ]]; then
  REMOTE_FLAG="--remote"
  echo "→ 导出远端 D1: $DB_NAME"
else
  echo "→ 导出本地 D1: $DB_NAME（生产数据请用 WS_REMOTE=1）"
fi

npx wrangler d1 export "$DB_NAME" $REMOTE_FLAG --table warungs --output "$OUT" -y
OUT_ABS="$(pwd -W 2>/dev/null || pwd)/$OUT"

echo "→ 灌入 Brand OS: $BRAND_OS_DIR"
(cd "$BRAND_OS_DIR" && python -m nbo.importer.warungscout --src "$OUT_ABS" --db nbo.db --replace)

echo "✅ 同步完成。刷新地图：python -m nbo.channel --out web/map/data/channel_map.json && python scripts/deploy.py"
