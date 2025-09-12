# app/api/websocket.py - Updated with comprehensive logging
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
    Request,
)
from sqlalchemy.orm import Session
from typing import Dict, Set, Optional, Any
import json
import asyncio
import logging
import time
from datetime import datetime

from app.core.dependencies import get_current_user_ws
from app.core.database import get_db
from app.models.user import User
from app.services.log_service import ApplicationInsightsLogger

router = APIRouter(prefix="/api/ws", tags=["websocket"], redirect_slashes=False)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store connections by campaign_id
        self.campaign_connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by user_id for user-specific updates
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_meta: Dict[WebSocket, Dict[str, Any]] = {}
        # Logger for tracking
        self._db_session = None

    def _get_logger(self):
        """Get a logger instance with database session"""
        if not self._db_session:
            from app.core.database import SessionLocal

            self._db_session = SessionLocal()
        return ApplicationInsightsLogger(self._db_session)

    async def connect(self, websocket: WebSocket, campaign_id: str, user_id: str):
        """Accept a WebSocket connection and register it"""
        await websocket.accept()

        # Add to campaign connections
        if campaign_id not in self.campaign_connections:
            self.campaign_connections[campaign_id] = set()
        self.campaign_connections[campaign_id].add(websocket)

        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        # Store connection metadata
        connected_at = datetime.utcnow()
        self.connection_meta[websocket] = {
            "campaign_id": campaign_id,
            "user_id": user_id,
            "connected_at": connected_at,
        }

        # Log connection
        logger_instance = self._get_logger()
        logger_instance.set_context(
            user_id=user_id,
            campaign_id=campaign_id if campaign_id != "user_channel" else None,
        )

        logger_instance.track_business_event(
            event_name="websocket_connected",
            properties={
                "connection_type": (
                    "campaign" if campaign_id != "user_channel" else "user"
                ),
                "campaign_id": campaign_id,
                "user_id": user_id,
                "total_campaign_connections": len(
                    self.campaign_connections.get(campaign_id, set())
                ),
                "total_user_connections": len(
                    self.user_connections.get(user_id, set())
                ),
            },
        )

        logger_instance.track_metric(
            name="websocket_connections",
            value=len(self.connection_meta),
            properties={"type": "total_active"},
        )

        logger.info(f"WebSocket connected: user={user_id}, campaign={campaign_id}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_meta:
            meta = self.connection_meta[websocket]
            campaign_id = meta.get("campaign_id")
            user_id = meta.get("user_id")
            connected_at = meta.get("connected_at")

            # Calculate connection duration
            if connected_at:
                duration_seconds = (datetime.utcnow() - connected_at).total_seconds()
            else:
                duration_seconds = 0

            # Remove from campaign connections
            if campaign_id and campaign_id in self.campaign_connections:
                self.campaign_connections[campaign_id].discard(websocket)
                if not self.campaign_connections[campaign_id]:
                    del self.campaign_connections[campaign_id]

            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            # Remove metadata
            del self.connection_meta[websocket]

            # Log disconnection
            logger_instance = self._get_logger()
            logger_instance.set_context(
                user_id=user_id,
                campaign_id=campaign_id if campaign_id != "user_channel" else None,
            )

            logger_instance.track_business_event(
                event_name="websocket_disconnected",
                properties={
                    "connection_type": (
                        "campaign" if campaign_id != "user_channel" else "user"
                    ),
                    "campaign_id": campaign_id,
                    "user_id": user_id,
                },
                metrics={
                    "connection_duration_seconds": duration_seconds,
                    "remaining_connections": len(self.connection_meta),
                },
            )

            logger_instance.track_metric(
                name="websocket_connection_duration",
                value=duration_seconds,
                properties={"user_id": user_id, "campaign_id": campaign_id},
            )

            logger.info(
                f"WebSocket disconnected: user={user_id}, campaign={campaign_id}, duration={duration_seconds}s"
            )

    async def send_to_campaign(self, message: str, campaign_id: str):
        """Send a message to all connections for a specific campaign"""
        if campaign_id in self.campaign_connections:
            disconnected = set()
            send_start = time.time()
            success_count = 0

            for connection in self.campaign_connections[campaign_id].copy():
                try:
                    await connection.send_text(message)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send message to connection: {e}")
                    disconnected.add(connection)

            send_time = (time.time() - send_start) * 1000

            # Log broadcast metrics
            logger_instance = self._get_logger()
            logger_instance.track_business_event(
                event_name="websocket_broadcast_campaign",
                properties={
                    "campaign_id": campaign_id,
                    "target_connections": len(self.campaign_connections[campaign_id]),
                    "successful_sends": success_count,
                    "failed_sends": len(disconnected),
                },
                metrics={
                    "broadcast_time_ms": send_time,
                    "message_size_bytes": len(message),
                },
            )

            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)

    async def send_to_user(self, message: str, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.user_connections:
            disconnected = set()
            send_start = time.time()
            success_count = 0

            for connection in self.user_connections[user_id].copy():
                try:
                    await connection.send_text(message)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send message to connection: {e}")
                    disconnected.add(connection)

            send_time = (time.time() - send_start) * 1000

            # Log broadcast metrics
            logger_instance = self._get_logger()
            logger_instance.track_business_event(
                event_name="websocket_broadcast_user",
                properties={
                    "user_id": user_id,
                    "target_connections": len(self.user_connections[user_id]),
                    "successful_sends": success_count,
                    "failed_sends": len(disconnected),
                },
                metrics={
                    "broadcast_time_ms": send_time,
                    "message_size_bytes": len(message),
                },
            )

            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)

    async def broadcast_to_campaign(self, data: dict, campaign_id: str):
        """Broadcast structured data to all connections for a campaign"""
        message = json.dumps(data)
        await self.send_to_campaign(message, campaign_id)

    async def broadcast_to_user(self, data: dict, user_id: str):
        """Broadcast structured data to all connections for a user"""
        message = json.dumps(data)
        await self.send_to_user(message, user_id)

    def get_campaign_connection_count(self, campaign_id: str) -> int:
        """Get the number of active connections for a campaign"""
        return len(self.campaign_connections.get(campaign_id, set()))

    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user"""
        return len(self.user_connections.get(user_id, set()))

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        stats = {
            "total_connections": len(self.connection_meta),
            "campaigns_with_connections": len(self.campaign_connections),
            "users_with_connections": len(self.user_connections),
            "campaign_connections": {
                campaign_id: len(connections)
                for campaign_id, connections in self.campaign_connections.items()
            },
            "user_connections": {
                user_id: len(connections)
                for user_id, connections in self.user_connections.items()
            },
        }

        # Log stats retrieval
        logger_instance = self._get_logger()
        logger_instance.track_metric(
            name="websocket_stats_retrieved",
            value=stats["total_connections"],
            properties=stats,
        )

        return stats


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/campaign/{campaign_id}")
async def websocket_campaign_endpoint(websocket: WebSocket, campaign_id: str):
    """WebSocket endpoint for real-time campaign updates"""
    db = next(get_db())
    logger_instance = ApplicationInsightsLogger(db)
    user_id = "anonymous"
    connection_start = time.time()
    messages_received = 0
    messages_sent = 0

    try:
        # Connect and track
        await manager.connect(websocket, campaign_id, user_id)

        logger_instance.track_user_action(
            action="websocket_campaign_connect",
            target="campaign_websocket",
            properties={"campaign_id": campaign_id},
        )

        # Send welcome message
        welcome_msg = json.dumps(
            {
                "type": "connection",
                "status": "connected",
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to campaign updates",
            }
        )
        await websocket.send_text(welcome_msg)
        messages_sent += 1

        while True:
            try:
                # Receive messages from client
                msg_start = time.time()
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                msg_receive_time = (time.time() - msg_start) * 1000
                messages_received += 1

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": "Invalid JSON format"})
                    )
                    messages_sent += 1
                    continue

                # Track message type
                message_type = message.get("type")
                logger_instance.track_user_action(
                    action=f"websocket_message_{message_type}",
                    target="campaign_websocket",
                    properties={
                        "campaign_id": campaign_id,
                        "user_id": user_id,
                        "message_type": message_type,
                    },
                )

                logger_instance.track_metric(
                    name="websocket_message_latency",
                    value=msg_receive_time,
                    properties={"message_type": message_type},
                )

                # Handle different message types
                if message_type == "ping":
                    await websocket.send_text(
                        json.dumps(
                            {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                        )
                    )
                    messages_sent += 1

                elif message_type == "auth":
                    # Handle authentication
                    new_user_id = message.get("user_id")
                    if new_user_id:
                        user_id = new_user_id
                        manager.connection_meta[websocket]["user_id"] = user_id
                        logger_instance.set_context(user_id=user_id)

                        await websocket.send_text(
                            json.dumps({"type": "auth_success", "user_id": user_id})
                        )
                        messages_sent += 1

                        logger_instance.track_authentication(
                            action="websocket_auth",
                            email="",  # Would need to lookup from user_id
                            success=True,
                            ip_address="websocket",
                        )

                elif message_type == "subscribe":
                    # Handle subscription to specific events
                    events = message.get("events", [])
                    await websocket.send_text(
                        json.dumps({"type": "subscribed", "events": events})
                    )
                    messages_sent += 1

                    logger_instance.track_business_event(
                        event_name="websocket_subscribe",
                        properties={"campaign_id": campaign_id, "events": events},
                    )

                else:
                    # Echo unknown messages
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "echo",
                                "original": message,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )
                    messages_sent += 1

            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "keepalive",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                )
                messages_sent += 1

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for campaign {campaign_id}")
    except Exception as e:
        logger_instance.track_exception(
            e, handled=True, properties={"campaign_id": campaign_id, "user_id": user_id}
        )
        logger.error(f"WebSocket error for campaign {campaign_id}: {e}")
    finally:
        connection_duration = time.time() - connection_start

        # Track session metrics
        logger_instance.track_business_event(
            event_name="websocket_session_ended",
            properties={"campaign_id": campaign_id, "user_id": user_id},
            metrics={
                "session_duration_seconds": connection_duration,
                "messages_received": messages_received,
                "messages_sent": messages_sent,
                "avg_messages_per_minute": (
                    (messages_received + messages_sent) / (connection_duration / 60)
                    if connection_duration > 0
                    else 0
                ),
            },
        )

        manager.disconnect(websocket)
        db.close()


@router.websocket("/user/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for user-specific updates"""
    db = next(get_db())
    logger_instance = ApplicationInsightsLogger(db)
    logger_instance.set_context(user_id=user_id)
    connection_start = time.time()
    messages_received = 0
    messages_sent = 0

    try:
        await manager.connect(websocket, "user_channel", user_id)

        logger_instance.track_user_action(
            action="websocket_user_connect",
            target="user_websocket",
            properties={"user_id": user_id},
        )

        # Send welcome message
        welcome_msg = json.dumps(
            {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to user updates",
            }
        )
        await websocket.send_text(welcome_msg)
        messages_sent += 1

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                messages_received += 1

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    continue

                # Track message
                message_type = message.get("type")
                logger_instance.track_user_action(
                    action=f"websocket_user_message_{message_type}",
                    target="user_websocket",
                    properties={"user_id": user_id, "message_type": message_type},
                )

                # Handle ping/pong
                if message_type == "ping":
                    await websocket.send_text(
                        json.dumps(
                            {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                        )
                    )
                    messages_sent += 1
                else:
                    # Echo other messages
                    await websocket.send_text(
                        json.dumps({"type": "echo", "data": message})
                    )
                    messages_sent += 1

            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "keepalive",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                )
                messages_sent += 1

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger_instance.track_exception(e, handled=True)
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        connection_duration = time.time() - connection_start

        logger_instance.track_business_event(
            event_name="websocket_user_session_ended",
            properties={"user_id": user_id},
            metrics={
                "session_duration_seconds": connection_duration,
                "messages_received": messages_received,
                "messages_sent": messages_sent,
            },
        )

        manager.disconnect(websocket)
        db.close()


