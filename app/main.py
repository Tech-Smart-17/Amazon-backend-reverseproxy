"""
Main FastAPI Application Entrypoint for Amazon Backend System.
"""
from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import engine, Base, init_redis
from app.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.middleware import CustomHeaderAndLoggingMiddleware, RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("amazon_backend")

# Import all routers
from app.routers import (
    auth_router, users_router, products_router, categories_router,
    search_router, inventory_router, warehouse_router, cart_router,
    wishlist_router, address_router, orders_router, payments_router,
    invoices_router, notifications_router, recommendations_router,
    analytics_router, admin_router, ai_router, voice_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan setup: DB migrations & background tasks."""
    logger.info("Initializing Amazon Backend System DB schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize async services
    await init_redis()
    
    logger.info("Amazon Backend System startup complete.")
    yield
    logger.info("Shutting down Amazon Backend System...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Amazon-style e-commerce API with FastAPI, SQLAlchemy, MongoDB, Redis, ChromaDB, and optional LangChain search, RAG, SQL, and voice assistants.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(CustomHeaderAndLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)

# Register Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Mount Static Uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Include API Routers under /api/v1/
prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=prefix)
app.include_router(users_router, prefix=prefix)
app.include_router(products_router, prefix=prefix)
app.include_router(categories_router, prefix=prefix)
app.include_router(search_router, prefix=prefix)
app.include_router(inventory_router, prefix=prefix)
app.include_router(warehouse_router, prefix=prefix)
app.include_router(cart_router, prefix=prefix)
app.include_router(wishlist_router, prefix=prefix)
app.include_router(address_router, prefix=prefix)
app.include_router(orders_router, prefix=prefix)
app.include_router(payments_router, prefix=prefix)
app.include_router(invoices_router, prefix=prefix)
app.include_router(notifications_router, prefix=prefix)
app.include_router(recommendations_router, prefix=prefix)
app.include_router(analytics_router, prefix=prefix)
app.include_router(admin_router, prefix=prefix)
app.include_router(ai_router, prefix=prefix)
app.include_router(voice_router, prefix=prefix)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root endpoint to Swagger UI."""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
