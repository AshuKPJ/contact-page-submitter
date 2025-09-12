# app/logging/decorators.py
"""Enhanced logging decorators"""
import asyncio
import functools
import time
from typing import Callable, Any, Optional

from .core import get_logger, campaign_id_var, user_id_var


def log_function(action: str, logger_name: Optional[str] = None):
    """
    Decorator to log function execution with timing and context

    Args:
        action: Description of the action being performed
        logger_name: Optional custom logger name, defaults to function module

    Usage:
        @log_function("create_campaign")
        async def create_campaign(db: Session, current_user: User, ...):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        logger = get_logger(logger_name or fn.__module__)

        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                # Extract context from function arguments
                current_user = kwargs.get("current_user")
                campaign_id = kwargs.get("campaign_id")
                db = kwargs.get("db")

                # Set context variables
                if current_user:
                    user_id_var.set(str(getattr(current_user, "id", "unknown")))
                if campaign_id:
                    campaign_id_var.set(str(campaign_id))

                start_time = time.time()

                # Build safe context for logging (avoid logging sensitive data)
                safe_context = {
                    "event_type": "function_start",
                    "function": fn.__name__,
                    "module": fn.__module__,
                    "action": action,
                }

                # Add safe kwargs (non-sensitive data only)
                for key, value in kwargs.items():
                    if key not in ["password", "token", "secret", "db", "current_user"]:
                        if isinstance(value, (str, int, float, bool)):
                            safe_context[f"param_{key}"] = str(value)[
                                :100
                            ]  # Truncate long strings

                logger.info(f"Function started: {action}", context=safe_context)

                try:
                    result = await fn(*args, **kwargs)

                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(f"{action}_duration", duration_ms)

                    logger.info(
                        f"Function completed: {action}",
                        context={
                            "event_type": "function_success",
                            "function": fn.__name__,
                            "action": action,
                            "duration_ms": duration_ms,
                        },
                    )

                    return result

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000

                    logger.exception(
                        e,
                        handled=False,
                        context={
                            "event_type": "function_error",
                            "function": fn.__name__,
                            "action": action,
                            "duration_ms": duration_ms,
                        },
                    )
                    raise

            return async_wrapper
        else:

            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                # Similar implementation for sync functions
                current_user = kwargs.get("current_user")
                campaign_id = kwargs.get("campaign_id")

                if current_user:
                    user_id_var.set(str(getattr(current_user, "id", "unknown")))
                if campaign_id:
                    campaign_id_var.set(str(campaign_id))

                start_time = time.time()

                # Build safe context for logging
                safe_context = {
                    "event_type": "function_start",
                    "function": fn.__name__,
                    "module": fn.__module__,
                    "action": action,
                }

                for key, value in kwargs.items():
                    if key not in ["password", "token", "secret", "db", "current_user"]:
                        if isinstance(value, (str, int, float, bool)):
                            safe_context[f"param_{key}"] = str(value)[:100]

                logger.info(f"Function started: {action}", context=safe_context)

                try:
                    result = fn(*args, **kwargs)

                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(f"{action}_duration", duration_ms)

                    logger.info(
                        f"Function completed: {action}",
                        context={
                            "event_type": "function_success",
                            "function": fn.__name__,
                            "action": action,
                            "duration_ms": duration_ms,
                        },
                    )

                    return result

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000

                    logger.exception(
                        e,
                        handled=False,
                        context={
                            "event_type": "function_error",
                            "function": fn.__name__,
                            "action": action,
                            "duration_ms": duration_ms,
                        },
                    )
                    raise

            return sync_wrapper

    return decorator


def log_exceptions(action: str, logger_name: Optional[str] = None):
    """
    Decorator to only log exceptions (lighter weight than log_function)

    Args:
        action: Description of the action for context
        logger_name: Optional custom logger name

    Usage:
        @log_exceptions("submit_form")
        async def submit_form(...):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        logger = get_logger(logger_name or fn.__module__)

        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    # Extract context
                    current_user = kwargs.get("current_user")
                    campaign_id = kwargs.get("campaign_id")

                    context = {
                        "event_type": "function_exception",
                        "function": fn.__name__,
                        "module": fn.__module__,
                        "action": action,
                    }

                    if current_user:
                        context["user_id"] = str(getattr(current_user, "id", "unknown"))
                    if campaign_id:
                        context["campaign_id"] = str(campaign_id)

                    logger.exception(e, handled=False, context=context)
                    raise

            return async_wrapper
        else:

            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    # Extract context
                    current_user = kwargs.get("current_user")
                    campaign_id = kwargs.get("campaign_id")

                    context = {
                        "event_type": "function_exception",
                        "function": fn.__name__,
                        "module": fn.__module__,
                        "action": action,
                    }

                    if current_user:
                        context["user_id"] = str(getattr(current_user, "id", "unknown"))
                    if campaign_id:
                        context["campaign_id"] = str(campaign_id)

                    logger.exception(e, handled=False, context=context)
                    raise

            return sync_wrapper

    return decorator


def log_performance(action: str, logger_name: Optional[str] = None):
    """
    Decorator to only log performance metrics (minimal overhead)

    Args:
        action: Description of the action being measured
        logger_name: Optional custom logger name

    Usage:
        @log_performance("database_query")
        def expensive_database_operation():
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        logger = get_logger(logger_name or fn.__module__)

        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await fn(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(f"{action}_duration", duration_ms)
                    return result
                except Exception:
                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(
                        f"{action}_duration", duration_ms, context={"success": False}
                    )
                    raise

            return async_wrapper
        else:

            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = fn(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(f"{action}_duration", duration_ms)
                    return result
                except Exception:
                    duration_ms = (time.time() - start_time) * 1000
                    logger.performance_metric(
                        f"{action}_duration", duration_ms, context={"success": False}
                    )
                    raise

            return sync_wrapper

    return decorator
