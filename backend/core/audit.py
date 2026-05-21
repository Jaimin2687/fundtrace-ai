"""
Audit logging utilities with a decorator interface.
Writes to local log file and optionally enqueues Celery tasks.
"""

import asyncio
import json
from functools import wraps
from datetime import datetime, timezone
from typing import Callable, Any

from .config import get_settings


async def write_audit_trail(user_id: str, action_type: str, payload: dict) -> None:
    settings = get_settings()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action_type": action_type,
        "payload": payload,
    }
    try:
        with open(settings.AUDIT_LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
    except Exception as exc:
        print(f"[Audit] Failed to write audit log: {exc}")


def audit_log(action_type: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            user_id = getattr(user, "id", "unknown")
            payload = {"args": str(args), "kwargs": {k: str(v) for k, v in kwargs.items()}}
            asyncio.create_task(write_audit_trail(user_id, action_type, payload))
            return await func(*args, **kwargs)

        return wrapper

    return decorator
