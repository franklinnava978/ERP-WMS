from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.modules.tenants.router import router as tenants_router
from src.modules.auth.router import router as auth_router
from src.modules.catalog.router import router as catalog_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers por módulos
app.include_router(tenants_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")  
app.include_router(catalog_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENV,
        "app": settings.PROJECT_NAME
    }