# ============================================================
# WarungScout Google Maps 抓取器
# 功能: 从 Google Maps 自动抓取 Warung 数据
# 支持三种方案:
#   1. SerpApi (推荐 MVP 阶段，稳定)
#   2. Google Places API (官方接口，合规)
#   3. Playwright 自建爬虫 (备用)
# 版本: v1.0.0
# ============================================================

import json
import time
import csv
import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
import os
from dataclasses import dataclass, field

# HTTP 请求
import httpx

# 可选依赖: Playwright (仅在需要时导入)
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================
# 1. 数据模型
# ============================================================

@dataclass
class WarungData:
    """Warung 数据抓取结果"""
    # 基础信息
    name: str
    address: str
    phone: str = ""
    website: str = ""
    email: str = ""
    
    # 位置
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    plus_code: str = ""
    
    # Google Maps 数据
    place_id: str = ""
    rating: float = 0.0
    reviews: int = 0
    types: List[str] = field(default_factory=list)
    
    # 城市/区域
    city: str = ""
    region: str = ""
    
    # 抓取元数据
    source_type: str = "serpapi"
    raw_data: Dict[str, Any] = field(default_factory=dict)
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_warung_dict(self) -> Dict[str, Any]:
        """转换为 WarungScout 的 warung 字典格式"""
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'region': self.region,
            'source': 'google_maps',
            'source_import_id': self.place_id,
            'source_imported_at': int(datetime.now().timestamp()),
            'gm_place_id': self.place_id,
            'gm_rating': self.rating,
            'gm_reviews': self.reviews,
            'gm_types': json.dumps(self.types) if self.types else '[]',
            'gm_plus_code': self.plus_code,
            'data_completeness': 'basic',
            # 评分维度默认值（后续由评分引擎计算）
            'location_score': 50,
            'activity_score': 50,
            'competition_score': 50,
            'cooperation_score': 50,
            'digital_score': 50,
            'owner_score': 50,
            'region_score': 50,
            'final_score': 0,
            'grade': 'normal',
            'sales_step': 0,
            'step_status': 'pending',
            'created_at': int(datetime.now().timestamp()),
            'updated_at': int(datetime.now().timestamp()),
        }


# ============================================================
# 2. SerpApi 抓取器
# ============================================================

class SerpApiImporter:
    """使用 SerpApi 抓取 Google Maps 数据"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.timeout = 30
    
    def search(self, query: str, location: Optional[str] = None, max_results: int = 100) -> List[WarungData]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词（如 "warung Jakarta"）
            location: GPS 坐标（如 "-6.2088,106.8456,14z"）
            max_results: 最大结果数
            
        Returns:
            WarungData 列表
        """
        all_results = []
        start = 0
        
        while len(all_results) < max_results:
            params = {
                "api_key": self.api_key,
                "engine": "google_maps",
                "q": query,
                "start": start,
                "num": 20,  # SerpApi 每页最多 20 条
            }
            
            if location:
                params["ll"] = location
            
            try:
                logger.info(f"请求 SerpApi: query={query}, start={start}")
                response = httpx.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                # 检查错误
                if data.get('error'):
                    logger.error(f"SerpApi 错误: {data.get('error')}")
                    break
                
                local_results = data.get('local_results', [])
                if not local_results:
                    break
                
                # 转换为 WarungData
                for item in local_results:
                    warung = self._parse_result(item)
                    if warung:
                        all_results.append(warung)
                
                # 检查是否还有更多结果
                if not data.get('pagination', {}).get('next'):
                    break
                
                start += 20
                
                # 避免频率过高
                time.sleep(0.5)
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP 错误: {e}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析错误: {e}")
                break
            except Exception as e:
                logger.error(f"未知错误: {e}")
                break
        
        return all_results[:max_results]
    
    def _parse_result(self, item: Dict[str, Any]) -> Optional[WarungData]:
        """解析 SerpApi 返回的结果"""
        try:
            # 提取坐标
            gps = item.get('gps_coordinates', {})
            lat = gps.get('latitude')
            lng = gps.get('longitude')
            
            # 提取地址
            address = item.get('address', '')
            
            # 提取城市
            city = self._extract_city(address)
            region = self._extract_region(address)
            
            return WarungData(
                name=item.get('title', ''),
                address=address,
                phone=item.get('phone', ''),
                website=item.get('website', ''),
                latitude=lat,
                longitude=lng,
                place_id=item.get('place_id', ''),
                rating=item.get('rating', 0.0),
                reviews=item.get('reviews', 0),
                types=item.get('types', []),
                city=city,
                region=region,
                source_type='serpapi',
                raw_data=item,
            )
        except Exception as e:
            logger.warning(f"解析结果失败: {e}")
            return None
    
    def _extract_city(self, address: str) -> str:
        """从地址提取城市"""
        if not address:
            return ''
        # 简单规则：匹配常见城市名
        cities = ['Jakarta', 'Surabaya', 'Medan', 'Bandung', 'Bali', 
                  'Yogyakarta', 'Semarang', 'Makassar']
        for city in cities:
            if city.lower() in address.lower():
                return city
        return ''
    
    def _extract_region(self, address: str) -> str:
        """从地址提取区域"""
        if not address:
            return ''
        # 提取省份或区域
        parts = address.split(',')
        if len(parts) >= 3:
            return parts[-2].strip()
        return ''


