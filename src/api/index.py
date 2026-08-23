# ============================================================
# WarungScout Cloudflare Worker 入口
# 框架: FastAPI
# 部署平台: Cloudflare Workers (Python 3.10+)
# ============================================================

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# 1. Pydantic 数据模型（API 请求/响应）
# ============================================================

class WarungBase(BaseModel):
    """Warung 基础信息"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    city: Optional[str] = None

class WarungCreate(WarungBase):
    """创建 Warung 请求"""
    source: str = "manual"
    gm_place_id: Optional[str] = None
    gm_rating: Optional[float] = None
    gm_reviews: Optional[int] = None

class FeedbackRequest(BaseModel):
    """反馈提交请求"""
    warung_id: str
    feedback_type: str  # wa_replied, visit_agreed, trial_ordered, etc.
    note: Optional[str] = None

class ImportRequest(BaseModel):
    """Google Maps 抓取请求"""
    query: str
    location: Optional[str] = None
    max_results: int = 100
    source_type: str = "serpapi"  # serpapi | places_api | playwright

class ScoreResponse(BaseModel):
    """评分响应"""
    warung_id: str
    warung_name: str
    total_score: int
    grade: str
    grade_label: str
    breakdown: Dict[str, Any]

class AdviceResponse(BaseModel):
    """步骤建议响应"""
    warung_id: str
    warung_name: str
    current_step: int
    current_step_name: str
    next_step: int
    next_step_name: str
    action: str
    description: str
    priority: str
    timeout_days: int
    channel: Optional[str]

# ============================================================
# 2. 依赖注入
# ============================================================

def get_db():
    """获取 D1 数据库连接"""
    # 在 Cloudflare Worker 中通过 env.DB 获取
    # 本地开发时通过 wrangler dev 注入
    pass

def get_settings():
    """获取应用配置"""
    # 从环境变量读取
    pass

# ============================================================
# 3. FastAPI 应用
# ============================================================

app = FastAPI(
    title="WarungScout API",
    description="印尼 Warung 智能评分与销售导航系统",
    version="1.0.0",
)

# ---------- CORS 中间件 ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://warungscout.com",
        "https://*.warungscout.com",
        "http://localhost:5173",
        "http://localhost:8501",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 4. API 路由
# ============================================================

# ---------- 健康检查 ----------
@app.get("/", tags=["health"])
async def root():
    """API 根路径"""
    return {
        "name": "WarungScout API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["health"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# ---------- 统计概览 ----------
@app.get("/api/stats", tags=["stats"])
async def get_stats():
    """
    获取统计概览
    - total: 总 Warung 数
    - gold_count: 黄金 Warung 数
    - silver_count: 白银 Warung 数
    - potential_count: 潜力 Warung 数
    - normal_count: 普通 Warung 数
    - from_google_maps: Google Maps 抓取数
    - from_manual: 人工录入数
    - avg_score: 平均评分
    """
    # TODO: 实现从 D1 读取统计数据
    return {
        "total": 520,
        "gold_count": 78,
        "silver_count": 156,
        "potential_count": 186,
        "normal_count": 100,
        "from_google_maps": 320,
        "from_manual": 200,
        "avg_score": 62,
        "today_tasks": 5
    }

# ---------- Warung 列表 ----------
@app.get("/api/warungs", tags=["warungs"])
async def list_warungs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    grade: Optional[str] = Query(None, regex="^(gold|silver|potential|normal|all)$"),
    step: Optional[int] = Query(None, ge=0, le=5),
    region: Optional[str] = None,
    source: Optional[str] = Query(None, regex="^(google_maps|manual|api|all)$"),
    sort: str = Query("final_score_desc"),
    search: Optional[str] = None,
):
    """
    获取 Warung 列表（分页 + 筛选 + 排序）
    """
    # TODO: 实现从 D1 查询
    # 当前返回模拟数据
    return {
        "items": [],
        "total": 0,
        "page": page,
        "limit": limit,
        "total_pages": 0
    }

# ---------- Warung 详情 ----------
@app.get("/api/warungs/{warung_id}", tags=["warungs"])
async def get_warung(warung_id: str):
    """
    获取 Warung 详情（含评分明细、步骤建议、历史记录）
    """
    # TODO: 实现从 D1 查询
    return {
        "id": warung_id,
        "name": "Warung Bu Siti",
        "phone": "+62 812-3456-7890",
        "address": "Jl. Raya Canggu No. 45, Bali",
        "source": "google_maps",
        "final_score": 87,
        "grade": "gold",
        "grade_label": "黄金",
        "breakdown": {
            "location": {"score": 85, "weighted": 21.25},
            "activity": {"score": 70, "weighted": 14.00},
            "competition": {"score": 90, "weighted": 13.50},
            "cooperation": {"score": 80, "weighted": 12.00},
            "digital": {"score": 75, "weighted": 11.25},
            "owner": {"score": 65, "weighted": 3.25},
            "region": {"score": 85, "weighted": 4.25}
        },
        "sales_step": 2,
        "step_status": "in_progress",
        "next_action": "安排地推团队上门拜访",
        "history": []
    }

# ---------- 获取评分 ----------
@app.get("/api/score/{warung_id}", tags=["score"])
async def get_score(warung_id: str):
    """获取 Warung 的 7 维评分"""
    # TODO: 实现评分计算
    return {
        "warung_id": warung_id,
        "total_score": 87,
        "grade": "gold",
        "grade_label": "黄金",
        "breakdown": {
            "location": 85,
            "activity": 70,
            "competition": 90,
            "cooperation": 80,
            "digital": 75,
            "owner": 65,
            "region": 85
        }
    }

# ---------- 获取步骤建议 ----------
@app.get("/api/advice/{warung_id}", tags=["advice"])
async def get_advice(warung_id: str):
    """获取 Warung 的下一步销售建议"""
    # TODO: 实现建议生成
    return {
        "warung_id": warung_id,
        "current_step": 1,
        "current_step_name": "首次破冰",
        "next_step": 2,
        "next_step_name": "初次拜访",
        "action": "安排地推团队上门拜访",
        "description": "店主已回复 WA，建议 3 天内完成首次拜访",
        "priority": "high",
        "timeout_days": 3,
        "channel": "visit",
        "template": "VISIT_SCRIPT_V1"
    }

# ---------- 提交反馈 ----------
@app.post("/api/feedback", tags=["feedback"])
async def submit_feedback(feedback: FeedbackRequest):
    """
    提交销售反馈，触发评分动态调整和步骤更新
    """
    # TODO: 实现反馈闭环
    return {
        "success": True,
        "warung_id": feedback.warung_id,
        "feedback_type": feedback.feedback_type,
        "score_delta": {"cooperation": 0, "digital": 0, "total": 0},
        "new_score": 87,
        "new_grade": "gold",
        "new_step": 2,
        "message": "反馈已记录，评分已更新"
    }

# ---------- 触发 Google Maps 抓取 ----------
@app.post("/api/import/google-maps", tags=["import"])
async def trigger_import(import_request: ImportRequest):
    """触发 Google Maps 抓取任务"""
    # TODO: 实现 Google Maps 抓取
    task_id = "task_" + datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "success": True,
        "task_id": task_id,
        "query": import_request.query,
        "max_results": import_request.max_results,
        "source_type": import_request.source_type,
        "status": "pending",
        "message": "抓取任务已创建，正在后台处理..."
    }

# ---------- 获取抓取任务状态 ----------
@app.get("/api/import/tasks", tags=["import"])
async def list_import_tasks(limit: int = 20):
    """获取最近的抓取任务列表"""
    # TODO: 实现从 D1 查询
    return {
        "items": [],
        "total": 0
    }

@app.get("/api/import/tasks/{task_id}", tags=["import"])
async def get_import_task(task_id: str):
    """获取抓取任务详情"""
    # TODO: 实现从 D1 查询
    return {
        "id": task_id,
        "query": "warung Jakarta",
        "status": "completed",
        "total_found": 50,
        "total_imported": 48,
        "created_at": 1724200000,
        "completed_at": 1724200300
    }

# ---------- 获取今日待办 ----------
@app.get("/api/tasks", tags=["tasks"])
async def get_tasks(
    priority: Optional[str] = Query(None, regex="^(high|medium|low|all)$")
):
    """获取今日待办任务列表"""
    # TODO: 实现从 D1 查询
    return {
        "items": [
            {
                "id": "task_1",
                "warung_id": "w_001",
                "warung_name": "Warung Bu Siti",
                "action": "WA破冰",
                "priority": "high",
                "deadline": "今日",
                "channel": "whatsapp"
            }
        ],
        "total": 5,
        "high": 2,
        "medium": 3,
        "low": 0
    }

# ============================================================
# 5. 错误处理
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": 500,
            "message": "内部服务器错误，请稍后重试",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================
# 6. Cloudflare Worker 入口（保持兼容）
# ============================================================

async def fetch(request: Request) -> Response:
    """Cloudflare Worker 入口"""
    return await app(request)


# ============================================================
# 7. 本地开发入口（uvicorn）
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.index:app",
        host="0.0.0.0",
        port=8787,
        reload=True
    )