@router.get("/stats")
async def get_websocket_stats(request: Request, db: Session = Depends(get_db)):
    """Get WebSocket connection statistics"""
    logger_instance = ApplicationInsightsLogger(db)

    logger_instance.track_user_action(
        action="view_websocket_stats",
        target="websocket_stats",
        properties={"ip": request.client.host if request.client else "unknown"},
    )

    stats = manager.get_stats()

    logger_instance.track_business_event(
        event_name="websocket_stats_retrieved", properties=stats
    )

    return stats


@router.post("/broadcast/campaign/{campaign_id}")
async def broadcast_to_campaign(
    campaign_id: str, message: dict, db: Session = Depends(get_db)
):
    """Broadcast a message to all connections for a campaign (admin endpoint)"""
    logger_instance = ApplicationInsightsLogger(db)

    broadcast_start = time.time()
    connection_count = manager.get_campaign_connection_count(campaign_id)

    await manager.broadcast_to_campaign(
        {
            "type": "broadcast",
            "campaign_id": campaign_id,
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        },
        campaign_id,
    )

    broadcast_time = (time.time() - broadcast_start) * 1000

    logger_instance.track_business_event(
        event_name="websocket_broadcast_sent",
        properties={"campaign_id": campaign_id, "target_type": "campaign"},
        metrics={
            "broadcast_time_ms": broadcast_time,
            "target_connections": connection_count,
            "message_size_bytes": len(json.dumps(message)),
        },
    )

    return {
        "success": True,
        "message": f"Broadcasted to {connection_count} connections",
    }


