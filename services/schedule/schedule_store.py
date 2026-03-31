"""
日程数据持久化（JSON文件）
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from services.schedule.models import Task, TaskStatus


class ScheduleStore:
    """日程数据存储（基于本地JSON文件）"""

    def __init__(self, data_file: str = "data/schedule.json"):
        self._data_file = data_file
        self._tasks: Dict[str, Task] = {}
        # 确保数据目录存在
        os.makedirs(os.path.dirname(os.path.abspath(data_file)), exist_ok=True)
        self._load()

    def _load(self):
        abs_path = os.path.abspath(self._data_file)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for item in raw.get("tasks", []):
                t = Task.from_dict(item)
                self._tasks[t.id] = t
            print(f"[ScheduleStore] 加载 {len(self._tasks)} 条日程")
        else:
            print("[ScheduleStore] 日程数据文件不存在，将新建")
            self._seed_defaults()
            self._save()

    def _save(self):
        abs_path = os.path.abspath(self._data_file)
        data = {"tasks": [t.to_dict() for t in self._tasks.values()]}
        with open(abs_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _seed_defaults(self):
        """预置一些示例日程"""
        defaults = [
            Task(
                id=str(uuid.uuid4()),
                title="元旦",
                task_type="yearly",
                yearly_month=1, yearly_day=1,
                tags=["节假日"],
                description="元旦假期",
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="春节",
                task_type="yearly",
                yearly_month=1, yearly_day=29,
                tags=["节假日"],
                description="春节，农历新年（示例）",
                remind_days_before=7,
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="劳动节",
                task_type="yearly",
                yearly_month=5, yearly_day=1,
                tags=["节假日"],
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="国庆节",
                task_type="yearly",
                yearly_month=10, yearly_day=1,
                tags=["节假日"],
                remind_days_before=3,
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="还房贷",
                task_type="monthly",
                monthly_day=25,
                tags=["财务"],
                description="每月25日还房贷，提前确认账户余额",
                remind_days_before=2,
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="提交周工作记录",
                task_type="weekly",
                weekly_days=[4],  # 周五
                tags=["工作"],
                description="每周五提交本周工作记录",
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="喝足量的水",
                task_type="daily",
                tags=["健康"],
                description="每天至少喝8杯水",
                created_at=datetime.now().isoformat(),
            ),
            Task(
                id=str(uuid.uuid4()),
                title="晨间计划",
                task_type="daily",
                tags=["习惯"],
                description="每日早上整理今日待办事项",
                created_at=datetime.now().isoformat(),
            ),
        ]
        for t in defaults:
            self._tasks[t.id] = t

    # ------------------------------------------------------------------ #
    #  CRUD
    # ------------------------------------------------------------------ #

    def add(self, task: Task) -> Task:
        if not task.id:
            task.id = str(uuid.uuid4())
        if not task.created_at:
            task.created_at = datetime.now().isoformat()
        self._tasks[task.id] = task
        self._save()
        return task

    def update(self, task: Task) -> bool:
        if task.id not in self._tasks:
            return False
        self._tasks[task.id] = task
        self._save()
        return True

    def delete(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save()
            return True
        return False

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        return list(self._tasks.values())

    def get_by_type(self, task_type: str) -> List[Task]:
        return [t for t in self._tasks.values() if t.task_type == task_type]

    def mark_done(self, task_id: str) -> bool:
        t = self._tasks.get(task_id)
        if t:
            t.status = TaskStatus.DONE.value
            self._save()
            return True
        return False

    def mark_pending(self, task_id: str) -> bool:
        t = self._tasks.get(task_id)
        if t:
            t.status = TaskStatus.PENDING.value
            self._save()
            return True
        return False
