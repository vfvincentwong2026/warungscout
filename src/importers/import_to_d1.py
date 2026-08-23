# ============================================================
# WarungScout 数据导入器
# 功能: 将抓取的数据导入 Cloudflare D1 数据库
# 版本: v1.0.0
# ============================================================

import json
import csv
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


# ============================================================
# 1. D1 导入器
# ============================================================

class D1Importer:
    """D1 数据库导入器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化导入器

        Args:
            db_path: SQLite 数据库路径（本地开发）
                    如果为 None，则使用环境变量或默认路径
        """
        if db_path is None:
            db_path = os.getenv('LOCAL_DB_PATH', './data/warungscout.db')

        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._conn = None

    def _get_conn(self):
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _execute(self, sql: str, params: tuple = ()):
        """执行 SQL 语句"""
        conn = self._get_conn()
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor

    def _execute_many(self, sql: str, params_list: List[tuple]):
        """批量执行 SQL 语句"""
        conn = self._get_conn()
        cursor = conn.executemany(sql, params_list)
        conn.commit()
        return cursor

    def _fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        conn = self._get_conn()
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def _fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录"""
        conn = self._get_conn()
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    # ============================================================
    # 2. 单条导入
    # ============================================================

    def import_one(self, warung_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        导入单条 Warung 数据

        Args:
            warung_data: Warung 数据字典

        Returns:
            {
                'success': bool,
                'warung_id': str,
                'message': str,
                'is_new': bool,      # 是否新插入（vs 更新）
            }
        """
        # 检查是否已存在（通过 place_id 或 name + address）
        existing = None

        gm_place_id = warung_data.get('gm_place_id')
        if gm_place_id:
            existing = self._fetch_one(
                "SELECT id FROM warungs WHERE gm_place_id = ?",
                (gm_place_id,)
            )

        if not existing:
            # 尝试通过 name + address 去重
            name = warung_data.get('name', '')
            address = warung_data.get('address', '')
            if name and address:
                existing = self._fetch_one(
                    "SELECT id FROM warungs WHERE name = ? AND address = ?",
                    (name, address)
                )

        if existing:
            # 更新已存在的记录
            warung_id = existing['id']
            self._update_warung(warung_id, warung_data)
            return {
                'success': True,
                'warung_id': warung_id,
                'message': '已更新现有记录',
                'is_new': False,
            }
        else:
            # 插入新记录
            warung_id = self._insert_warung(warung_data)
            return {
                'success': True,
                'warung_id': warung_id,
                'message': '成功导入新记录',
                'is_new': True,
            }

    def _insert_warung(self, data: Dict[str, Any]) -> str:
        """插入新 Warung 记录"""
        import uuid

        warung_id = str(uuid.uuid4())
        now = int(datetime.now().timestamp())

        sql = """
        INSERT INTO warungs (
            id, name, phone, email, address, latitude, longitude,
            region, city, source, source_import_id, source_imported_at,
            gm_place_id, gm_rating, gm_reviews, gm_types, gm_plus_code,
            location_score, activity_score, competition_score,
            cooperation_score, digital_score, owner_score, region_score,
            final_score, grade, sales_step, step_status,
            data_completeness, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            warung_id,
            data.get('name', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data.get('latitude'),
            data.get('longitude'),
            data.get('region', ''),
            data.get('city', ''),
            data.get('source', 'google_maps'),
            data.get('source_import_id', ''),
            data.get('source_imported_at', now),
            data.get('gm_place_id', ''),
            data.get('gm_rating', 0.0),
            data.get('gm_reviews', 0),
            data.get('gm_types', '[]'),
            data.get('gm_plus_code', ''),
            data.get('location_score', 50),
            data.get('activity_score', 50),
            data.get('competition_score', 50),
            data.get('cooperation_score', 50),
            data.get('digital_score', 50),
            data.get('owner_score', 50),
            data.get('region_score', 50),
            data.get('final_score', 0),
            data.get('grade', 'normal'),
            data.get('sales_step', 0),
            data.get('step_status', 'pending'),
            data.get('data_completeness', 'basic'),
            data.get('created_at', now),
            data.get('updated_at', now),
        )

        self._execute(sql, params)

        # 记录评分历史
        self._insert_score_history(warung_id, 0, data.get('final_score', 0), 'gmaps_imported')

        return warung_id

    def _update_warung(self, warung_id: str, data: Dict[str, Any]):
        """更新已有 Warung 记录"""
        now = int(datetime.now().timestamp())

        # 获取旧分数
        old = self._fetch_one(
            "SELECT final_score FROM warungs WHERE id = ?",
            (warung_id,)
        )
        old_score = old['final_score'] if old else 0

        sql = """
        UPDATE warungs SET
            name = ?, phone = ?, email = ?, address = ?,
            latitude = ?, longitude = ?, region = ?, city = ?,
            source = ?, source_import_id = ?, source_imported_at = ?,
            gm_place_id = ?, gm_rating = ?, gm_reviews = ?, gm_types = ?, gm_plus_code = ?,
            location_score = ?, activity_score = ?, competition_score = ?,
            cooperation_score = ?, digital_score = ?, owner_score = ?, region_score = ?,
            final_score = ?, grade = ?, sales_step = ?, step_status = ?,
            data_completeness = ?, updated_at = ?
        WHERE id = ?
        """

        params = (
            data.get('name', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data.get('latitude'),
            data.get('longitude'),
            data.get('region', ''),
            data.get('city', ''),
            data.get('source', 'google_maps'),
            data.get('source_import_id', ''),
            data.get('source_imported_at', now),
            data.get('gm_place_id', ''),
            data.get('gm_rating', 0.0),
            data.get('gm_reviews', 0),
            data.get('gm_types', '[]'),
            data.get('gm_plus_code', ''),
            data.get('location_score', 50),
            data.get('activity_score', 50),
            data.get('competition_score', 50),
            data.get('cooperation_score', 50),
            data.get('digital_score', 50),
            data.get('owner_score', 50),
            data.get('region_score', 50),
            data.get('final_score', 0),
            data.get('grade', 'normal'),
            data.get('sales_step', 0),
            data.get('step_status', 'pending'),
            data.get('data_completeness', 'basic'),
            now,
            warung_id,
        )

        self._execute(sql, params)

        # 如果分数有变化，记录历史
        new_score = data.get('final_score', 0)
        if new_score != old_score:
            self._insert_score_history(warung_id, old_score, new_score, 'gmaps_imported')

    def _insert_score_history(self, warung_id: str, score_before: int, score_after: int, feedback_type: str):
        """插入评分历史"""
        import uuid

        sql = """
        INSERT INTO score_history (
            id, warung_id, score_before, score_after, feedback_type, reason, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            str(uuid.uuid4()),
            warung_id,
            score_before,
            score_after,
            feedback_type,
            f'自动导入: {feedback_type}',
            int(datetime.now().timestamp()),
        )

        self._execute(sql, params)

    # ============================================================
    # 3. 批量导入
    # ============================================================

    def import_batch(self, warung_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量导入 Warung 数据

        Args:
            warung_list: Warung 数据列表

        Returns:
            {
                'total': int,
                'inserted': int,
                'updated': int,
                'failed': int,
                'errors': list,
                'warung_ids': list,
            }
        """
        result = {
            'total': len(warung_list),
            'inserted': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
            'warung_ids': [],
        }

        for i, warung_data in enumerate(warung_list):
            try:
                import_result = self.import_one(warung_data)
                if import_result['success']:
                    result['warung_ids'].append(import_result['warung_id'])
                    if import_result['is_new']:
                        result['inserted'] += 1
                    else:
                        result['updated'] += 1
                else:
                    result['failed'] += 1
                    result['errors'].append({
                        'index': i,
                        'data': warung_data.get('name', '未知'),
                        'error': import_result.get('message', '未知错误'),
                    })
            except Exception as e:
                result['failed'] += 1
                result['errors'].append({
                    'index': i,
                    'data': warung_data.get('name', '未知'),
                    'error': str(e),
                })

        return result

    # ============================================================
    # 4. 从 CSV/JSON 导入
    # ============================================================

    def import_from_csv(self, file_path: str) -> Dict[str, Any]:
        """从 CSV 文件导入"""
        warung_list = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                warung_data = self._csv_row_to_dict(row)
                warung_list.append(warung_data)

        logger.info(f"从 CSV 读取了 {len(warung_list)} 条记录")
        return self.import_batch(warung_list)

    def import_from_json(self, file_path: str) -> Dict[str, Any]:
        """从 JSON 文件导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            warung_list = data
        elif isinstance(data, dict) and 'items' in data:
            warung_list = data['items']
        else:
            raise ValueError("JSON 格式不正确，应为列表或包含 items 字段的对象")

        logger.info(f"从 JSON 读取了 {len(warung_list)} 条记录")
        return self.import_batch(warung_list)

    def _csv_row_to_dict(self, row: Dict[str, str]) -> Dict[str, Any]:
        """将 CSV 行转换为 Warung 数据字典"""
        # 尝试解析数值字段
        def parse_float(v):
            try:
                return float(v) if v else None
            except:
                return None

        def parse_int(v):
            try:
                return int(v) if v else 0
            except:
                return 0

        return {
            'name': row.get('name', ''),
            'phone': row.get('phone', ''),
            'email': row.get('email', ''),
            'address': row.get('address', ''),
            'latitude': parse_float(row.get('latitude')),
            'longitude': parse_float(row.get('longitude')),
            'city': row.get('city', ''),
            'region': row.get('region', ''),
            'source': 'manual',
            'gm_place_id': row.get('place_id', ''),
            'gm_rating': parse_float(row.get('rating')),
            'gm_reviews': parse_int(row.get('reviews')),
            'gm_types': row.get('types', '[]'),
        }

    # ============================================================
    # 5. 任务管理
    # ============================================================

    def create_import_task(self, query: str, location: str = None,
                           max_results: int = 100, source_type: str = 'serpapi') -> str:
        """创建导入任务"""
        import uuid

        task_id = str(uuid.uuid4())
        now = int(datetime.now().timestamp())

        sql = """
        INSERT INTO google_maps_import_tasks (
            id, query, location, max_results, source_type,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            task_id,
            query,
            location,
            max_results,
            source_type,
            'pending',
            now,
            now,
        )

        self._execute(sql, params)
        return task_id

    def update_task_status(self, task_id: str, status: str,
                           total_found: int = 0, total_imported: int = 0,
                           error_message: str = None):
        """更新任务状态"""
        now = int(datetime.now().timestamp())

        sql = """
        UPDATE google_maps_import_tasks SET
            status = ?,
            total_found = ?,
            total_imported = ?,
            error_message = ?,
            completed_at = ?,
            updated_at = ?
        WHERE id = ?
        """

        completed_at = now if status in ['completed', 'failed'] else None

        params = (
            status,
            total_found,
            total_imported,
            error_message,
            completed_at,
            now,
            task_id,
        )

        self._execute(sql, params)


# ============================================================
# 6. 命令行接口
# ============================================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='WarungScout 数据导入器')
    parser.add_argument('--file', '-f', help='导入文件路径 (CSV 或 JSON)')
    parser.add_argument('--format', choices=['csv', 'json'], help='文件格式')
    parser.add_argument('--db', help='数据库路径')
    parser.add_argument('--list', action='store_true', help='列出所有 Warung')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    importer = D1Importer(args.db)

    try:
        if args.list:
            # 列出所有 Warung
            rows = importer._fetch_all(
                "SELECT id, name, phone, address, city, final_score, grade FROM warungs LIMIT 20"
            )
            print(f"{'ID':<8} {'名称':<20} {'城市':<12} {'分数':<6} {'等级':<8}")
            print('-' * 60)
            for row in rows:
                print(f"{row['id'][:8]:<8} {row['name'][:20]:<20} {row['city'][:12]:<12} {row['final_score']:<6} {row['grade']:<8}")
            print(f"\n共 {len(rows)} 条记录")

        elif args.file:
            # 导入文件
            if args.format == 'json':
                result = importer.import_from_json(args.file)
            elif args.format == 'csv':
                result = importer.import_from_csv(args.file)
            else:
                # 自动检测格式
                if args.file.endswith('.json'):
                    result = importer.import_from_json(args.file)
                elif args.file.endswith('.csv'):
                    result = importer.import_from_csv(args.file)
                else:
                    print("无法识别文件格式，请指定 --format")
                    return

            print(f"\n导入完成！")
            print(f"总计: {result['total']} 条")
            print(f"新增: {result['inserted']} 条")
            print(f"更新: {result['updated']} 条")
            print(f"失败: {result['failed']} 条")

            if result['errors']:
                print(f"\n错误详情:")
                for err in result['errors'][:5]:
                    print(f"  - 第 {err['index']+1} 条: {err['data']} - {err['error']}")

        else:
            parser.print_help()

    finally:
        importer.close()


if __name__ == "__main__":
    main()
