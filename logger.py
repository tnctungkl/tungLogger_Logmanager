from __future__ import annotations
from database import init_db, insert_log_row, insert_logs_bulk, fetch_logs, reset_log_table
from typing import List, Optional, Sequence, Tuple, Dict, Any
from dataclasses import dataclass, asdict
from uis import get_hostname, utcnow
import logging

log = logging.getLogger("LogManager")

if not log.handlers:
    log.setLevel(logging.INFO)
    _ch = logging.StreamHandler()
    _ch.setFormatter(logging.Formatter("[%(levelname)s] LogManager: %(message)s"))
    log.addHandler(_ch)

VALID_LOG_TYPES = ("INFO", "WARNING", "ERROR", "DEBUG")

@dataclass
class LogRecord:
    id: Optional[int]
    log_type: str
    log_message: str
    hostname: str
    created_at: Any

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LogManager:
    def __init__(self) -> None:
        init_db()

        self.logs: List[LogRecord] = []
        self.hostname = get_hostname()

    def _validate_type(self, log_type: str) -> None:
        if log_type not in VALID_LOG_TYPES:
            raise ValueError(f"Invalid log_type '{log_type}'. "f"Allowed: {', '.join(VALID_LOG_TYPES)}")

    def add_log(self, log_message: str, log_type: str = "INFO") -> Tuple[bool, str, Optional[LogRecord]]:
        try:
            self._validate_type(log_type)
            record = insert_log_row(
                log_type=log_type,
                log_message=log_message,
                hostname=self.hostname,
                created_at=utcnow()
            )
            if not record or "id" not in record:
                msg = "Insert returned no row.."
                log.error(msg)
                return False, msg, None

            log_rec = LogRecord(
                id=record["id"],
                log_type=record["log_type"],
                log_message=record["log_message"],
                hostname=record["hostname"],
                created_at=record["created_at"],
            )
            self.logs.insert(0, log_rec)
            icl_msg = f"Saved log #{log_rec.id} ({log_rec.log_type}) !"
            log.info(icl_msg)
            return True, icl_msg, log_rec
        except Exception as e:
            err = f"Failed to add log: {e} !"
            log.error(err)
            return False, err, None

    def add_logs_bulk(self, items: Sequence[Tuple[str, str]]) -> Tuple[bool, str, int]:
        try:
            for t, _ in items:
                self._validate_type(t)
            loader = [(t, m, self.hostname, utcnow()) for (t, m) in items]
            count = insert_logs_bulk(loader)
            msg = f"Inserted {count} logs!"
            log.info(msg)
            return True, msg, count
        except Exception as e:
            err = f"Bulk insert failed: {e} !"
            log.error(err)
            return False, err, 0

    def refresh_from_db(self, filter_types: Optional[Sequence[str]] = None, limit: int = 500) -> Tuple[bool, str, List[LogRecord]]:
        try:
            if filter_types:
                for t in filter_types:
                    self._validate_type(t)
            rows = fetch_logs(filter_types, limit)
            self.logs = [
                LogRecord(
                    id=r["id"],
                    log_type=r["log_type"],
                    log_message=r["log_message"],
                    hostname=r["hostname"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]
            msg = f"Fetched {len(self.logs)} logs from DB!"
            log.info(msg)
            return True, msg, self.logs
        except Exception as e:
            err = f"Failed to refresh logs: {e} !"
            log.error(err)
            return False, err, []

    def filter_local(self, types: Sequence[str]) -> List[LogRecord]:
        lc_filter = [l for l in self.logs if l.log_type in set(types)]
        return lc_filter

    def to_list_of_dicts(self, source: Optional[List[LogRecord]] = None) -> List[Dict[str, Any]]:
        lsdc_rec = source if source is not None else self.logs
        return [l.to_dict() for l in lsdc_rec]

    def reset_logs(self) -> Tuple[bool, str]:
        try:
            reset_log_table()
            self.logs.clear()
            msg = "Log table and ID counter successfully reset!"
            log.info(msg)
            return True, msg
        except Exception as e:
            err = f"Failed to reset log table: {e} !"
            log.error(err)
            return False, err