
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import mlflow

from backend.middleware.hardening_middleware import HardeningMiddleware
from backend.mcp.api import router as mcp_router
from backend.mpa.ingestion.api import router as ingestion_router
from backend.mpa.quality.api import router as quality_router
from backend.mpa.ai_proxy.api import router as ai_proxy_router
from backend.mpa.governance.api import router as governance_router
from backend.mpa.ethics.api import router as ethics_router
from backend.mpa.compliance.api import router as compliance_router
from backend.wpa.auto_analysis.api import router as auto_analysis_api
from backend.wpa.auto_ml.api import router as auto_ml_router
from backend.wpa.intelligent_router.api import router as intelligent_router
from backend.wpa.powerbi.routers.powerbi_router import router as powerbi_router
from backend.mpa.dtl.api import router as dtl_router
from backend.mpa.delivery.router import router as delivery_router
from backend.core.auth.api import router as auth_router

def create_app():
    app = FastAPI(title="SADI API", version="1.0")
    app.add_middleware(HardeningMiddleware)
    # Read allowed origins from environment variable, default to localhost for development
    cors_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8080")
    allowed_origins = [origin.strip() for origin in cors_origins_str.split(',')]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    Instrumentator().instrument(app).expose(app)
    mlflow.set_tracking_uri("http://mlflow:5000")

    unified_router = APIRouter(prefix="/unified/v1")
    unified_router.include_router(mcp_router, prefix="/mcp")
    unified_router.include_router(ingestion_router, prefix="/mpa/ingestion")
    unified_router.include_router(quality_router, prefix="/mpa/quality")
    unified_router.include_router(governance_router, prefix="/mpa/governance")
    unified_router.include_router(ethics_router, prefix="/mpa/ethics")
    unified_router.include_router(compliance_router, prefix="/mpa/compliance")
    unified_router.include_router(dtl_router, prefix="/mpa/dtl")
    unified_router.include_router(delivery_router) # The prefix is already in the router
    unified_router.include_router(ai_proxy_router, prefix="/mpa/ai_proxy")
    unified_router.include_router(auto_analysis_api, prefix="/wpa/auto-analysis")
    unified_router.include_router(auto_ml_router, prefix="/wpa/auto-ml", tags=["WPA - AutoML"])
    unified_router.include_router(powerbi_router, prefix="/wpa/powerbi")
    unified_router.include_router(intelligent_router, prefix="/wpa/router")

    app.include_router(unified_router)
    app.include_router(auth_router)

    @app.on_event("startup")
    async def startup_event():
        from backend.core.state_store import get_state_store
        from backend.core.security import initialize_default_admin

        state_store = get_state_store()
        db = state_store.SessionLocal()
        try:
            initialize_default_admin(db)
        finally:
            db.close()

        print("--- Registered Routes ---")
        for route in app.routes:
            if hasattr(route, "methods"):
                print(f"Path: {route.path}, Methods: {list(route.methods)}")
        print("-------------------------")

    return app
