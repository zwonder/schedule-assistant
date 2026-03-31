"""
日程管理微服务
"""
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from core.base_service import BaseService
from core.config_loader import config
from services.schedule.models import Task, TaskType, TaskStatus
from services.schedule.schedule_store import ScheduleStore


WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


class ScheduleService(BaseService):
    """日程管理服务"""

    def __init__(self):
        super().__init__(name="schedule", version="1.0.0")
        data_file = config.get("schedule.data_file", "data/schedule.json")
        self._store = ScheduleStore(data_file)
        self._global_remind_days = config.get("schedule.remind_days_before", 3)

    def start(self) -> bool:
        self._running = True
        print("[ScheduleService] 日程服务已启动")
        return True

    def stop(self) -> bool:
        self._running = False
        print("[ScheduleService] 日程服务已停止")
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "running": self._running,
            "total_tasks": len(self._store.get_all()),
        }

    # ------------------------------------------------------------------ #
    #  任务查询
    # ------------------------------------------------------------------ #

    def get_today_tasks(self, target_date: Optional[date] = None) -> List[Task]:
        """获取指定日期（默认今天）应该出现的任务"""
        d = target_date or date.today()
        result = []
        for task in self._store.get_all():
            if self._is_task_active_on(task, d):
                result.append(task)
        return result

    def get_upcoming_reminders(self, days_ahead: int = 7) -> List[Tuple[date, Task]]:
        """获取未来N天内需要提醒的事项（主要针对yearly/monthly/once）"""
        today = date.today()
        reminders = []
        for task in self._store.get_all():
            for offset in range(days_ahead + 1):
                check_date = today + timedelta(days=offset)
                if self._should_remind_on(task, check_date):
                    reminders.append((check_date, task))
                    break
        reminders.sort(key=lambda x: x[0])
        return reminders

    def _is_task_active_on(self, task: Task, d: date) -> bool:
        """判断任务是否在指定日期应执行"""
        tt = task.task_type
        if tt == TaskType.DAILY.value:
            return True
        elif tt == TaskType.WEEKLY.value:
            return d.weekday() in (task.weekly_days or [])
        elif tt == TaskType.MONTHLY.value:
            if task.monthly_day == -1:
                # 每月最后一天
                next_month = d.replace(day=28) + timedelta(days=4)
                last_day = (next_month - timedelta(days=next_month.day)).day
                return d.day == last_day
            return d.day == task.monthly_day
        elif tt == TaskType.YEARLY.value:
            return d.month == task.yearly_month and d.day == task.yearly_day
        elif tt == TaskType.ONCE.value:
            if task.once_date:
                return str(d) == task.once_date
        return False

    def _should_remind_on(self, task: Task, d: date) -> bool:
        """判断是否需要在日期d提前提醒某任务"""
        remind_days = task.remind_days_before or self._global_remind_days
        if remind_days <= 0:
            return False
        tt = task.task_type
        # 对 yearly/monthly/once 类型计算提前提醒
        for offset in range(1, remind_days + 1):
            future = d + timedelta(days=offset)
            if tt == TaskType.YEARLY.value:
                if future.month == task.yearly_month and future.day == task.yearly_day:
                    return True
            elif tt == TaskType.MONTHLY.value:
                if task.monthly_day and future.day == task.monthly_day:
                    return True
            elif tt == TaskType.ONCE.value:
                if task.once_date and str(future) == task.once_date:
                    return True
        return False

    # ------------------------------------------------------------------ #
    #  报告生成
    # ------------------------------------------------------------------ #

    def get_daily_report(self, target_date: Optional[date] = None) -> str:
        """生成每日日程报告"""
        d = target_date or date.today()
        tasks = self.get_today_tasks(d)
        upcoming = self.get_upcoming_reminders(days_ahead=7)

        lines = []
        lines.append("=" * 50)
        lines.append(f"  📅 日程提醒  {d.strftime('%Y年%m月%d日')} {WEEKDAY_CN[d.weekday()]}")
        lines.append("=" * 50)

        if not tasks and not upcoming:
            lines.append("\n  🎉 今日无待办事项，轻松一天！")
        else:
            if tasks:
                lines.append(f"\n📌 今日待办 ({len(tasks)} 项):")
                for t in tasks:
                    status_icon = "✅" if t.status == TaskStatus.DONE.value else "⬜"
                    tag_str = f" [{', '.join(t.tags)}]" if t.tags else ""
                    lines.append(f"   {status_icon} {t.title}{tag_str}")
                    if t.description:
                        lines.append(f"      📝 {t.description}")

            if upcoming:
                lines.append(f"\n🔔 近期提醒 (7日内):")
                today = date.today()
                for remind_date, t in upcoming:
                    diff = (remind_date - today).days
                    if diff == 0:
                        when = "今天"
                    elif diff == 1:
                        when = "明天"
                    else:
                        when = f"{diff}天后 ({remind_date.strftime('%m/%d')})"
                    lines.append(f"   ⏰ {when} - {t.title}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

    def list_all_tasks(self, task_type: Optional[str] = None) -> str:
        """以可读格式列出所有任务"""
        if task_type:
            tasks = self._store.get_by_type(task_type)
        else:
            tasks = self._store.get_all()

        if not tasks:
            return "暂无日程记录"

        # 按类型分组
        groups: Dict[str, List[Task]] = {}
        for t in tasks:
            groups.setdefault(t.task_type, []).append(t)

        type_labels = {
            "yearly": "📆 每年任务（纪念日/节假日）",
            "monthly": "🗓️  每月任务",
            "weekly": "📋 每周任务",
            "daily": "☀️  每日任务",
            "once": "📍 单次任务",
        }
        lines = ["", "=" * 50, "  所有日程列表", "=" * 50]
        for ttype, label in type_labels.items():
            if ttype in groups:
                lines.append(f"\n{label}")
                for t in groups[ttype]:
                    status_icon = "✅" if t.status == TaskStatus.DONE.value else "⬜"
                    extra = ""
                    if ttype == "yearly":
                        extra = f" (每年 {t.yearly_month}/{t.yearly_day})"
                    elif ttype == "monthly":
                        day = "最后一天" if t.monthly_day == -1 else f"第{t.monthly_day}天"
                        extra = f" (每月{day})"
                    elif ttype == "weekly":
                        days_str = "/".join(WEEKDAY_CN[d] for d in (t.weekly_days or []))
                        extra = f" (每{days_str})"
                    elif ttype == "once":
                        extra = f" ({t.once_date})"
                    tag_str = f" [{', '.join(t.tags)}]" if t.tags else ""
                    lines.append(f"  {status_icon} [{t.id[:8]}] {t.title}{extra}{tag_str}")
                    if t.description:
                        lines.append(f"       {t.description}")
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  CRUD
    # ------------------------------------------------------------------ #

    def add_task(self, **kwargs) -> Task:
        task = Task(id=str(uuid.uuid4()), **kwargs)
        self._store.add(task)
        print(f"[ScheduleService] 已添加任务: {task.title}")
        return task

    def delete_task(self, task_id: str) -> bool:
        # 支持短ID匹配（前8位）
        full_id = self._find_full_id(task_id)
        if full_id and self._store.delete(full_id):
            print(f"[ScheduleService] 已删除任务: {task_id}")
            return True
        print(f"[ScheduleService] 未找到任务: {task_id}")
        return False

    def mark_done(self, task_id: str) -> bool:
        full_id = self._find_full_id(task_id)
        if full_id:
            return self._store.mark_done(full_id)
        return False

    def mark_pending(self, task_id: str) -> bool:
        full_id = self._find_full_id(task_id)
        if full_id:
            return self._store.mark_pending(full_id)
        return False

    def _find_full_id(self, short_or_full_id: str) -> Optional[str]:
        """通过完整ID或前8位短ID查找任务"""
        if short_or_full_id in self._store._tasks:
            return short_or_full_id
        for tid in self._store._tasks:
            if tid.startswith(short_or_full_id):
                return tid
        return None
