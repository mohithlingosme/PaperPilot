"""
Trading API Routes

REST and WebSocket endpoints for orders, positions, P&L, and streaming events.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

from finbot.engine import TradingEngine
from finbot.portfolio import Portfolio
from finbot.risk import RiskManager
from finbot.strategy import Strategy, Order as TradingOrder

from ..deps import AuthContext, get_auth_context
from ...services.event_stream import stream as event_stream

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

# In-memory storage for demo (in production, use database)
_trading_engine: Optional[TradingEngine] = None


# ============ Schemas ============

class OrderRequest(BaseModel):
    """Request model for creating an order."""
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, description="Limit price (None for market)")
    order_type: str = Field("MARKET", description="MARKET or LIMIT")


class OrderResponse(BaseModel):
    """Response model for an order."""
    id: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float]
    order_type: str
    status: str
    filled_quantity: float
    remaining_quantity: float
    created_at: float


class PositionResponse(BaseModel):
    """Response model for a position."""
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float


class PortfolioSummary(BaseModel):
    """Response model for portfolio summary."""
    cash: float
    equity: float
    total_pnl: float
    positions_count: int
    positions: List[PositionResponse]


class FillResponse(BaseModel):
    """Response model for a fill."""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: float
    commission: float


class RiskStatusResponse(BaseModel):
    """Response model for risk status."""
    trading_paused: bool
    initial_equity: float
    current_equity: float
    drawdown_pct: float
    exposure_pct: float
    cash_reserve_pct: float


class BarRequest(BaseModel):
    """Request model for processing a bar."""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: Optional[float] = None


class PnLResponse(BaseModel):
    """Response model for P&L breakdown."""
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float


# ============ Demo Strategy ============

class DemoStrategy(Strategy):
    """Demo strategy that generates signals based on simple logic."""
    
    def __init__(self):
        super().__init__("DemoStrategy")
        self.price_history: Dict[str, List[float]] = {}
        
    def on_bar(self, bar: Dict[str, Any]) -> Optional[TradingOrder]:
        """Generate trading signals based on price movement."""
        symbol = bar.get('symbol')
        close = bar.get('close')
        
        if not symbol or not close:
            return None
            
        # Initialize price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            
        self.price_history[symbol].append(close)
        
        # Keep only last 5 prices
        if len(self.price_history[symbol]) > 5:
            self.price_history[symbol] = self.price_history[symbol][-5:]
            
        # Simple momentum strategy
        if len(self.price_history[symbol]) >= 3:
            prices = self.price_history[symbol]
            # Buy if price is going up
            if prices[-1] > prices[-2] > prices[-3]:
                return TradingOrder(
                    symbol=symbol,
                    side="BUY",
                    quantity=10,
                    order_type="MARKET"
                )
            # Sell if price is going down
            elif prices[-1] < prices[-2] < prices[-3]:
                return TradingOrder(
                    symbol=symbol,
                    side="SELL",
                    quantity=10,
                    order_type="MARKET"
                )
                
        return None


# ============ Dependencies ============

def get_trading_engine() -> TradingEngine:
    """Get or create the trading engine instance."""
    global _trading_engine
    
    if _trading_engine is None:
        # Create new trading engine
        portfolio = Portfolio(initial_cash=100000.0)
        risk_manager = RiskManager()
        strategy = DemoStrategy()
        
        _trading_engine = TradingEngine(
            strategy=strategy,
            portfolio=portfolio,
            risk_manager=risk_manager
        )

        logger.info("Trading engine initialized")

    return _trading_engine


# ============ Routes ============

@router.get("/health")
async def trading_health():
    """Health check for trading service."""
    return {
        "status": "healthy",
        "service": "trading",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/engine/initialize")
async def initialize_engine(
    initial_cash: float = 100000.0,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Initialize or reset the trading engine."""
    global _trading_engine
    
    portfolio = Portfolio(initial_cash=initial_cash)
    risk_manager = RiskManager()
    strategy = DemoStrategy()
    
    _trading_engine = TradingEngine(
        strategy=strategy,
        portfolio=portfolio,
        risk_manager=risk_manager
    )
    
    result = {
        "status": "initialized",
        "initial_cash": initial_cash,
        "message": "Trading engine reset successfully"
    }

    await event_stream.broadcast(auth.tenant_id, {"type": "engine.reset", "initial_cash": initial_cash})
    return result


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_req: OrderRequest,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Create a new trading order."""
    try:
        # Submit order to execution engine
        order_id = engine.execution_engine.submit_order(
            symbol=order_req.symbol,
            side=order_req.side,
            quantity=order_req.quantity,
            price=order_req.price,
            order_type=order_req.order_type
        )
        
        if order_id is None:
            raise HTTPException(status_code=400, detail="Order rejected by risk manager")
        
        # Get order details
        order = engine.execution_engine.get_order_status(order_id)
        
        if order is None:
            raise HTTPException(status_code=500, detail="Order not found after submission")
            
        response = OrderResponse(
            id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            order_type=order.order_type,
            status=order.status.value,
            filled_quantity=order.filled_quantity,
            remaining_quantity=order.remaining_quantity,
            created_at=order.created_at
        )
        await event_stream.broadcast(auth.tenant_id, {"type": "order.created", "order": response.dict()})
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get all orders, optionally filtered by status."""
    orders = engine.execution_engine.get_all_orders()
    
    if status:
        orders = [o for o in orders if o.status.value == status]
    
    return [
        OrderResponse(
            id=o.id,
            symbol=o.symbol,
            side=o.side,
            quantity=o.quantity,
            price=o.price,
            order_type=o.order_type,
            status=o.status.value,
            filled_quantity=o.filled_quantity,
            remaining_quantity=o.remaining_quantity,
            created_at=o.created_at
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get a specific order by ID."""
    order = engine.execution_engine.get_order_status(order_id)
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse(
        id=order.id,
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price,
        order_type=order.order_type,
        status=order.status.value,
        filled_quantity=order.filled_quantity,
        remaining_quantity=order.remaining_quantity,
        created_at=order.created_at
    )


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Cancel a pending order."""
    success = engine.execution_engine.cancel_order(order_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Order not found or already completed")
    
    response = {"status": "cancelled", "order_id": order_id}
    await event_stream.broadcast(auth.tenant_id, {"type": "order.cancelled", "order_id": order_id})
    return response


@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio(
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get current portfolio summary."""
    portfolio = engine.portfolio
    
    positions = [
        PositionResponse(
            symbol=pos.symbol,
            quantity=pos.quantity,
            avg_entry_price=pos.avg_entry_price,
            current_price=pos.current_price,
            unrealized_pnl=pos.unrealized_pnl,
            realized_pnl=pos.realized_pnl
        )
        for pos in portfolio.positions.values()
    ]
    
    return PortfolioSummary(
        cash=portfolio.cash,
        equity=portfolio.equity,
        total_pnl=portfolio.total_pnl,
        positions_count=len(portfolio.positions),
        positions=positions
    )


@router.get("/positions/{symbol}", response_model=PositionResponse)
async def get_position(
    symbol: str,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get a specific position by symbol."""
    position = engine.portfolio.get_position(symbol)
    
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return PositionResponse(
        symbol=position.symbol,
        quantity=position.quantity,
        avg_entry_price=position.avg_entry_price,
        current_price=position.current_price,
        unrealized_pnl=position.unrealized_pnl,
        realized_pnl=position.realized_pnl
    )


@router.get("/fills", response_model=List[FillResponse])
async def get_fills(
    order_id: Optional[str] = None,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get fills, optionally filtered by order ID."""
    fills = engine.execution_engine.get_fills(order_id)
    
    return [
        FillResponse(
            order_id=f.order_id,
            symbol=f.symbol,
            side=f.side,
            quantity=f.quantity,
            price=f.price,
            timestamp=f.timestamp,
            commission=f.commission
        )
        for f in fills
    ]


@router.get("/risk/status", response_model=RiskStatusResponse)
async def get_risk_status(
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get current risk status."""
    risk_status = engine.risk_manager.get_risk_status(engine.portfolio)
    
    return RiskStatusResponse(
        trading_paused=risk_status['trading_paused'],
        initial_equity=risk_status['initial_equity'],
        current_equity=risk_status['current_equity'],
        drawdown_pct=risk_status['drawdown_pct'],
        exposure_pct=risk_status['exposure_pct'],
        cash_reserve_pct=risk_status['cash_reserve_pct']
    )


@router.post("/risk/resume")
async def resume_trading(
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Resume trading after risk pause."""
    engine.risk_manager.resume_trading()
    await event_stream.broadcast(auth.tenant_id, {"type": "risk.resumed"})
    return {"status": "resumed", "message": "Trading resumed"}


@router.post("/market/bar")
async def process_bar(
    bar: BarRequest,
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Process a market bar and generate orders."""
    bar_data = {
        'symbol': bar.symbol,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': bar.volume,
        'timestamp': bar.timestamp or time.time()
    }
    
    # Process bar through trading engine
    fills = engine.process_bar(bar_data)

    # Broadcast fills/events
    for fill in fills:
        await event_stream.broadcast(auth.tenant_id, {
            "type": "fill",
            "fill": {
                "order_id": fill.order_id,
                "symbol": fill.symbol,
                "side": fill.side,
                "quantity": fill.quantity,
                "price": fill.price,
                "timestamp": fill.timestamp
            }
        })

    summary = engine.get_portfolio_summary()
    await event_stream.broadcast(auth.tenant_id, {"type": "portfolio.updated", "summary": summary})

    return {
        "status": "processed",
        "bar": bar_data,
        "fills_count": len(fills),
        "portfolio": summary
    }


@router.get("/summary")
async def get_summary(
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Get full trading summary."""
    return engine.get_portfolio_summary()


@router.get("/pnl", response_model=PnLResponse)
async def get_pnl(
    engine: TradingEngine = Depends(get_trading_engine),
    auth: AuthContext = Depends(get_auth_context)
):
    """Return realized and unrealized P&L breakdown."""
    realized = sum(p.realized_pnl for p in engine.portfolio.positions.values())
    unrealized = sum(p.unrealized_pnl for p in engine.portfolio.positions.values())
    total = realized + unrealized
    return PnLResponse(total_pnl=total, realized_pnl=realized, unrealized_pnl=unrealized)


@router.websocket("/ws")
async def trading_stream(websocket: WebSocket):
    """WebSocket stream for real-time trading events."""
    api_key = websocket.headers.get("X-API-Key")
    tenant = websocket.headers.get("X-Tenant-Id")

    # Basic header validation (mirrors REST dependency)
    if not tenant:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    expected_env = None
    try:
        import os
        expected_env = os.getenv("PAPERPILOT_API_KEY")
    except Exception:
        expected_env = None

    if expected_env and api_key != expected_env:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await event_stream.connect(tenant, websocket)
    try:
        while True:
            # Keep alive; we expect client to just listen
            await websocket.receive_text()
    except WebSocketDisconnect:
        await event_stream.disconnect(tenant, websocket)
