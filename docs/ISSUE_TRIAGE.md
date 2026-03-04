# Issue Triage for Tradebot Repository

## Summary
This document triages the open issues based on the provided task description. Since direct GitHub access is not available, issues are derived from the task's epics and requirements.

## Triaged Issues

### Issue: Quick Housekeeping
- **Severity**: P1
- **Component**: Infra
- **Proposed Fix Summary**: Update .gitignore to exclude common Python artifacts (.venv/, __pycache__/, *.pyc, *.egg-info/, .vscode/, .idea/, logs, build artifacts). Remove any already-committed junk from git tracking. Optionally add CI check to prevent future tracking.
- **Estimated PR Grouping**: Standalone PR for repo hygiene.

### Issue: Split indicators into separate files
- **Severity**: P1
- **Component**: Backend
- **Proposed Fix Summary**: Create finbot/indicators/ directory with one indicator per file. Define consistent interface and export via __init__.py. Add runtime validation. Add unit tests for OHLCV fixtures (output shape, determinism, NaN handling). Maintain backwards compatibility with thin re-export layer.
- **Estimated PR Grouping**: Standalone PR for indicators refactor.

### Epic: Trading Logic & Strategy Engine
- **Severity**: P0
- **Component**: Backend
- **Proposed Fix Summary**: Implement minimal core trading engine with strategy interface (on_bar/on_tick → signals/orders), portfolio bookkeeping (cash/positions/pnl), risk checks (position sizing, max exposure, drawdown, per-symbol limits), execution simulation (order → fill for paper/backtest parity), and structured logging.
- **Estimated PR Grouping**: Core trading engine PR, possibly combined with API if tightly related.

### Epic: API / Backend Services
- **Severity**: P0
- **Component**: Backend
- **Proposed Fix Summary**: Add REST endpoints for placing orders (paper), listing orders/positions, pnl/equity snapshot, health. Add WebSocket for streaming market/order/fill events, system status. Enforce auth and tenant scoping. Add OpenAPI docs in docs/api.md.
- **Estimated PR Grouping**: API layer PR, can be combined with trading engine if endpoints depend on it.

### Epic: Testing, QA & Documentation
- **Severity**: P1
- **Component**: Testing/Docs
- **Proposed Fix Summary**: Add testing pyramid (unit for indicators/risk/fills/pnl, integration for strategy→order→fill→portfolio). Add fixture dataset in tests/fixtures/. Ensure CI runs tests. Update README with setup, test running, sample paper session.
- **Estimated PR Grouping**: Testing and docs PR, can be combined with other backend changes.

### Epic: MVP scope
- **Severity**: P1
- **Component**: Docs
- **Proposed Fix Summary**: Add docs/MVP_SCOPE.md locking 1 asset class, 1 sample strategy, paper-first execution, minimal dashboard/API. Add docs/DEPLOYMENT.md with env vars, staging/prod, rollback.
- **Estimated PR Grouping**: Docs PR.

### Epic: Expansion & Continuous Improvement / Maintenance
- **Severity**: P2
- **Component**: Docs
- **Proposed Fix Summary**: Convert into docs/ROADMAP.md with phased MVP→Beta→Prod. Add operational checklists for logging/metrics, incident response, dependency updates.
- **Estimated PR Grouping**: Roadmap and maintenance docs PR.

## Duplicates
No duplicates detected among the listed issues/epics.

## PR Grouping Recommendations
- Group 1: Quick Housekeeping (standalone)
- Group 2: Indicators refactor (standalone)
- Group 3: Trading Engine + API + Testing (combined, as they are interdependent)
- Group 4: MVP Scope + Deployment + Roadmap docs (combined docs PR)
