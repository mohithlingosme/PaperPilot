"""
Lightweight event streamer for broadcasting trading events per tenant.
"""
import asyncio
from typing import Dict, Set, Any
from starlette.websockets import WebSocket


class EventStream:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, tenant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self.lock:
            self.connections.setdefault(tenant_id, set()).add(websocket)

    async def disconnect(self, tenant_id: str, websocket: WebSocket) -> None:
        async with self.lock:
            if tenant_id in self.connections and websocket in self.connections[tenant_id]:
                self.connections[tenant_id].remove(websocket)
                if not self.connections[tenant_id]:
                    del self.connections[tenant_id]

    async def broadcast(self, tenant_id: str, event: Dict[str, Any]) -> None:
        async with self.lock:
            targets = list(self.connections.get(tenant_id, set()))
        stale = []
        for ws in targets:
            try:
                await ws.send_json(event)
            except RuntimeError:
                stale.append(ws)
        if stale:
            async with self.lock:
                for ws in stale:
                    if tenant_id in self.connections and ws in self.connections[tenant_id]:
                        self.connections[tenant_id].remove(ws)
                        if not self.connections[tenant_id]:
                            del self.connections[tenant_id]


# Singleton for module use
stream = EventStream()
