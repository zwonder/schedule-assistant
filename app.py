"""
个人工作助理 - Flask Web 后端
提供 REST API 供前端调用，保留微服务架构
"""
import sys
import os
import uuid
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory  # pyright: ignore[reportMissingImports]
from flask_cors import CORS
from core.registry import registry
from core.event_bus import event_bus
from core.config_loader import config
from services.weather.weather_service import WeatherService
from services.schedule.schedule_service import ScheduleService
from services.schedule.models import TaskType, TaskStatus

app = Flask(__name__, static_folder="web/static", static_url_path="/static")
CORS(app)  # 允许跨域，支持静态托管前端访问

# ============================================================
#  初始化微服务
# ============================================================
_weather: WeatherService = None
_schedule: ScheduleService = None


def init_services():
    global _weather, _schedule
    _weather = WeatherService()
    _schedule = ScheduleService()
    registry.register(_weather)
    registry.register(_schedule)
    registry.start_all()


# ============================================================
#  工具函数
# ============================================================
def ok(data=None, msg="success"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def err(msg="error", code=400):
    return jsonify({"code": 1, "msg": msg, "data": None}), code


# ============================================================
#  前端页面路由
# ============================================================
@app.route("/")
def index():
    return send_from_directory("web", "index.html")


# ============================================================
#  天气 API
# ============================================================
@app.route("/api/weather", methods=["GET"])
def get_weather():
    """获取完整天气数据（结构化JSON，供前端渲染）"""
    data = _weather.fetch_weather()
    if not data:
        return err("天气数据获取失败，请检查网络连接或城市名称配置", 503)
    # 新版 weather_service 直接返回已结构化的数据
    return ok(data)


@app.route("/api/weather/city", methods=["PUT"])
def set_city():
    body = request.get_json(silent=True) or {}
    city = (body.get("city") or "").strip()
    if not city:
        return err("城市名不能为空")
    _weather.set_city(city)
    config.save()
    return ok({"city": city})


# ============================================================
#  日程 API
# ============================================================
@app.route("/api/schedule/today", methods=["GET"])
def get_today():
    """获取今日日程 + 近期提醒"""
    today = date.today()
    tasks = _schedule.get_today_tasks(today)
    upcoming = _schedule.get_upcoming_reminders(days_ahead=7)

    def task_to_dict(t):
        return {
            "id": t.id,
            "short_id": t.id[:8],
            "title": t.title,
            "task_type": t.task_type,
            "status": t.status,
            "description": t.description,
            "tags": t.tags,
        }

    upcoming_list = []
    for remind_date, t in upcoming:
        diff = (remind_date - today).days
        upcoming_list.append({
            "date": str(remind_date),
            "diff_days": diff,
            "diff_label": "今天" if diff == 0 else ("明天" if diff == 1 else f"{diff}天后"),
            **task_to_dict(t),
        })

    return ok({
        "date": str(today),
        "weekday": ["周一","周二","周三","周四","周五","周六","周日"][today.weekday()],
        "tasks": [task_to_dict(t) for t in tasks],
        "upcoming": upcoming_list,
    })


@app.route("/api/schedule", methods=["GET"])
def get_all_schedule():
    """获取所有日程，按类型分组"""
    task_type = request.args.get("type")
    if task_type:
        tasks = _schedule._store.get_by_type(task_type)
    else:
        tasks = _schedule._store.get_all()

    WEEKDAY_CN = ["周一","周二","周三","周四","周五","周六","周日"]
    result = []
    for t in tasks:
        extra = {}
        if t.task_type == "yearly":
            extra["schedule_desc"] = f"每年 {t.yearly_month}/{t.yearly_day}"
        elif t.task_type == "monthly":
            day = "最后一天" if t.monthly_day == -1 else f"第{t.monthly_day}天"
            extra["schedule_desc"] = f"每月{day}"
        elif t.task_type == "weekly":
            days_str = "/".join(WEEKDAY_CN[d] for d in (t.weekly_days or []))
            extra["schedule_desc"] = f"每{days_str}"
        elif t.task_type == "daily":
            extra["schedule_desc"] = "每天"
        elif t.task_type == "once":
            extra["schedule_desc"] = t.once_date or ""

        result.append({
            "id": t.id,
            "short_id": t.id[:8],
            "title": t.title,
            "task_type": t.task_type,
            "status": t.status,
            "description": t.description,
            "tags": t.tags,
            "remind_days_before": t.remind_days_before,
            **extra,
        })

    return ok(result)


@app.route("/api/schedule", methods=["POST"])
def add_schedule():
    """新增日程"""
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        return err("任务标题不能为空")

    task_type = body.get("task_type", "")
    valid_types = [t.value for t in TaskType]
    if task_type not in valid_types:
        return err(f"无效的任务类型，可选: {valid_types}")

    kwargs = dict(
        title=title,
        task_type=task_type,
        description=body.get("description", ""),
        tags=body.get("tags", []),
        remind_days_before=int(body.get("remind_days_before", 0)),
    )

    # 类型专属字段
    if task_type == "yearly":
        kwargs["yearly_month"] = int(body.get("yearly_month", 1))
        kwargs["yearly_day"] = int(body.get("yearly_day", 1))
    elif task_type == "monthly":
        kwargs["monthly_day"] = int(body.get("monthly_day", 1))
    elif task_type == "weekly":
        raw = body.get("weekly_days", [])
        kwargs["weekly_days"] = [int(x) for x in raw]
    elif task_type == "once":
        kwargs["once_date"] = body.get("once_date", "")

    task = _schedule.add_task(**kwargs)
    return ok({"id": task.id, "short_id": task.id[:8], "title": task.title}, "添加成功")


@app.route("/api/schedule/<task_id>", methods=["DELETE"])
def delete_schedule(task_id):
    if _schedule.delete_task(task_id):
        return ok(msg="已删除")
    return err("未找到该任务", 404)


@app.route("/api/schedule/<task_id>/done", methods=["PUT"])
def mark_done(task_id):
    if _schedule.mark_done(task_id):
        return ok(msg="已标记完成")
    return err("未找到该任务", 404)


@app.route("/api/schedule/<task_id>/pending", methods=["PUT"])
def mark_pending(task_id):
    if _schedule.mark_pending(task_id):
        return ok(msg="已重置为待完成")
    return err("未找到该任务", 404)


# ============================================================
#  系统 API
# ============================================================
@app.route("/api/health", methods=["GET"])
def health():
    return ok(registry.health_report())


@app.route("/api/config", methods=["GET"])
def get_config():
    return ok({
        "city": config.get("weather.city", "Beijing"),
        "remind_days_before": config.get("schedule.remind_days_before", 3),
        "app_name": config.get("app.name", "个人工作助理"),
    })


@app.route("/api/config", methods=["PUT"])
def update_config():
    body = request.get_json(silent=True) or {}
    if "city" in body:
        _weather.set_city(body["city"])
    if "remind_days_before" in body:
        config.set("schedule.remind_days_before", int(body["remind_days_before"]))
    config.save()
    return ok(msg="配置已保存")


# ============================================================
#  自动初始化（gunicorn / Cloud Run 部署时模块被直接 import）
# ============================================================
import os as _os
if _os.environ.get("FLASK_ENV") != "development":
    init_services()


# ============================================================
#  启动
# ============================================================
if __name__ == "__main__":
    host = _os.environ.get("HOST", "127.0.0.1")
    port = int(_os.environ.get("PORT", 5001))
    print(f"\n  🚀 个人工作助理已启动")
    print(f"  📡 访问地址: http://{host}:{port}\n")
    app.run(host=host, port=port, debug=False)
