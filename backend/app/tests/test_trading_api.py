import os
import time

import pytest
from fastapi.testclient import TestClient

os.environ["PAPERPILOT_API_KEY"] = "test-key"

from backend.app.main import app  # noqa: E402

client = TestClient(app)


def _headers():
    return {"X-API-Key": "test-key", "X-Tenant-Id": "tenant-1"}


def _bar(symbol: str, price: float):
    return {
        "symbol": symbol,
        "open": price,
        "high": price,
        "low": price,
        "close": price,
        "volume": 1000,
        "timestamp": time.time(),
    }


def test_health_endpoint():
    resp = client.get("/api/v1/trading/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_auth_enforced():
    resp = client.get("/api/v1/trading/portfolio")
    # Missing headers triggers validation error
    assert resp.status_code in (401, 422)

    resp = client.get("/api/v1/trading/portfolio", headers={"X-API-Key": "bad", "X-Tenant-Id": "t1"})
    assert resp.status_code == 401


def test_full_bar_to_fill_flow():
    # Reset engine
    reset = client.post("/api/v1/trading/engine/initialize", headers=_headers(), params={"initial_cash": 50000})
    assert reset.status_code == 200

    # Send bars to trigger demo momentum strategy BUY
    prices = [100, 101, 102]
    for p in prices:
        resp = client.post("/api/v1/trading/market/bar", headers=_headers(), json=_bar("AAPL", p))
        assert resp.status_code == 200

    orders = client.get("/api/v1/trading/orders", headers=_headers())
    assert orders.status_code == 200
    body = orders.json()
    assert len(body) >= 1

    fills = client.get("/api/v1/trading/fills", headers=_headers())
    assert fills.status_code == 200
    assert len(fills.json()) >= 1

    portfolio = client.get("/api/v1/trading/portfolio", headers=_headers())
    assert portfolio.status_code == 200
    data = portfolio.json()
    assert data["equity"] > 0

    pnl = client.get("/api/v1/trading/pnl", headers=_headers())
    assert pnl.status_code == 200
    assert "total_pnl" in pnl.json()


def test_websocket_stream_receives_event():
    with client.websocket_connect("/api/v1/trading/ws", headers=_headers()) as websocket:
        # Send a bar to create an event
        client.post("/api/v1/trading/market/bar", headers=_headers(), json=_bar("MSFT", 200))
        message = websocket.receive_json()
        assert "type" in message
