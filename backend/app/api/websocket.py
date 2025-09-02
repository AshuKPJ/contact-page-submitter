from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, campaign_id: str):
        await websocket.accept()
        self.active_connections[campaign_id] = websocket

    def disconnect(self, campaign_id: str):
        if campaign_id in self.active_connections:
            del self.active_connections[campaign_id]

    async def send_update(self, campaign_id: str, data: dict):
        if campaign_id in self.active_connections:
            await self.active_connections[campaign_id].send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/campaign/{campaign_id}")
async def websocket_endpoint(websocket: WebSocket, campaign_id: str):
    await manager.connect(websocket, campaign_id)

    try:
        while True:
            # Send campaign status every 2 seconds
            db = SessionLocal()
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

            if campaign:
                stats = {
                    "status": campaign.status,
                    "total": campaign.total_urls,
                    "processed": campaign.submitted_count + campaign.failed_count,
                    "successful": campaign.submitted_count,
                    "failed": campaign.failed_count,
                }
                await manager.send_update(campaign_id, stats)

            db.close()
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(campaign_id)
