from __future__ import annotations
from datetime import datetime, timezone
import socket

def get_hostname() -> str:
    return socket.gethostname()

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def isoformat(dt: datetime) -> str:
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)