# ============================================================
# 3. Google Places API 抓取器
# ============================================================

class PlacesAPIImporter:
    """使用 Google Places API 抓取数据"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.timeout = 30
    
    def search(self, query: str, location: Optional[str] = None, max_results: int = 100) -> List[WarungData]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            location: GPS 坐标（如 "-6.2088,106.8456"）
            max_results: 最大结果数
            
        Returns:
            WarungData 列表
        """
        all_results = []
        next_page_token = None
        
        # 解析坐标
        lat, lng = self._parse_location(location)
        
        while len(all_results) < max_results:
            params = {
                "key": self.api_key,
                "query": query,
                "inputtype": "textquery",
                "fields": "place_id,name,formatted_address,formatted_phone_number,website,geometry,rating,user_ratings_total,types,plus_code",
            }
            
            if lat and lng:
                params["location"] = f"{lat},{lng}"
                params["radius"] = 50000  # 50km
            
            if next_page_token:
                params["pagetoken"] = next_page_token
            
            try:
                logger.info(f"请求 Places API: query={query}")
                response = httpx.get(f"{self.base_url}/findplacefromtext/json", 
                                     params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') != 'OK':
                    logger.error(f"Places API 错误: {data.get('status')}")
                    break
                
                candidates = data.get('candidates', [])
                for candidate in candidates:
                    warung = self._parse_result(candidate)
                    if warung:
                        all_results.append(warung)
                
                # 获取下一页 token
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break
                
                # Places API 要求等待 2 秒后才能使用下一页 token
                time.sleep(2)
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP 错误: {e}")
                break
            except Exception as e:
                logger.error(f"未知错误: {e}")
                break
        
        return all_results[:max_results]
    
    def _parse_result(self, item: Dict[str, Any]) -> Optional[WarungData]:
        """解析 Places API 返回的结果"""
        try:
            geometry = item.get('geometry', {})
            location = geometry.get('location', {})
            
            address = item.get('formatted_address', '')
            city = self._extract_city(address)
            region = self._extract_region(address)
            
            return WarungData(
                name=item.get('name', ''),
                address=address,
                phone=item.get('formatted_phone_number', ''),
                website=item.get('website', ''),
                latitude=location.get('lat'),
                longitude=location.get('lng'),
                place_id=item.get('place_id', ''),
                rating=item.get('rating', 0.0),
                reviews=item.get('user_ratings_total', 0),
                types=item.get('types', []),
                city=city,
                region=region,
                source_type='places_api',
                raw_data=item,
            )
        except Exception as e:
            logger.warning(f"解析结果失败: {e}")
            return None
    
    def _parse_location(self, location: Optional[str]) -> tuple:
        """解析位置字符串"""
        if not location:
            return None, None
        parts = location.replace(',', ' ').split()
        if len(parts) >= 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                pass
        return None, None
    
    def _extract_city(self, address: str) -> str:
        """从地址提取城市"""
        if not address:
            return ''
        cities = ['Jakarta', 'Surabaya', 'Medan', 'Bandung', 'Bali', 
                  'Yogyakarta', 'Semarang', 'Makassar']
        for city in cities:
            if city.lower() in address.lower():
                return city
        return ''
    
    def _extract_region(self, address: str) -> str:
        """从地址提取区域"""
        if not address:
            return ''
        parts = address.split(',')
        if len(parts) >= 3:
            return parts[-2].strip()
        return ''


# ============================================================
# 4. Playwright 抓取器（自建爬虫）
# ============================================================

class PlaywrightImporter:
    """使用 Playwright 自建爬虫"""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.timeout = 60000
        self.delay = 2
    
    def search(self, query: str, max_results: int = 50) -> List[WarungData]:
        """执行搜索"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright 未安装，请运行: playwright install chromium")
            return []
        
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                locale='id-ID',
            )
            
            if self.proxy:
                context.set_extra_http_headers({'Proxy-Authorization': self.proxy})
            
            page = context.new_page()
            
            try:
                # 构建 URL
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                logger.info(f"访问: {search_url}")
                
                page.goto(search_url, timeout=self.timeout)
                time.sleep(self.delay)
                
                # 滚动加载更多
                self._scroll_page(page, max_results)
                
                # 提取结果
                results = self._extract_results(page)
                
            except Exception as e:
                logger.error(f"抓取失败: {e}")
            
            browser.close()
        
        return results[:max_results]
    
    def _scroll_page(self, page: Page, max_results: int):
        """滚动页面以加载更多结果"""
        for _ in range(max_results // 10 + 1):
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1)
            
            # 检查是否到底
            is_bottom = page.evaluate("""
                () => {
                    const el = document.querySelector('div.section-layout');
                    return el ? el.scrollHeight - el.scrollTop <= 1000 : false;
                }
            """)
            if is_bottom:
                break
    
    def _extract_results(self, page: Page) -> List[WarungData]:
        """从页面提取结果"""
        results = []
        
        # 等待结果容器加载
        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except:
            logger.warning("未找到结果容器")
            return results
        
        items = page.query_selector_all('div[role="article"]')
        
        for item in items:
            try:
                name_el = item.query_selector('div[role="heading"]')
                name = name_el.inner_text() if name_el else ''
                
                address_el = item.query_selector('div[class*="address"]')
                address = address_el.inner_text() if address_el else ''
                
                # 提取电话
                phone_el = item.query_selector('a[href*="tel:"]')
                phone = phone_el.get_attribute('href').replace('tel:', '') if phone_el else ''
                
                # 提取评分
                rating_el = item.query_selector('span[aria-hidden*="true"]')
                rating = float(rating_el.inner_text().replace(',', '.')) if rating_el else 0.0
                
                # 提取评论数
                reviews_el = item.query_selector('span[aria-label*="ulasan"]')
                reviews = 0
                if reviews_el:
                    text = reviews_el.inner_text()
                    reviews = int(re.search(r'(\d+)', text).group(1)) if re.search(r'(\d+)', text) else 0
                
                city = self._extract_city(address)
                region = self._extract_region(address)
                
                results.append(WarungData(
                    name=name,
                    address=address,
                    phone=phone,
                    rating=rating,
                    reviews=reviews,
                    city=city,
                    region=region,
                    source_type='playwright',
                ))
                
            except Exception as e:
                logger.warning(f"提取单个结果失败: {e}")
                continue
        
        return results
    
    def _extract_city(self, address: str) -> str:
        if not address:
            return ''
        cities = ['Jakarta', 'Surabaya', 'Medan', 'Bandung', 'Bali', 
                  'Yogyakarta', 'Semarang', 'Makassar']
        for city in cities:
            if city.lower() in address.lower():
                return city
        return ''
    
    def _extract_region(self, address: str) -> str:
        if not address:
            return ''
        parts = address.split(',')
        if len(parts) >= 3:
            return parts[-2].strip()
        return ''


# ============================================================
# 5. 统一导入器
# ============================================================

class GoogleMapsImporter:
    """统一 Google Maps 导入器"""
    
    def __init__(
        self,
        source_type: str = 'serpapi',
        api_key: Optional[str] = None,
        headless: bool = True,
        proxy: Optional[str] = None,
    ):
        """
        初始化导入器
        
        Args:
            source_type: 'serpapi' | 'places_api' | 'playwright'
            api_key: API Key (SerpApi 或 Places API)
            headless: Playwright 是否无头模式
            proxy: 代理配置 (Playwright 使用)
        """
        self.source_type = source_type
        self._importer = self._create_importer(source_type, api_key, headless, proxy)
    
    def _create_importer(self, source_type: str, api_key: Optional[str], headless: bool, proxy: Optional[str]):
        """创建具体的导入器实例"""
        if source_type == 'serpapi':
            if not api_key:
                raise ValueError("SerpApi 需要 API Key")
            return SerpApiImporter(api_key)
        elif source_type == 'places_api':
            if not api_key:
                raise ValueError("Google Places API 需要 API Key")
            return PlacesAPIImporter(api_key)
        elif source_type == 'playwright':
            return PlaywrightImporter(headless=headless, proxy=proxy)
        else:
            raise ValueError(f"不支持的来源类型: {source_type}")
    
    def search(self, query: str, location: Optional[str] = None, max_results: int = 100) -> List[WarungData]:
        """执行搜索"""
        return self._importer.search(query, location, max_results)
    
    def search_batch(self, queries: List[Dict[str, Any]], max_results: int = 50) -> List[WarungData]:
        """
        批量搜索
        
        Args:
            queries: 查询列表，每个查询包含 {'query': str, 'location': str}
            max_results: 每个查询的最大结果数
        
        Returns:
            所有 WarungData 的合并列表（已去重）
        """
        all_results = []
        place_ids = set()
        
        for q in queries:
            query = q.get('query')
            location = q.get('location')
            
            if not query:
                continue
            
            logger.info(f"批量搜索: {query}")
            results = self.search(query, location, max_results)
            
            # 去重
            for warung in results:
                if warung.place_id and warung.place_id in place_ids:
                    continue
                if warung.place_id:
                    place_ids.add(warung.place_id)
                all_results.append(warung)
            
            # 避免频率过高
            time.sleep(1)
        
        return all_results


# ============================================================
# 6. 命令行接口
# ============================================================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Maps Warung 抓取器')
    parser.add_argument('--query', '-q', required=True, help='搜索关键词')
    parser.add_argument('--location', '-l', help='位置坐标')
    parser.add_argument('--max', '-m', type=int, default=50, help='最大结果数')
    parser.add_argument('--source', '-s', default='serpapi', 
                        choices=['serpapi', 'places_api', 'playwright'],
                        help='抓取来源')
    parser.add_argument('--output', '-o', help='输出文件路径 (CSV)')
    parser.add_argument('--api-key', help='API Key')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 创建导入器
    api_key = args.api_key or os.getenv('SERPAPI_API_KEY') or os.getenv('GOOGLE_PLACES_API_KEY')
    importer = GoogleMapsImporter(source_type=args.source, api_key=api_key)
    
    # 执行搜索
    logger.info(f"开始搜索: {args.query}")
    results = importer.search(args.query, args.location, args.max)
    
    logger.info(f"找到 {len(results)} 个结果")
    
    # 输出结果
    if args.output:
        import csv
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if results:
                fieldnames = ['name', 'address', 'phone', 'website', 'email', 
                            'latitude', 'longitude', 'rating', 'reviews', 
                            'city', 'region', 'place_id']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for w in results:
                    writer.writerow({
                        'name': w.name,
                        'address': w.address,
                        'phone': w.phone,
                        'website': w.website,
                        'email': w.email,
                        'latitude': w.latitude,
                        'longitude': w.longitude,
                        'rating': w.rating,
                        'reviews': w.reviews,
                        'city': w.city,
                        'region': w.region,
                        'place_id': w.place_id,
                    })
        logger.info(f"结果已保存到: {args.output}")
    else:
        # 打印摘要
        for i, w in enumerate(results[:10]):
            print(f"{i+1}. {w.name} - {w.address} - {w.phone} - {w.rating}⭐ ({w.reviews}评论)")


if __name__ == "__main__":
    main()
