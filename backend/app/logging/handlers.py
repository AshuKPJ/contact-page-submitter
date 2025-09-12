# app/logging/handlers.py
"""Custom logging handlers"""
import asyncio
import queue
import threading
import time
from collections import deque
from typing import Dict, Any, List, Optional, Deque
import logging
from logging.handlers import QueueHandler, QueueListener

from app.core.database import get_db
from app.utils.logs import insert_app_log


class BufferHandler(logging.Handler):
    """In-memory ring buffer for recent logs"""

    def __init__(self, buffer_size: int = 1000, level: int = logging.NOTSET):
        super().__init__(level)
        self.buffer_size = buffer_size
        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=buffer_size)
        self._lock = threading.RLock()

    def emit(self, record: logging.LogRecord):
        try:
            # Convert record to dict
            log_data = {
                "timestamp": time.time(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Add extra fields
            for key, value in record.__dict__.items():
                if not key.startswith("_") and key not in log_data:
                    log_data[key] = value

            with self._lock:
                self._buffer.append(log_data)

        except Exception:
            self.handleError(record)

    def get_recent(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        with self._lock:
            logs = list(self._buffer)
            if limit:
                logs = logs[-limit:]
            return logs

    def get_campaign_logs(
        self, campaign_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get logs for a specific campaign"""
        with self._lock:
            campaign_logs = [
                log for log in self._buffer if log.get("campaign_id") == campaign_id
            ]
            if limit:
                campaign_logs = campaign_logs[-limit:]
            return campaign_logs

    def clear(self):
        """Clear the buffer"""
        with self._lock:
            self._buffer.clear()


class DatabaseHandler(logging.Handler):
    """Async database handler with batching"""

    def __init__(
        self, level: int = logging.NOTSET, batch_size: int = 50, flush_interval: int = 5
    ):
        super().__init__(level)
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Use queue for async processing
        self._queue: queue.Queue = queue.Queue()
        self._listener = None
        self._start_listener()

    def _start_listener(self):
        """Start the queue listener for async processing"""

        def process_logs():
            batch = []
            last_flush = time.time()

            while True:
                try:
                    # Get log with timeout
                    try:
                        record = self._queue.get(timeout=1.0)
                        if record is None:  # Sentinel to stop
                            break
                        batch.append(record)
                    except queue.Empty:
                        pass

                    now = time.time()

                    # Flush if batch is full or time elapsed
                    if len(batch) >= self.batch_size or (
                        batch and now - last_flush >= self.flush_interval
                    ):
                        self._flush_batch(batch)
                        batch.clear()
                        last_flush = now

                except Exception as e:
                    # Log error but don't break the loop
                    print(f"Database handler error: {e}")

        self._listener = threading.Thread(target=process_logs, daemon=True)
        self._listener.start()

    def _flush_batch(self, batch: List[logging.LogRecord]):
        """Flush a batch of log records to database"""
        if not batch:
            return

        try:
            db = next(get_db())

            for record in batch:
                try:
                    # Extract fields from record
                    context = {}
                    for key, value in record.__dict__.items():
                        if not key.startswith("_") and key not in [
                            "name",
                            "msg",
                            "args",
                            "levelname",
                            "levelno",
                        ]:
                            context[key] = value

                    # Insert to database
                    insert_app_log(
                        db,
                        message=record.getMessage(),
                        level=record.levelname,
                        user_id=getattr(record, "user_id", None),
                        campaign_id=getattr(record, "campaign_id", None),
                        organization_id=getattr(record, "organization_id", None),
                        website_id=getattr(record, "website_id", None),
                        context=context,
                        autocommit=False,
                    )
                except Exception as e:
                    print(f"Failed to log record to database: {e}")

            db.commit()

        except Exception as e:
            print(f"Database batch flush failed: {e}")
        finally:
            if "db" in locals():
                db.close()

    def emit(self, record: logging.LogRecord):
        """Queue log record for async processing"""
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            # Drop log if queue is full to prevent blocking
            pass
        except Exception:
            self.handleError(record)

    def close(self):
        """Close the handler and flush remaining logs"""
        # Signal listener to stop
        self._queue.put(None)
        if self._listener:
            self._listener.join(timeout=5.0)
        super().close()


# Global buffer handler instance for easy access
_global_buffer_handler: Optional[BufferHandler] = None


def get_buffer_handler() -> Optional[BufferHandler]:
    """Get the global buffer handler instance"""
    return _global_buffer_handler


def set_buffer_handler(handler: BufferHandler):
    """Set the global buffer handler instance"""
    global _global_buffer_handler
    _global_buffer_handler = handler
