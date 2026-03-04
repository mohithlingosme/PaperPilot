import os
import structlog
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .observability import init_observability, http_requests_total, http_request_duration, db_query_duration
from .api.routes import trading_router

logger = structlog.get_logger()

# Database setup (best-effort; skip if models are incomplete)
engine = None
SessionLocal = None
try:
    from .models import Base

    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # pragma: no cover - defensive path
    logger.warning("Database initialization skipped", error=str(exc))
    Base = None


app = FastAPI(title="PaperPilot API", version="1.0.0")

# Initialize observability
init_observability(app, "api")

# Routers
app.include_router(trading_router)

logger = structlog.get_logger()

@app.on_event("startup")
async def startup_event():
    logger.info("API starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API shutting down")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return {"message": "Welcome to PaperPilot API"}

@app.get("/api/v1/projects")
async def get_projects():
    """Get user projects"""
    with http_request_duration.labels(method="GET", endpoint="/api/v1/projects").time():
        try:
            # Simulate DB query
            with db_query_duration.labels(operation="select").time():
                # In real app, query projects from DB
                projects = [{"id": 1, "name": "Sample Project"}]

            http_requests_total.labels(method="GET", endpoint="/api/v1/projects", status_code="200").inc()
            logger.info("Retrieved projects", count=len(projects))
            return {"projects": projects}
        except Exception as e:
            http_requests_total.labels(method="GET", endpoint="/api/v1/projects", status_code="500").inc()
            logger.error("Failed to get projects", error=str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/projects")
async def create_project(name: str):
    """Create a new project"""
    with http_request_duration.labels(method="POST", endpoint="/api/v1/projects").time():
        try:
            # Simulate DB insert
            with db_query_duration.labels(operation="insert").time():
                # In real app, insert into DB
                project = {"id": 2, "name": name}

            http_requests_total.labels(method="POST", endpoint="/api/v1/projects", status_code="201").inc()
            logger.info("Created project", project_id=project["id"], name=name)
            return project
        except Exception as e:
            http_requests_total.labels(method="POST", endpoint="/api/v1/projects", status_code="500").inc()
            logger.error("Failed to create project", error=str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
