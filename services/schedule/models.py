"""
日程数据模型
"""
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional, List
from enum import Enum


class TaskType(str, Enum):
    YEARLY = "yearly"       # 每年（纪念日、节假日）
    MONTHLY = "monthly"     # 每月
    WEEKLY = "weekly"       # 每周
    DAILY = "daily"         # 每日
    ONCE = "once"           # 单次


class TaskStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


@dataclass
class Task:
    id: str
    title: str
    task_type: str          # TaskType value
    status: str = TaskStatus.PENDING.value
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # 每年任务：月份(1-12)和日期(1-31)
    yearly_month: Optional[int] = None
    yearly_day: Optional[int] = None

    # 每月任务：每月第几天（1-31，-1表示最后一天）
    monthly_day: Optional[int] = None

    # 每周任务：星期几列表（0=周一 ... 6=周日）
    weekly_days: List[int] = field(default_factory=list)

    # 每日任务：无需额外字段

    # 单次任务：具体日期
    once_date: Optional[str] = None   # "YYYY-MM-DD"

    # 提前提醒天数（覆盖全局配置）
    remind_days_before: int = 0

    # 创建时间
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