@router.post("/broadcast/user/{user_id}")
async def broadcast_to_user(user_id: str, message: dict, db: Session = Depends(get_db)):
    """Broadcast a message to all connections for a user (admin endpoint)"""
    logger_instance = ApplicationInsightsLogger(db)
    logger_instance.set_context(user_id=user_id)

    broadcast_start = time.time()
    connection_count = manager.get_user_connection_count(user_id)

    await manager.broadcast_to_user(
        {
            "type": "broadcast",
            "user_id": user_id,
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        },
        user_id,
    )

    broadcast_time = (time.time() - broadcast_start) * 1000

    logger_instance.track_business_event(
        event_name="websocket_broadcast_sent",
        properties={"user_id": user_id, "target_type": "user"},
        metrics={
            "broadcast_time_ms": broadcast_time,
            "target_connections": connection_count,
            "message_size_bytes": len(json.dumps(message)),
        },
    )

    return {
        "success": True,
        "message": f"Broadcasted to {connection_count} connections",
    }


# Helper functions for sending updates from other parts of the application
async def send_campaign_update(campaign_id: str, update_type: str, data: dict):
    """Helper function to send campaign updates from other parts of the application"""
    await manager.broadcast_to_campaign(
        {
            "type": "campaign_update",
            "update_type": update_type,
            "campaign_id": campaign_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        },
        campaign_id,
    )


async def send_user_notification(user_id: str, notification_type: str, data: dict):
    """Helper function to send user notifications from other parts of the application"""
    await manager.broadcast_to_user(
        {
            "type": "notification",
            "notification_type": notification_type,
            "user_id": user_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        },
        user_id,
    )
